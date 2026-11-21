"""WebSocket bridge to Godot editor plugin.

Two ways to reach the editor (JSON-RPC 2.0 over WebSocket either way):

- Connection-file mode (fork addition, preferred): the plugin listens on a port
  the OS picks and writes <project>/.godot/mcp_connection.json; we find our
  project, read the file and connect to that editor as a CLIENT. Works when the
  OS reserves the fixed ports, and each server only reaches its own project.
  See connection_file.py and memory-bank/systemPatterns.md.
- Fixed ports (upstream): we act as a WebSocket SERVER on ports 6505-6514 and
  every editor connects to us. Used when the project is not known at startup
  (GODOT_MCP_FIXED_PORTS=auto) and for plugins without connection-file support.
"""

import asyncio
import inspect
import json
import logging
import os
from pathlib import Path
from typing import Any

import websockets
from websockets.asyncio.server import Server, ServerConnection

from . import connection_file

logger = logging.getLogger(__name__)

# FORK: never route the local editor connection through a system proxy
# (websockets >= 15 honours proxy environment variables; older versions have no proxy argument)
_NO_PROXY = {"proxy": None} if "proxy" in inspect.signature(websockets.connect.__init__).parameters else {}

# Default port range matching Godot plugin expectations
BASE_PORT = 6505
MAX_PORT = 6514
PING_INTERVAL = 10.0  # seconds – JSON-RPC ping sent to Godot
PING_TIMEOUT = 30.0  # seconds – WebSocket protocol-level pong timeout


class GodotBridge:
    """Manages WebSocket server and communication with Godot editor plugin."""

    def __init__(self, port: int = BASE_PORT, port_retry: bool = True):
        self.port = port
        self._port_retry = port_retry
        self._server: Server | None = None
        self._connection: ServerConnection | None = None
        self._request_id: int = 0
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._connected = asyncio.Event()
        self._lock = asyncio.Lock()
        self._ping_task: asyncio.Task | None = None
        # FORK: connection-file mode
        self._project: Path | None = None  # Godot project this server serves
        self._roots_checked = False
        self._connect_lock = asyncio.Lock()
        self._outbound = False  # current connection was opened by us (connection file)
        self._fixed_error: str | None = None  # why the fixed ports are not in use

    @property
    def is_connected(self) -> bool:
        return self._connection is not None

    async def start(self) -> None:
        """Get ready to reach Godot.

        FORK: when the project is known (GODOT_MCP_PROJECT or the working
        directory) the fixed ports are not used: we connect through the
        project's connection file on the first call. Otherwise we also listen
        on the fixed ports (upstream behaviour); failing to bind them is no
        longer fatal, because the project may still come from the client's
        roots on the first call. GODOT_MCP_FIXED_PORTS=on|off|auto overrides.

        If port_retry is True, tries ports BASE_PORT through MAX_PORT in
        sequence until one is available (matching v1.13.2 parallel-session
        behavior). If port_retry is False, only the configured port is tried.
        """
        self._project = connection_file.from_env() or connection_file.from_cwd()
        fixed = os.environ.get("GODOT_MCP_FIXED_PORTS", "auto").strip().lower()
        if fixed == "off" or (fixed != "on" and self._project is not None):
            self._fixed_error = "not used: this server connects through the project's connection file"
            logger.info(f"Connection-file mode for {self._project or '(project from client roots)'}")
            return
        try:
            if self._port_retry:
                await self._start_with_retry()
            else:
                await self._bind_port(self.port)
        except (OSError, ValueError) as e:
            self._fixed_error = str(e)
            logger.warning(f"Fixed ports unavailable ({e}); will use the project's connection file instead")

    async def _bind_port(self, port: int) -> None:
        """Bind to a specific port."""
        self._server = await websockets.serve(
            self._handle_connection,
            "127.0.0.1",
            port,
            max_size=16 * 1024 * 1024,  # 16MB to match Godot buffer
            ping_interval=PING_INTERVAL,
            ping_timeout=PING_TIMEOUT,
        )
        self.port = port
        logger.info(f"WebSocket server started on ws://127.0.0.1:{self.port}")

    async def _start_with_retry(self) -> None:
        """Bind the configured port first, then the rest of BASE_PORT..MAX_PORT.

        The Godot plugin only ever connects to BASE_PORT..MAX_PORT, so a
        configured port outside that range would never be reached.
        """
        if not BASE_PORT <= self.port <= MAX_PORT:
            raise ValueError(
                f"GODOT_MCP_PORT={self.port} is outside {BASE_PORT}-{MAX_PORT}, "
                "the only ports the Godot plugin connects to."
            )
        candidate_ports = [self.port] + [
            port for port in range(BASE_PORT, MAX_PORT + 1) if port != self.port
        ]
        last_error: OSError | None = None
        for port in candidate_ports:
            try:
                await self._bind_port(port)
                return
            except OSError as e:
                last_error = e
                logger.debug(f"Port {port} unavailable: {e}")
                continue

        # All ports exhausted
        raise OSError(
            f"All MCP ports {BASE_PORT}-{MAX_PORT} are in use. "
            f"Close other MCP sessions or set GODOT_MCP_PORT to a specific port. "
            f"Last error: {last_error}"
        )

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        # Cancel ping task
        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
            self._ping_task = None

        if self._connection:
            await self._connection.close(1000, "Server shutting down")
            self._connection = None
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        # Cancel all pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()
        self._connected.clear()
        logger.info("WebSocket server stopped")

    async def wait_for_connection(self, timeout: float | None = None) -> bool:
        """Wait until Godot connects. Returns True if connected, False on timeout."""
        try:
            await asyncio.wait_for(self._connected.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def call_godot(self, method: str, params: dict[str, Any] | None = None, timeout: float = 30.0) -> Any:
        """Send a JSON-RPC 2.0 request to Godot and wait for response.

        Args:
            method: The command method name (e.g. "get_project_info")
            params: Optional parameters dictionary
            timeout: Timeout in seconds (default 30s)

        Returns:
            The result from Godot

        Raises:
            ConnectionError: If not connected to Godot
            TimeoutError: If Godot doesn't respond in time
            RuntimeError: If Godot returns an error
        """
        if not self._connection or not self._roots_checked:
            await self._ensure_connection()

        async with self._lock:
            self._request_id += 1
            request_id = self._request_id

        # Create JSON-RPC 2.0 request
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        # Create future for response
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending_requests[request_id] = future

        try:
            # Send request
            await self._connection.send(json.dumps(request))
            logger.debug(f"Sent request #{request_id}: {method}")

            # Wait for response
            result = await asyncio.wait_for(future, timeout=timeout)
            return result

        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            raise TimeoutError(
                f"Godot did not respond to '{method}' within {timeout}s. "
                "The editor might be busy or the command is taking too long."
            )
        except websockets.exceptions.ConnectionClosed:
            self._pending_requests.pop(request_id, None)
            raise ConnectionError("Connection to Godot was lost during request.")

    async def _handle_connection(self, websocket: ServerConnection, outbound: bool = False) -> None:
        """Handle a WebSocket connection to Godot (incoming on the fixed ports,
        or outbound through the connection file)."""
        if not outbound and self._outbound:
            # FORK: bound to our project's editor; an editor of another project
            # connecting to the fixed port must not take over.
            await websocket.close(1008, "This MCP server is bound to another project")
            return
        if self._connection and self._connection is not websocket:
            # Close old connection if any
            logger.info("New Godot connection, replacing old one")
            # Cancel old ping task
            if self._ping_task and not self._ping_task.done():
                self._ping_task.cancel()
            try:
                await self._connection.close(1000, "Replaced by new connection")
            except Exception:
                pass

        self._connection = websocket
        self._connected.set()
        logger.info(f"Godot editor connected from {websocket.remote_address}")

        # Start JSON-RPC ping task for this connection. Kept in a local so this
        # handler only ever cancels its own task: when a new connection replaces
        # this one, self._ping_task already belongs to the newcomer.
        ping_task = asyncio.create_task(self._ping_loop(websocket))
        self._ping_task = ping_task

        try:
            async for message in websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Godot disconnected: {e}")
        finally:
            if not ping_task.done():
                ping_task.cancel()
                try:
                    await ping_task
                except asyncio.CancelledError:
                    pass
            if self._ping_task is ping_task:
                self._ping_task = None

            if self._connection is websocket:
                self._connection = None
                self._outbound = False  # FORK: next call rereads the connection file
                self._connected.clear()
                # Fail all pending requests
                for req_id, future in list(self._pending_requests.items()):
                    if not future.done():
                        future.set_exception(
                            ConnectionError("Godot disconnected")
                        )
                self._pending_requests.clear()

    async def _ping_loop(self, websocket: ServerConnection) -> None:
        """Send periodic JSON-RPC pings to Godot to keep the connection alive.

        This ensures Godot's inactivity timer (30s) is reset even when no
        tool calls are in progress. Matches the Node.js server behavior of
        sending pings every 10s.
        """
        try:
            while True:
                await asyncio.sleep(PING_INTERVAL)
                if websocket.close_code is not None:
                    break
                try:
                    await websocket.send(
                        json.dumps({"jsonrpc": "2.0", "method": "ping", "params": {}})
                    )
                    logger.debug("Sent JSON-RPC ping to Godot")
                except websockets.exceptions.ConnectionClosed:
                    break
        except asyncio.CancelledError:
            pass

    async def _handle_message(self, raw: str | bytes) -> None:
        """Process a message received from Godot."""
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from Godot: {raw[:100]}")
            return

        if not isinstance(msg, dict):
            return

        # Handle pong (response to our ping)
        if msg.get("method") == "pong":
            return

        # Handle ping from Godot
        if msg.get("method") == "ping":
            if self._connection:
                await self._connection.send(
                    json.dumps({"jsonrpc": "2.0", "method": "pong", "params": {}})
                )
            return

        # Handle auth_required from Godot (opt-in connection token)
        if msg.get("method") == "auth_required":
            token = self._read_auth_token()
            if token and self._connection:
                await self._connection.send(
                    json.dumps({"jsonrpc": "2.0", "method": "auth", "params": {"token": token}})
                )
                logger.info("Responded to auth_required with connection token")
            else:
                logger.warning(
                    "Godot requires a connection token but none is configured. "
                    "Set GODOT_MCP_TOKEN or GODOT_MCP_TOKEN_FILE environment variable."
                )
            return

        # Handle JSON-RPC response (has "id" field)
        msg_id = msg.get("id")
        if msg_id is not None and msg_id in self._pending_requests:
            future = self._pending_requests.pop(msg_id)
            if future.done():
                return

            if "error" in msg:
                error = msg["error"]
                error_msg = error.get("message", "Unknown error")
                error_data = error.get("data", {})
                suggestion = error_data.get("suggestion", "")
                full_msg = f"{error_msg}"
                if suggestion:
                    full_msg += f" (Suggestion: {suggestion})"
                future.set_exception(RuntimeError(full_msg))
            else:
                future.set_result(msg.get("result", {}))

    # --- FORK: connection-file mode ------------------------------------------

    async def _ensure_connection(self) -> None:
        """Connect to our project's editor through its connection file.

        On the first call the client's roots are consulted (once) when the
        project is not known yet; if they name a project that has a connection
        file, the fixed ports are given up so that editors of other projects
        cannot reach this server.
        """
        async with self._connect_lock:
            ambiguous: list[Path] = []
            if not self._roots_checked:
                self._roots_checked = True
                if self._project is None:
                    project, ambiguous = await self._project_from_roots()
                    if project is not None:
                        self._project = project
                        logger.info(f"Godot project from client roots: {project}")
                if self._project is not None and (self._project / connection_file.CONNECTION_FILE).is_file():
                    await self._close_fixed()
            if self._connection:
                return
            if self._project is None:
                raise ConnectionError(self._no_project_message(ambiguous))
            await self._connect_file(self._project)

    async def _project_from_roots(self) -> tuple[Path | None, list[Path]]:
        try:
            from fastmcp.server.dependencies import get_context

            roots = await asyncio.wait_for(get_context().list_roots(), timeout=5.0)
        except Exception as e:  # no request context, client without roots, timeout
            logger.debug(f"Client roots unavailable: {e}")
            return None, []
        paths = [p for p in (connection_file.root_to_path(str(r.uri)) for r in roots) if p is not None]
        project, candidates = connection_file.from_roots(paths)
        return project, (candidates if project is None else [])

    def _no_project_message(self, ambiguous: list[Path]) -> str:
        head = "Not connected to a Godot editor. "
        if ambiguous:
            listed = ", ".join(str(p) for p in ambiguous)
            return head + f"The workspace has several Godot projects ({listed}); set GODOT_MCP_PROJECT to the one to use."
        fixed = f" Fixed ports {BASE_PORT}-{MAX_PORT}: {self._fixed_error}." if self._fixed_error else (
            f" Listening on ws://127.0.0.1:{self.port} for an editor to connect; none has." if self._server else ""
        )
        return head + (
            "This server could not tell which Godot project to use: set GODOT_MCP_PROJECT to the project "
            "directory, start the server from inside the project, or use an MCP client that reports "
            "workspace roots." + fixed
        )

    async def _close_fixed(self) -> None:
        """Stop listening on the fixed ports and drop an editor that came in on them."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
            self._fixed_error = "closed: this server uses the project's connection file"
            logger.info("Stopped listening on the fixed ports")
        if self._connection and not self._outbound:
            await self._connection.close(1000, "Switching to the project's connection file")
            self._connection = None
            self._connected.clear()

    async def _connect_file(self, project: Path) -> None:
        try:
            info = connection_file.read(project)
        except connection_file.ConnectionFileError as e:
            raise ConnectionError(f"Not connected to a Godot editor: {e}") from e
        try:
            ws = await websockets.connect(
                f"ws://127.0.0.1:{info.port}",
                max_size=16 * 1024 * 1024,  # 16MB to match Godot buffer
                ping_interval=PING_INTERVAL,
                ping_timeout=PING_TIMEOUT,
                open_timeout=5.0,
                **_NO_PROXY,
            )
        except (OSError, asyncio.TimeoutError, websockets.exceptions.WebSocketException) as e:
            alive = connection_file.pid_alive(info.pid)
            why = (
                f"editor process {info.pid} that wrote {info.file} is no longer running: "
                "open the project in Godot again"
                if alive is False
                else f"{info.file} was written by editor process {info.pid}; if that editor was closed "
                "or crashed, open the project in Godot again"
            )
            raise ConnectionError(
                f"Could not reach the Godot editor of {project} at 127.0.0.1:{info.port} "
                f"({type(e).__name__}). The {why}."
            ) from e
        try:
            async with self._lock:
                self._request_id += 1
                auth_id = self._request_id
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": auth_id, "method": "auth", "params": {"token": info.token}}))
            reply = json.loads(await asyncio.wait_for(ws.recv(), timeout=5.0))
        except Exception as e:
            await ws.close()
            raise ConnectionError(f"The Godot editor of {project} did not complete the handshake ({e}).") from e
        if not isinstance(reply, dict) or "error" in reply:
            await ws.close()
            err = reply.get("error", {}) if isinstance(reply, dict) else {}
            raise ConnectionError(f"The Godot editor of {project} refused the connection: {err.get('message', reply)}")
        got = str((reply.get("result") or {}).get("project_path", ""))
        if got and not connection_file.same_path(got, project):
            await ws.close()
            raise ConnectionError(f"{info.file} points to an editor of another project ({got}); restart the Godot editor of {project}.")
        self._connection = ws
        self._outbound = True
        self._connected.set()
        asyncio.create_task(self._handle_connection(ws, outbound=True))
        logger.info(f"Connected to the Godot editor of {project} at 127.0.0.1:{info.port}")

    def _read_auth_token(self) -> str:
        """Read the connection token from environment or file.

        Checks GODOT_MCP_TOKEN first (inline token), then GODOT_MCP_TOKEN_FILE
        (path to a file containing the token). Returns empty string if neither
        is available.
        """
        # Direct token in environment
        token = os.environ.get("GODOT_MCP_TOKEN", "").strip()
        if token:
            return token

        # Token file path
        token_file = os.environ.get("GODOT_MCP_TOKEN_FILE", "").strip()
        if token_file and os.path.isfile(token_file):
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except OSError as e:
                logger.warning(f"Could not read token file {token_file}: {e}")

        return ""