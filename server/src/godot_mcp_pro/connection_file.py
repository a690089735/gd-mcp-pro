"""Find the Godot editor of THIS project through its connection file.

Fork addition (not in upstream). The editor plugin (addons/godot_mcp/
mcp_listener.gd) listens on a port the OS picks and writes
``<project>/.godot/mcp_connection.json`` with the port and a per-session token.
The server finds its project, reads that file and connects to the editor.

Which project:
1. ``GODOT_MCP_PROJECT``: the project directory (or its project.godot);
2. the MCP client's roots (workspace folders the client announces): a root
   that is a Godot project, or has exactly one Godot project directly inside;
3. the server's working directory or one of its parents.

See memory-bank/systemPatterns.md (connection-file mode).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

CONNECTION_FILE = Path(".godot") / "mcp_connection.json"
FORMAT = 1


@dataclass
class ConnectionInfo:
    port: int
    token: str
    pid: int | None
    project_path: str
    file: Path


class ConnectionFileError(Exception):
    """The connection file is missing or unreadable; the message says what to do."""


def is_project(path: Path) -> bool:
    return (path / "project.godot").is_file()


def from_env() -> Path | None:
    raw = os.environ.get("GODOT_MCP_PROJECT", "").strip()
    if not raw:
        return None
    p = Path(raw).expanduser()
    if p.name == "project.godot":
        p = p.parent
    return p.resolve()


def from_cwd(cwd: Path | None = None) -> Path | None:
    here = (cwd or Path.cwd()).resolve()
    for p in [here, *here.parents]:
        if is_project(p):
            return p
    return None


def root_to_path(uri: str) -> Path | None:
    parsed = urlparse(str(uri))
    if parsed.scheme != "file":
        return None
    path = unquote(parsed.path)
    # file:///E:/x -> "/E:/x" on Windows
    if os.name == "nt" and len(path) >= 3 and path[0] == "/" and path[2] == ":":
        path = path[1:]
    if parsed.netloc and parsed.netloc != "localhost":
        path = f"//{parsed.netloc}{path}"  # UNC share
    return Path(path)


def from_roots(roots: list[Path]) -> tuple[Path | None, list[Path]]:
    """Project from the client's roots. Returns (project, candidates): project is
    None when there is none or more than one (candidates lists them)."""
    found: list[Path] = []
    for root in roots:
        if is_project(root):
            found.append(root.resolve())
            continue
        try:
            children = [c for c in root.iterdir() if c.is_dir() and not c.name.startswith(".")]
        except OSError:
            continue
        found.extend(c.resolve() for c in children if is_project(c))
    unique = list(dict.fromkeys(found))
    return (unique[0] if len(unique) == 1 else None), unique


def read(project: Path) -> ConnectionInfo:
    file = project / CONNECTION_FILE
    if not file.is_file():
        raise ConnectionFileError(
            f"{file} does not exist: the Godot editor is not open on {project}, "
            "or its MCP plugin is disabled or an older version without connection-file support "
            "(update addons/godot_mcp from this fork)."
        )
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        port = int(data["port"])
        token = str(data["token"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise ConnectionFileError(f"{file} is unreadable ({e}); restart the Godot editor to rewrite it.") from e
    pid = data.get("pid")
    return ConnectionInfo(
        port=port,
        token=token,
        pid=int(pid) if isinstance(pid, int) else None,
        project_path=str(data.get("project_path", "")),
        file=file,
    )


def pid_alive(pid: int | None) -> bool | None:
    """Whether a process is running; None when it cannot be told."""
    if not pid:
        return None
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False if kernel32.GetLastError() == 87 else None  # ERROR_INVALID_PARAMETER: no such pid
        try:
            code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return None
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return None
    return True


def same_path(a: str | Path, b: str | Path) -> bool:
    def norm(p: str | Path) -> str:
        s = os.path.normcase(os.path.normpath(str(p).replace("\\", "/")))
        return s.rstrip("\\/")

    return norm(a) == norm(b)
