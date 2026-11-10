"""Python-side wait budget for every GDScript command.

Godot answers most commands within a frame, but some legitimately keep running
for seconds or minutes (headless runs, patch exports, timed key holds, test
scenarios). If the server stops waiting first, the caller gets a timeout while
Godot finishes the work anyway and the result is lost.

This module is the single source of truth for those budgets. Full-mode tools,
compact-mode tools and both `batch_execute` implementations all call
`call_timeout()`, so a long-running command only needs to be added here.
Each budget stays above the deadline the addon itself enforces for that command.
"""

from __future__ import annotations

from typing import Any

DEFAULT_CALL_TIMEOUT = 30.0


def _number(value: Any, default: float) -> float:
    """A JSON number as float; anything else falls back to the command default."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return default
    return float(value)


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _test_scenario_seconds(params: dict[str, Any]) -> float:
    """Worst-case time the addon spends on run_test_scenario's own waits.

    Mirrors test_commands.gd: starting a scene waits 1.5s, input steps may wait
    up to 1s for the input channel, wait steps sleep `seconds` or wait for a node
    (`timeout` + 2s), assert and screenshot steps each allow a 5s game round trip.
    """
    steps = params.get("steps")
    if not isinstance(steps, list):
        return 0.0
    total_seconds = 1.5 if params.get("scene_path") else 0.0
    for step in steps:
        if not isinstance(step, dict):
            continue
        step_type = step.get("type")
        if step_type == "wait":
            if "node_path" in step:
                total_seconds += _number(step.get("timeout"), 5.0) + 2.0
            else:
                total_seconds += max(_number(step.get("seconds"), 1.0), 0.0)
        elif step_type in ("assert", "screenshot"):
            total_seconds += 5.0
        elif step_type == "input":
            total_seconds += 1.5
    return total_seconds


def call_timeout(method: str, params: dict[str, Any] | None) -> float:
    """Seconds the server waits for Godot's answer to `method` called with `params`."""
    params = params or {}
    budget = DEFAULT_CALL_TIMEOUT
    if method in ("run_headless_scene", "run_headless_script"):
        # Godot clamps timeout_sec to 1..900, then needs up to 2s to confirm a kill.
        budget = _clamp(_number(params.get("timeout_sec"), 120.0), 1.0, 900.0) + 30.0
    elif method == "export_patch_pck":
        # Godot clamps timeout_sec to 10..1800 (queueing + export together).
        budget = _clamp(_number(params.get("timeout_sec"), 300.0), 10.0, 1800.0) + 30.0
    elif method == "move_to":
        # Godot waits timeout + 5s on the game IPC channel.
        budget = _number(params.get("timeout"), 15.0) + 10.0
    elif method == "wait_for_node":
        # Godot waits timeout + 2s on the game IPC channel.
        budget = _number(params.get("timeout"), 5.0) + 10.0
    elif method == "watch_signals":
        # Godot waits duration + 5s on the game IPC channel.
        budget = _number(params.get("duration_ms"), 5000.0) / 1000.0 + 15.0
    elif method == "simulate_key":
        hold_seconds = _number(params.get("hold_sec"), 0.0)
        if hold_seconds > 0:
            # Godot waits hold_sec + 30s for the game's release acknowledgement.
            budget = hold_seconds + 40.0
    elif method == "replay_recording":
        # Godot caps the replay wait at 120s.
        budget = 130.0
    elif method == "bake_navigation_mesh":
        budget = 120.0
    elif method == "run_test_scenario":
        budget = _test_scenario_seconds(params) + DEFAULT_CALL_TIMEOUT
    elif method == "run_stress_test":
        # duration is 0..60s; backpressure, the final batch and cancelling it
        # add up to ~15s on the addon side.
        budget = _clamp(_number(params.get("duration"), 5.0), 0.0, 60.0) + DEFAULT_CALL_TIMEOUT
    # Never below the default: a negative or tiny user value must not make the
    # server give up before Godot has even answered.
    return max(budget, DEFAULT_CALL_TIMEOUT)
