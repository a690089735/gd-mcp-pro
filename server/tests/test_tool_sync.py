"""Guard the tool-count contract between GDScript, full mode, and compact mode.

Three things must stay in lockstep:

1. Every GDScript command in ``addons/godot_mcp/commands/`` is exposed by exactly
   one full-mode Python tool.
2. Compact mode (``--compact``) reaches the same set of commands through its
   ``ACTION_MAP`` dictionaries — no command may become unreachable just because
   the user opted into the smaller tool surface.
3. Compact mode collapses everything into a handful of umbrella tools.

Run after every upstream merge:

    python -m pytest server/tests/ -v
    # or standalone, without pytest:
    python server/tests/test_tool_sync.py
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = SERVER_ROOT / "src" / "godot_mcp_pro" / "tools"
COMMANDS_DIR = SERVER_ROOT.parent / "addons" / "godot_mcp" / "commands"

SKIP_MODULES = {"__init__.py", "compact.py"}

# Pure-Python tools with no GDScript counterpart (implemented in the server).
PYTHON_ONLY_TOOLS = {"batch_execute"}


def collect_gdscript_commands() -> set[str]:
    """Every command name registered in a get_commands() dictionary.

    Entries look like ``"add_node": _add_node`` — requiring the value to be a
    handler reference avoids picking up unrelated dictionary literals that may
    appear inside the same brace block.
    """
    commands: set[str] = set()
    for gd_file in COMMANDS_DIR.glob("*.gd"):
        text = gd_file.read_text(encoding="utf-8")
        match = re.search(
            r"func get_commands\(\)[\s\S]*?\n\treturn \{([\s\S]*?)\n\t\}", text
        )
        if not match:
            continue
        commands |= set(
            re.findall(r'"([a-z0-9_]+)"\s*:\s*_[A-Za-z0-9_]+', match.group(1))
        )
    return commands


def collect_full_mode() -> tuple[set[str], int]:
    """Returns (GDScript commands reached, number of @mcp.tool() functions)."""
    methods: set[str] = set()
    tool_count = 0
    for py_file in TOOLS_DIR.glob("*.py"):
        if py_file.name in SKIP_MODULES:
            continue
        text = py_file.read_text(encoding="utf-8")
        tool_count += len(re.findall(r"@mcp\.tool\(\)", text))
        methods |= set(re.findall(r'bridge\.call_godot\(\s*"([a-z0-9_]+)"', text))
    return methods, tool_count


def collect_compact_mode() -> tuple[set[str], int]:
    """Returns (GDScript commands reached via ACTION_MAP, umbrella tool count)."""
    text = (TOOLS_DIR / "compact.py").read_text(encoding="utf-8")
    tool_count = len(re.findall(r"@mcp\.tool\(\)", text))

    methods: set[str] = set()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "ACTION_MAP"
            for target in node.targets
        ):
            continue
        assert isinstance(node.value, ast.Dict), "ACTION_MAP must be a dict literal"
        for value in node.value.values:
            assert isinstance(value, ast.Constant), "ACTION_MAP values must be literals"
            methods.add(value.value)
    return methods, tool_count


def test_full_mode_covers_every_gdscript_command() -> None:
    gd = collect_gdscript_commands()
    full, _ = collect_full_mode()

    unexposed = sorted(gd - full)
    phantom = sorted(full - gd)
    assert not unexposed, f"GDScript commands with no full-mode tool: {unexposed}"
    assert not phantom, f"Full-mode tools calling unknown commands: {phantom}"


def test_compact_mode_covers_every_gdscript_command() -> None:
    gd = collect_gdscript_commands()
    compact, _ = collect_compact_mode()

    unreachable = sorted(gd - compact)
    phantom = sorted(compact - gd)
    assert not unreachable, (
        f"Commands unreachable in --compact mode: {unreachable}"
    )
    assert not phantom, f"compact.py maps to unknown commands: {phantom}"


def test_full_and_compact_expose_the_same_commands() -> None:
    full, _ = collect_full_mode()
    compact, _ = collect_compact_mode()

    only_full = sorted(full - compact)
    only_compact = sorted(compact - full)
    assert not only_full, f"Only reachable in full mode: {only_full}"
    assert not only_compact, f"Only reachable in compact mode: {only_compact}"


def test_full_mode_tool_count_matches_command_count() -> None:
    """One full-mode tool per GDScript command, plus the pure-Python extras."""
    gd = collect_gdscript_commands()
    _, tool_count = collect_full_mode()

    expected = len(gd) + len(PYTHON_ONLY_TOOLS)
    assert tool_count == expected, (
        f"Full mode registers {tool_count} tools but {expected} were expected "
        f"({len(gd)} GDScript commands + {len(PYTHON_ONLY_TOOLS)} Python-only)."
    )


def test_compact_mode_stays_small() -> None:
    """Compact mode exists to shrink the tool surface; keep it that way."""
    _, tool_count = collect_compact_mode()
    assert tool_count <= 30, (
        f"Compact mode registers {tool_count} tools; it should stay well under 30 "
        "or it loses its reason to exist."
    )


if __name__ == "__main__":
    gd = collect_gdscript_commands()
    full, full_tools = collect_full_mode()
    compact, compact_tools = collect_compact_mode()
    print(f"GDScript commands       : {len(gd)}")
    print(f"Full-mode tools         : {full_tools}")
    print(f"Full-mode commands      : {len(full)}")
    print(f"Compact-mode tools      : {compact_tools}")
    print(f"Compact-mode commands   : {len(compact)}")
    print()

    failures = 0
    for check in (
        test_full_mode_covers_every_gdscript_command,
        test_compact_mode_covers_every_gdscript_command,
        test_full_and_compact_expose_the_same_commands,
        test_full_mode_tool_count_matches_command_count,
        test_compact_mode_stays_small,
    ):
        try:
            check()
            print(f"PASS  {check.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {check.__name__}\n{exc}")

    raise SystemExit(1 if failures else 0)