"""WebSocket bridge to Godot editor plugin.

The Godot plugin acts as a WebSocket CLIENT that connects to us.
We act as a WebSocket SERVER on ports 6505-6514.
Communication uses JSON-RPC 2.0 protocol.
"""

import asyncio
import json
import logging
from typing import Any

import websockets
from websockets.asyncio.server import Server, ServerConnection

logger = logging.getLogger(__name__)

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

    @property
    def is_connected(self) -> bool:
        return self._connection is not None

    async def start(self) -> None:
        """Start the WebSocket server and wait for Godot to connect.

        If port_retry is True, tries ports BASE_PORT through MAX_PORT in
        sequence until one is available (matching v1.13.2 parallel-session
        behavior). If port_retry is False, only the configured port is tried.
        """
        if self._port_retry:
            await self._start_with_retry()
        else:
            await self._bind_port(self.port)

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
        """Try binding to ports BASE_PORT..MAX_PORT in sequence."""
        last_error: OSError | None = None
        for port in range(BASE_PORT, MAX_PORT + 1):
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
        if not self._connection:
            raise ConnectionError(
                "Not connected to Godot editor. "
                "Make sure the Godot editor is running with the MCP plugin enabled."
            )

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

    async def _handle_connection(self, websocket: ServerConnection) -> None:
        """Handle incoming WebSocket connection from Godot."""
        if self._connection:
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

        # Start JSON-RPC ping task for this connection
        self._ping_task = asyncio.create_task(self._ping_loop(websocket))

        try:
            async for message in websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Godot disconnected: {e}")
        finally:
            # Cancel ping task for this connection
            if self._ping_task and not self._ping_task.done():
                self._ping_task.cancel()
                try:
                    await self._ping_task
                except asyncio.CancelledError:
                    pass
                self._ping_task = None

            if self._connection is websocket:
                self._connection = None
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