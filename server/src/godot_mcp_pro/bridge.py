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
PING_INTERVAL = 10.0  # seconds


class GodotBridge:
    """Manages WebSocket server and communication with Godot editor plugin."""

    def __init__(self, port: int = BASE_PORT):
        self.port = port
        self._server: Server | None = None
        self._connection: ServerConnection | None = None
        self._request_id: int = 0
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._connected = asyncio.Event()
        self._lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        return self._connection is not None

    async def start(self) -> None:
        """Start the WebSocket server and wait for Godot to connect."""
        self._server = await websockets.serve(
            self._handle_connection,
            "127.0.0.1",
            self.port,
            max_size=16 * 1024 * 1024,  # 16MB to match Godot buffer
            ping_interval=PING_INTERVAL,
            ping_timeout=30,
        )
        logger.info(f"WebSocket server started on ws://127.0.0.1:{self.port}")

    async def stop(self) -> None:
        """Stop the WebSocket server."""
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
            try:
                await self._connection.close(1000, "Replaced by new connection")
            except Exception:
                pass

        self._connection = websocket
        self._connected.set()
        logger.info(f"Godot editor connected from {websocket.remote_address}")

        try:
            async for message in websocket:
                await self._handle_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Godot disconnected: {e}")
        finally:
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