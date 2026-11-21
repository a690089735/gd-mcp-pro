"""Connection-file mode (fork addition): project discovery, file parsing, handshake.

Runs without Godot: a fake editor listens on an OS-picked port the way
addons/godot_mcp/mcp_listener.gd does. Run directly:
    python server/tests/test_connection_file.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import websockets  # noqa: E402

from godot_mcp_pro import connection_file  # noqa: E402
from godot_mcp_pro.bridge import GodotBridge  # noqa: E402


def make_project(root: Path, name: str) -> Path:
    p = root / name
    (p / ".godot").mkdir(parents=True)
    (p / "project.godot").write_text("config_version=5\n", encoding="utf-8")
    return p


def test_discovery():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        a = make_project(root, "a")
        b = make_project(root, "b")
        (a / "scenes").mkdir()
        assert connection_file.from_cwd(a / "scenes") == a.resolve()
        assert connection_file.from_cwd(root) is None
        assert connection_file.from_roots([a])[0] == a.resolve()
        project, candidates = connection_file.from_roots([root])
        assert project is None and set(candidates) == {a.resolve(), b.resolve()}
        only = root / "only"
        only.mkdir()
        c = make_project(only, "game")
        assert connection_file.from_roots([only])[0] == c.resolve()
        os.environ["GODOT_MCP_PROJECT"] = str(a / "project.godot")
        try:
            assert connection_file.from_env() == a.resolve()
        finally:
            del os.environ["GODOT_MCP_PROJECT"]
        uri = a.resolve().as_uri()
        assert connection_file.same_path(connection_file.root_to_path(uri), a.resolve())


def test_read_errors():
    with tempfile.TemporaryDirectory() as tmp:
        a = make_project(Path(tmp), "a")
        try:
            connection_file.read(a)
            raise AssertionError("missing file must raise")
        except connection_file.ConnectionFileError as e:
            assert "not open" in str(e) and "plugin" in str(e)
        (a / connection_file.CONNECTION_FILE).write_text("{", encoding="utf-8")
        try:
            connection_file.read(a)
            raise AssertionError("bad file must raise")
        except connection_file.ConnectionFileError as e:
            assert "restart the Godot editor" in str(e)


def test_pid_alive():
    assert connection_file.pid_alive(os.getpid()) is True
    assert connection_file.pid_alive(None) is None


async def fake_editor(project: Path, token: str, reported: str | None = None):
    """Listen like mcp_listener.gd: auth first, then answer get_project_info."""

    async def handler(ws):
        auth = json.loads(await ws.recv())
        if auth.get("method") != "auth" or auth["params"]["token"] != token:
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": auth.get("id"), "error": {"code": -32001, "message": "Invalid token"}}))
            await ws.close()
            return
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": auth["id"], "result": {"authenticated": True, "project_path": reported or str(project)}}))
        async for raw in ws:
            msg = json.loads(raw)
            if msg.get("method") == "ping":
                continue
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": {"project_name": project.name}}))

    server = await websockets.serve(handler, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    (project / connection_file.CONNECTION_FILE).write_text(
        json.dumps({"format": 1, "port": port, "token": token, "pid": os.getpid(), "project_path": str(project)}), encoding="utf-8"
    )
    return server


async def run_bridge(project: Path) -> GodotBridge:
    os.environ["GODOT_MCP_PROJECT"] = str(project)
    try:
        bridge = GodotBridge()
        await bridge.start()
    finally:
        del os.environ["GODOT_MCP_PROJECT"]
    return bridge


def test_connects_to_own_project():
    async def main():
        with tempfile.TemporaryDirectory() as tmp:
            a = make_project(Path(tmp), "a")
            b = make_project(Path(tmp), "b")
            sa = await fake_editor(a, "ta")
            sb = await fake_editor(b, "tb")
            ba, bb = await run_bridge(a), await run_bridge(b)
            try:
                assert ba._server is None, "project known: fixed ports not used"
                assert (await ba.call_godot("get_project_info"))["project_name"] == "a"
                assert (await bb.call_godot("get_project_info"))["project_name"] == "b"
                assert (await ba.call_godot("get_project_info"))["project_name"] == "a"
            finally:
                await ba.stop()
                await bb.stop()
                sa.close()
                sb.close()

    asyncio.run(main())


def test_refuses_wrong_token_and_wrong_project():
    async def main():
        with tempfile.TemporaryDirectory() as tmp:
            a = make_project(Path(tmp), "a")
            s = await fake_editor(a, "right")
            data = json.loads((a / connection_file.CONNECTION_FILE).read_text(encoding="utf-8"))
            data["token"] = "wrong"
            (a / connection_file.CONNECTION_FILE).write_text(json.dumps(data), encoding="utf-8")
            bridge = await run_bridge(a)
            try:
                await bridge.call_godot("get_project_info")
                raise AssertionError("wrong token must fail")
            except ConnectionError as e:
                assert "refused" in str(e)
            finally:
                await bridge.stop()
                s.close()
            b = make_project(Path(tmp), "b")
            s = await fake_editor(b, "t", reported=str(Path(tmp) / "other"))
            bridge = await run_bridge(b)
            try:
                await bridge.call_godot("get_project_info")
                raise AssertionError("other project must fail")
            except ConnectionError as e:
                assert "another project" in str(e)
            finally:
                await bridge.stop()
                s.close()

    asyncio.run(main())


def test_reconnects_after_editor_restart():
    async def main():
        with tempfile.TemporaryDirectory() as tmp:
            a = make_project(Path(tmp), "a")
            s = await fake_editor(a, "one")
            bridge = await run_bridge(a)
            try:
                assert (await bridge.call_godot("get_project_info"))["project_name"] == "a"
                s.close()
                await s.wait_closed()
                for _ in range(50):
                    if not bridge.is_connected:
                        break
                    await asyncio.sleep(0.05)
                try:
                    await bridge.call_godot("get_project_info")
                    raise AssertionError("closed editor must fail")
                except ConnectionError as e:
                    assert "Could not reach" in str(e)
                s = await fake_editor(a, "two")  # new port, new token
                assert (await bridge.call_godot("get_project_info"))["project_name"] == "a"
            finally:
                await bridge.stop()
                s.close()

    asyncio.run(main())


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {t.__name__}: {e!r}")
    sys.exit(1 if failed else 0)
