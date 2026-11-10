"""Guard the Python-side wait budgets in godot_mcp_pro/timeouts.py.

If the server stops waiting before Godot answers, the caller sees a timeout
while Godot still finishes the work, and the result is lost. These tests check:

1. No tool hard-codes its own `timeout=`; every call that passes one goes
   through `call_timeout()`, so full mode, compact mode and batch_execute agree.
2. Each long-running command's budget stays above the deadline the addon
   enforces for it (values taken from addons/godot_mcp/commands/*.gd).

Run standalone, without pytest:

    python server/tests/test_timeouts.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = SERVER_ROOT / "src"
TOOLS_DIR = SOURCE_DIR / "godot_mcp_pro" / "tools"
sys.path.insert(0, str(SOURCE_DIR))

from godot_mcp_pro.timeouts import DEFAULT_CALL_TIMEOUT, call_timeout  # noqa: E402


def test_tools_take_timeouts_from_call_timeout() -> None:
    problems: list[str] = []
    for py_file in sorted(TOOLS_DIR.glob("*.py")):
        for line_number, line in enumerate(
            py_file.read_text(encoding="utf-8").splitlines(), start=1
        ):
            match = re.search(r"\btimeout=([^,)]+)", line)
            if match and not match.group(1).strip().startswith("call_timeout("):
                problems.append(f"  {py_file.name}:{line_number}: {line.strip()}")
    assert not problems, (
        "Tools must take their Python-side timeout from timeouts.call_timeout():\n"
        + "\n".join(problems)
    )


def test_budgets_outlast_addon_deadlines() -> None:
    # (method, params, deadline the addon itself may take, in seconds)
    cases = [
        ("run_headless_scene", {}, 120.0 + 2.0),
        ("run_headless_scene", {"timeout_sec": 900}, 900.0 + 2.0),
        ("run_headless_script", {"timeout_sec": 5000}, 900.0 + 2.0),
        ("export_patch_pck", {}, 300.0),
        ("export_patch_pck", {"timeout_sec": 1800}, 1800.0),
        ("export_patch_pck", {"timeout_sec": 99999}, 1800.0),
        ("move_to", {"timeout": 60}, 60.0 + 5.0),
        ("wait_for_node", {"timeout": 40}, 40.0 + 2.0),
        ("watch_signals", {"duration_ms": 30000}, 30.0 + 5.0),
        ("simulate_key", {"hold_sec": 600}, 600.0 + 30.0),
        ("replay_recording", {}, 120.0),
        ("run_stress_test", {"duration": 60}, 60.0 + 2.0 + 5.0 + 5.0),
        (
            "run_test_scenario",
            {
                "scene_path": "res://main.tscn",
                "steps": [
                    {"type": "wait", "seconds": 45},
                    {"type": "wait", "node_path": "Player", "timeout": 20},
                    {"type": "assert", "text": "Win"},
                    {"type": "screenshot"},
                    {"type": "input", "keycode": "space"},
                ],
            },
            1.5 + 45.0 + 22.0 + 5.0 + 5.0 + 1.0,
        ),
    ]
    problems = [
        f"  {method}({params}): budget {call_timeout(method, params)}s <= addon {deadline}s"
        for method, params, deadline in cases
        if call_timeout(method, params) <= deadline
    ]
    assert not problems, "Server gives up before Godot answers:\n" + "\n".join(problems)


def test_bad_values_never_shrink_the_budget() -> None:
    for method, params in [
        ("move_to", {"timeout": -100}),
        ("watch_signals", {"duration_ms": "abc"}),
        ("simulate_key", {"hold_sec": None}),
        ("run_test_scenario", {"steps": "not a list"}),
        ("run_headless_scene", {"timeout_sec": True}),
        ("get_scene_tree", None),
    ]:
        assert call_timeout(method, params) >= DEFAULT_CALL_TIMEOUT, (method, params)


if __name__ == "__main__":
    failures = 0
    for check in (
        test_tools_take_timeouts_from_call_timeout,
        test_budgets_outlast_addon_deadlines,
        test_bad_values_never_shrink_the_budget,
    ):
        try:
            check()
            print(f"PASS  {check.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {check.__name__}\n{exc}")
    sys.exit(1 if failures else 0)
