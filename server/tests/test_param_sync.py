"""Guard against Python↔GDScript parameter drift.

The Python MCP layer forwards JSON dictionaries to GDScript command handlers.
Nothing at runtime checks that the keys Python *sends* are the keys GDScript
*reads*, so the two sides can silently diverge — a tool then either fails
outright (missing required key) or "succeeds" while doing nothing (dead keys).

This test parses both sides statically and fails on any mismatch:

- **A / DEAD**: Python sends a key the GDScript handler never reads.
- **B / MISSING**: The GDScript handler reads a key Python never sends.

Run it after every upstream merge:

    python -m pytest server/tests/ -v
    # or standalone, without pytest:
    python server/tests/test_param_sync.py
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = SERVER_ROOT / "src" / "godot_mcp_pro" / "tools"
COMMANDS_DIR = SERVER_ROOT.parent / "addons" / "godot_mcp" / "commands"

# Python modules that are not 1:1 GDScript wrappers.
SKIP_MODULES = {"__init__.py", "compact.py"}

# Ways a GDScript handler can read a key out of its `params` dictionary.
KEY_PATTERNS = (
    r'require_\w+\(\s*params\s*,\s*"([a-z0-9_]+)"',
    r'optional_\w+\(\s*params\s*,\s*"([a-z0-9_]+)"',
    r'params\.has\(\s*"([a-z0-9_]+)"\s*\)',
    r'params\.get\(\s*"([a-z0-9_]+)"',
    r'params\[\s*"([a-z0-9_]+)"\s*\]',
)

# Keys Python may send that no handler reads, with the reason they are allowed.
# Keep this empty unless there is a deliberate, documented exception.
ALLOWED_DEAD: dict[str, set[str]] = {}

# Keys a handler reads that Python deliberately does not expose.
ALLOWED_MISSING: dict[str, set[str]] = {}


def _split_gd_functions(text: str) -> dict[str, str]:
    """Map GDScript function name -> body text."""
    out: dict[str, str] = {}
    parts = re.split(r"\nfunc ([A-Za-z0-9_]+)\(", text)
    for i in range(1, len(parts), 2):
        out[parts[i]] = parts[i + 1]
    return out


def _direct_keys(body: str) -> set[str]:
    keys: set[str] = set()
    for pattern in KEY_PATTERNS:
        keys |= set(re.findall(pattern, body))
    return keys


def collect_gdscript_params() -> dict[str, set[str]]:
    """command name -> set of param keys the handler reads (helpers included)."""
    base_funcs = _split_gd_functions(
        (COMMANDS_DIR / "base_command.gd").read_text(encoding="utf-8")
    )

    result: dict[str, set[str]] = {}
    for gd_file in sorted(COMMANDS_DIR.glob("*.gd")):
        if gd_file.name == "base_command.gd":
            continue
        text = gd_file.read_text(encoding="utf-8")
        all_funcs = {**base_funcs, **_split_gd_functions(text)}

        command_map: dict[str, str] = {}
        match = re.search(
            r"func get_commands\(\)[\s\S]*?\n\treturn \{([\s\S]*?)\n\t\}", text
        )
        if match:
            for cmd, func in re.findall(
                r'"([a-z0-9_]+)"\s*:\s*(_[A-Za-z0-9_]+)', match.group(1)
            ):
                command_map[cmd] = func

        def collect(func_name: str, seen: set[str]) -> set[str]:
            """Keys read by func_name, following helpers that receive `params`."""
            if func_name in seen or func_name not in all_funcs:
                return set()
            seen.add(func_name)
            body = all_funcs[func_name]
            keys = _direct_keys(body)
            forwarded = re.findall(
                r"\b([A-Za-z0-9_]+)\(\s*[A-Za-z0-9_.]*\s*,?\s*params\s*[,)]", body
            ) + re.findall(r"\b([A-Za-z0-9_]+)\(\s*params\s*[,)]", body)
            for helper in forwarded:
                keys |= collect(helper, seen)
            return keys

        for cmd, func in command_map.items():
            result[cmd] = collect(func, set())
    return result


def collect_python_params() -> tuple[dict[str, set[str]], set[str]]:
    """command name -> set of literal param keys Python sends.

    Returns (params, dynamic) where `dynamic` holds commands whose payload is
    built at runtime (e.g. conditionally populated dicts); those cannot be
    checked for MISSING keys statically.
    """
    params: dict[str, set[str]] = {}
    dynamic: set[str] = set()

    for py_file in sorted(TOOLS_DIR.glob("*.py")):
        if py_file.name in SKIP_MODULES:
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "call_godot"):
                continue
            if not node.args or not isinstance(node.args[0], ast.Constant):
                continue
            command = node.args[0].value
            params.setdefault(command, set())
            if len(node.args) < 2:
                continue
            payload = node.args[1]
            if isinstance(payload, ast.Dict):
                for key in payload.keys:
                    if isinstance(key, ast.Constant):
                        params[command].add(key.value)
                    else:  # **spread of a caller-supplied dict
                        dynamic.add(command)
            else:  # a variable built up conditionally
                dynamic.add(command)
    return params, dynamic


def test_every_command_is_exposed() -> None:
    gd = collect_gdscript_params()
    py, _ = collect_python_params()

    missing = sorted(set(gd) - set(py))
    extra = sorted(set(py) - set(gd))
    assert not missing, f"GDScript commands not exposed by any Python tool: {missing}"
    assert not extra, f"Python tools calling non-existent GDScript commands: {extra}"


def test_no_dead_params() -> None:
    """Python must not send keys the GDScript handler ignores."""
    gd = collect_gdscript_params()
    py, _ = collect_python_params()

    problems: list[str] = []
    for command in sorted(py):
        if command not in gd:
            continue
        dead = py[command] - gd[command] - ALLOWED_DEAD.get(command, set())
        if dead:
            problems.append(f"  {command}: {sorted(dead)}")

    assert not problems, (
        "Python sends parameters the GDScript command never reads "
        "(they are silently dropped):\n" + "\n".join(problems)
    )


def test_no_unexposed_params() -> None:
    """Every key a GDScript handler reads should be reachable from Python."""
    gd = collect_gdscript_params()
    py, dynamic = collect_python_params()

    problems: list[str] = []
    for command in sorted(gd):
        if command not in py or command in dynamic:
            continue
        unexposed = gd[command] - py[command] - ALLOWED_MISSING.get(command, set())
        if unexposed:
            problems.append(f"  {command}: {sorted(unexposed)}")

    assert not problems, (
        "GDScript reads parameters no Python tool exposes "
        "(functionality unreachable):\n" + "\n".join(problems)
    )


if __name__ == "__main__":
    gd = collect_gdscript_params()
    py, dynamic = collect_python_params()
    print(f"GDScript commands: {len(gd)}   Python-mapped: {len(py)}")
    print(f"Dynamic-payload commands (excluded from MISSING check): {len(dynamic)}")

    failures = 0
    for check in (
        test_every_command_is_exposed,
        test_no_dead_params,
        test_no_unexposed_params,
    ):
        try:
            check()
            print(f"PASS  {check.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {check.__name__}\n{exc}")

    raise SystemExit(1 if failures else 0)