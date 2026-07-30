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
ALLOWED_MISSING: dict[str, set[str]] = {
    # These are read out of the NESTED params["params"] dictionary, which the
    # Python tool forwards verbatim; the flat names are not top-level keys.
    "add_audio_bus_effect": {
        "attack_us", "ceiling_db", "cutoff_hz", "damping", "depth", "drive",
        "dry", "feedback", "gain", "keep_hf_hz", "mix", "mode", "post_gain",
        "pre_gain", "range_max_hz", "range_min_hz", "rate_hz", "ratio",
        "release_ms", "resonance", "room_size", "soft_clip_db",
        "soft_clip_ratio", "spread", "tap1_active", "tap1_delay_ms",
        "tap1_level_db", "tap2_active", "tap2_delay_ms", "tap2_level_db",
        "threshold", "threshold_db", "voice_count", "volume_db", "wet",
    },
    # `layers` (bitmask) and `layer_bits` (1-based numbers) already cover the
    # supported input shapes; `layer_names` needs project-specific layer names
    # that the MCP layer cannot resolve.
    "set_navigation_layers": {"layer_names"},
}


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


def _own_nodes(func: ast.AST):
    """Walk a function body without descending into nested function definitions."""
    stack = list(ast.iter_child_nodes(func))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)):
            continue
        yield node
        stack.extend(ast.iter_child_nodes(node))


def _subscript_keys(func: ast.AST, name: str) -> set[str]:
    """Literal string keys assigned as `name["key"] = ...` inside `func`.

    Most tools build their payload conditionally:

        params = {"path": path}
        if force:
            params["force"] = True

    Without collecting these, ~1/3 of all commands would escape the DEAD check.
    """
    keys: set[str] = set()
    for node in _own_nodes(func):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets = [node.target]
        for target in targets:
            if (
                isinstance(target, ast.Subscript)
                and isinstance(target.value, ast.Name)
                and target.value.id == name
                and isinstance(target.slice, ast.Constant)
                and isinstance(target.slice.value, str)
            ):
                keys.add(target.slice.value)
    return keys


def collect_python_params() -> tuple[dict[str, set[str]], set[str]]:
    """command name -> set of literal param keys Python sends.

    Returns (params, dynamic) where `dynamic` holds commands whose payload
    contains keys that cannot be resolved statically (a `**spread` of a
    caller-supplied dict). Only those are exempt from the MISSING check;
    conditionally-assigned keys ARE resolved, so the DEAD check still applies.
    """
    params: dict[str, set[str]] = {}
    dynamic: set[str] = set()

    for py_file in sorted(TOOLS_DIR.glob("*.py")):
        if py_file.name in SKIP_MODULES:
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for func in ast.walk(tree):
            if not isinstance(func, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            for node in _own_nodes(func):
                if not isinstance(node, ast.Call):
                    continue
                target = node.func
                if not (
                    isinstance(target, ast.Attribute) and target.attr == "call_godot"
                ):
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
                elif isinstance(payload, ast.Name):
                    # A dict built up in local variables; resolve the keys
                    # assigned via `payload[...] = ...` plus any dict literal
                    # it was initialised with.
                    params[command] |= _subscript_keys(func, payload.id)
                    for node2 in _own_nodes(func):
                        if isinstance(node2, ast.Assign):
                            names = [
                                t
                                for t in node2.targets
                                if isinstance(t, ast.Name) and t.id == payload.id
                            ]
                            value = node2.value
                        elif isinstance(node2, ast.AnnAssign):
                            names = (
                                [node2.target]
                                if isinstance(node2.target, ast.Name)
                                and node2.target.id == payload.id
                                else []
                            )
                            value = node2.value
                        else:
                            continue
                        if not names or value is None:
                            continue
                        if isinstance(value, ast.Dict):
                            for key in value.keys:
                                if isinstance(key, ast.Constant):
                                    params[command].add(key.value)
                                else:
                                    dynamic.add(command)
                        elif isinstance(value, ast.Call) and isinstance(
                            value.func, ast.Name
                        ):
                            # e.g. params = _build_payload(...) — opaque
                            dynamic.add(command)
                        else:
                            dynamic.add(command)
                else:
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