@tool
extends Node

## FORK ADDITION (not in upstream) — see memory-bank/fork-addon-patches.md.
##
## Connection-file mode. The editor listens on a port the OS picks (port 0)
## and publishes it, with a per-session token, in
## res://.godot/mcp_connection.json. The MCP server of THIS project reads that
## file and connects to this editor directly.
##
## Why: the upstream scheme (MCP server listens on fixed ports 6505-6514, every
## editor connects to all of them) breaks when the OS reserves those ports
## (Windows excluded port ranges give WinError 10013 on bind), and with several
## editors open each server is fought over by every editor, so commands can
## land in another project. A port picked by the OS is always bindable, and the
## file lives inside the project, so a server can only find its own editor.
##
## Accepted peers are handed to websocket_server.gd (register_listener_peer)
## and from then on go through its normal dispatch, so commands, ping/pong and
## responses behave exactly like the upstream connections.

const FILE_PATH := "res://.godot/mcp_connection.json"
const FORMAT := 1
const BUFFER_SIZE := 16 * 1024 * 1024  # same as websocket_server.gd
const HANDSHAKE_TIMEOUT := 10.0  # WebSocket upgrade not finished
const AUTH_TIMEOUT := 5.0  # connected but no valid token yet
const INACTIVITY_TIMEOUT := 30.0  # the MCP server pings every 10s
## Connection keys start above any real port number, so they never collide
## with the upstream per-port dictionaries (6505-6514) they share.
const KEY_BASE := 70000

var server: Node  # websocket_server.gd

var _tcp: TCPServer
var _port := 0
var _token := ""
var _next_key := KEY_BASE
var _conns: Dictionary = {}  # key -> {ws, authed, age, idle}


func start() -> bool:
	_tcp = TCPServer.new()
	var err := _tcp.listen(0, "127.0.0.1")
	if err != OK:
		push_warning("[MCP] Could not open a listening port (%s); only the fixed ports 6505-6514 will be used." % error_string(err))
		_tcp = null
		return false
	_port = _tcp.get_local_port()
	_token = Crypto.new().generate_random_bytes(24).hex_encode()
	if not _write_file():
		_tcp.stop()
		_tcp = null
		return false
	print("[MCP] Listening on 127.0.0.1:%d for this project's MCP server (%s)" % [_port, ProjectSettings.globalize_path(FILE_PATH)])
	return true


func stop() -> void:
	for key: int in _conns.keys():
		_drop(key, 1000, "Plugin shutting down")
	if _tcp:
		_tcp.stop()
		_tcp = null
	_remove_file()


func get_port() -> int:
	return _port


func _process(delta: float) -> void:
	if _tcp == null:
		return
	while _tcp.is_connection_available():
		var ws := WebSocketPeer.new()
		ws.outbound_buffer_size = BUFFER_SIZE
		ws.inbound_buffer_size = BUFFER_SIZE
		if ws.accept_stream(_tcp.take_connection()) != OK:
			continue
		_conns[_next_key] = {"ws": ws, "authed": false, "age": 0.0, "idle": 0.0}
		_next_key += 1

	for key: int in _conns.keys():
		var c: Dictionary = _conns[key]
		var ws: WebSocketPeer = c["ws"]
		ws.poll()
		c["age"] += delta
		match ws.get_ready_state():
			WebSocketPeer.STATE_OPEN:
				c["idle"] += delta
				while ws.get_available_packet_count() > 0:
					var text := ws.get_packet().get_string_from_utf8()
					c["idle"] = 0.0
					if c["authed"]:
						server.dispatch_listener_message(key, text)
					else:
						_handle_auth(key, c, text)
					if not _conns.has(key):
						break
				if not _conns.has(key):
					continue
				if not c["authed"] and c["age"] > HANDSHAKE_TIMEOUT + AUTH_TIMEOUT:
					_drop(key, 4001, "Authentication required")
				elif c["idle"] > INACTIVITY_TIMEOUT:
					push_warning("[MCP] Connection %d silent for %.0fs, closing" % [key, c["idle"]])
					_drop(key, 4000, "Heartbeat timeout")
			WebSocketPeer.STATE_CONNECTING:
				if c["age"] > HANDSHAKE_TIMEOUT:
					_drop(key, 1002, "Handshake timeout")
			WebSocketPeer.STATE_CLOSED:
				_drop(key, 1000, "")


## The first message must be {"method":"auth","params":{"token":...},"id":...}
## with the token from the connection file. The reply carries the project path
## so the server can check it reached the editor it was looking for.
func _handle_auth(key: int, c: Dictionary, text: String) -> void:
	var json := JSON.new()
	var msg: Variant = json.data if json.parse(text) == OK else null
	var id: Variant = msg.get("id") if msg is Dictionary else null
	var ws: WebSocketPeer = c["ws"]
	if not (msg is Dictionary) or msg.get("method") != "auth":
		ws.send_text(JSON.stringify({"jsonrpc": "2.0", "id": id, "error": {"code": -32001, "message": "Send {\"method\":\"auth\",\"params\":{\"token\":...}} first; the token is in %s" % FILE_PATH}}))
		return
	var params: Variant = msg.get("params", {})
	var supplied := str(params.get("token", "")) if params is Dictionary else ""
	if supplied != _token:
		push_warning("[MCP] Connection %d presented a wrong token" % key)
		ws.send_text(JSON.stringify({"jsonrpc": "2.0", "id": id, "error": {"code": -32001, "message": "Invalid token (the connection file was rewritten: reread it)"}}))
		_drop(key, 4001, "Invalid token")
		return
	c["authed"] = true
	server.register_listener_peer(key, ws)
	ws.send_text(JSON.stringify({"jsonrpc": "2.0", "id": id, "result": {
		"authenticated": true,
		"project_path": ProjectSettings.globalize_path("res://"),
		"pid": OS.get_process_id(),
	}}))
	print_verbose("[MCP] MCP server connected (connection %d)" % key)


func _drop(key: int, code: int, reason: String) -> void:
	var c: Dictionary = _conns.get(key, {})
	_conns.erase(key)
	if c.is_empty():
		return
	var ws: WebSocketPeer = c["ws"]
	if ws.get_ready_state() == WebSocketPeer.STATE_OPEN:
		ws.close(code, reason)
	if c["authed"]:
		server.unregister_listener_peer(key)


func _write_file() -> bool:
	var abs_path := ProjectSettings.globalize_path(FILE_PATH)
	DirAccess.make_dir_recursive_absolute(abs_path.get_base_dir())
	var info := {
		"format": FORMAT,
		"port": _port,
		"token": _token,
		"pid": OS.get_process_id(),
		"project_path": ProjectSettings.globalize_path("res://"),
		"godot_version": Engine.get_version_info().get("string", ""),
		"started_at": Time.get_datetime_string_from_system(true) + "Z",
	}
	var file := FileAccess.open(abs_path, FileAccess.WRITE)
	if file == null:
		push_warning("[MCP] Could not write %s (%s); only the fixed ports 6505-6514 will be used." % [abs_path, error_string(FileAccess.get_open_error())])
		return false
	file.store_string(JSON.stringify(info, "  "))
	file.close()
	return true


## Remove the file only while it is still ours: a second editor on the same
## project may have taken it over since.
func _remove_file() -> void:
	if _token.is_empty() or not FileAccess.file_exists(FILE_PATH):
		return
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(FILE_PATH))
	if data is Dictionary and data.get("token", "") == _token:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(FILE_PATH))
	_token = ""
