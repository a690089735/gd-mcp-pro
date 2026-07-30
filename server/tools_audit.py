"""Generate a full three-way tool audit table: GDScript <-> Python <-> compact mode.

Usage:
    python server/tools_audit.py            # print summary
    python server/tools_audit.py --md OUT   # write markdown report

For every GDScript command this reports:
  * the keys the GDScript handler reads, split into required / optional
  * the keys the full-mode Python tool actually sends (plus its signature)
  * the keys the compact-mode docstring advertises for the matching action
and flags every discrepancy.
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parent
TOOLS_DIR = SERVER_ROOT / "src" / "godot_mcp_pro" / "tools"
COMMANDS_DIR = SERVER_ROOT.parent / "addons" / "godot_mcp" / "commands"
COMPACT_FILE = TOOLS_DIR / "compact.py"

SKIP_MODULES = {"__init__.py", "compact.py"}

REQUIRED_PATTERN = r'require_\w+\(\s*params\s*,\s*"([a-z0-9_]+)"'
OPTIONAL_PATTERNS = (
    r'optional_\w+\(\s*params\s*,\s*"([a-z0-9_]+)"',
    r'params\.has\(\s*"([a-z0-9_]+)"\s*\)',
    r'params\.get\(\s*"([a-z0-9_]+)"',
    r'params\[\s*"([a-z0-9_]+)"\s*\]',
)


# ---------------------------------------------------------------- GDScript side
def _split_gd_functions(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    parts = re.split(r"\nfunc ([A-Za-z0-9_]+)\(", text)
    for i in range(1, len(parts), 2):
        out[parts[i]] = parts[i + 1]
    return out


def collect_gdscript() -> dict[str, dict[str, object]]:
    """command -> {file, func, required:set, optional:set}"""
    base_funcs = _split_gd_functions(
        (COMMANDS_DIR / "base_command.gd").read_text(encoding="utf-8")
    )

    result: dict[str, dict[str, object]] = {}
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

        def collect(func_name: str, seen: set[str]) -> tuple[set[str], set[str]]:
            if func_name in seen or func_name not in all_funcs:
                return set(), set()
            seen.add(func_name)
            body = all_funcs[func_name]
            required = set(re.findall(REQUIRED_PATTERN, body))
            optional: set[str] = set()
            for pattern in OPTIONAL_PATTERNS:
                optional |= set(re.findall(pattern, body))
            forwarded = re.findall(
                r"\b([A-Za-z0-9_]+)\(\s*[A-Za-z0-9_.]*\s*,?\s*params\s*[,)]", body
            ) + re.findall(r"\b([A-Za-z0-9_]+)\(\s*params\s*[,)]", body)
            for helper in forwarded:
                r2, o2 = collect(helper, seen)
                required |= r2
                optional |= o2
            return required, optional

        for cmd, func in command_map.items():
            required, optional = collect(func, set())
            result[cmd] = {
                "file": gd_file.name,
                "func": func,
                "required": required,
                "optional": optional - required,
            }
    return result


# ------------------------------------------------------------------ Python side
def _sig_names(func: ast.AsyncFunctionDef | ast.FunctionDef) -> list[str]:
    args = func.args
    names = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs]
    return [n for n in names if n != "self"]


def _own_nodes(func: ast.AST):
    """Walk a function body without descending into nested function definitions."""
    stack = list(ast.iter_child_nodes(func))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)):
            continue
        yield node
        stack.extend(ast.iter_child_nodes(node))


def _iter_functions(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            yield node


def collect_python() -> dict[str, dict[str, object]]:
    """command -> {module, tool, signature:list, sent:set, dynamic:bool}"""
    result: dict[str, dict[str, object]] = {}

    for py_file in sorted(TOOLS_DIR.glob("*.py")):
        if py_file.name in SKIP_MODULES:
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for func in _iter_functions(tree):
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
                entry = result.setdefault(
                    command,
                    {
                        "module": py_file.name,
                        "tool": func.name,
                        "signature": _sig_names(func),
                        "sent": set(),
                        "dynamic": False,
                    },
                )
                if len(node.args) < 2:
                    continue
                payload = node.args[1]
                if isinstance(payload, ast.Dict):
                    for key in payload.keys:
                        if isinstance(key, ast.Constant):
                            entry["sent"].add(key.value)  # type: ignore[union-attr]
                        else:
                            entry["dynamic"] = True
                else:
                    entry["dynamic"] = True
    return result


# ----------------------------------------------------------------- compact side
def collect_compact() -> dict[str, dict[str, object]]:
    """command -> {tool, action, doc_params:set}"""
    tree = ast.parse(COMPACT_FILE.read_text(encoding="utf-8"))
    result: dict[str, dict[str, object]] = {}

    for func in ast.walk(tree):
        if not isinstance(func, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        action_map: dict[str, str] = {}
        for node in ast.walk(func):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if (
                        isinstance(tgt, ast.Name)
                        and tgt.id == "ACTION_MAP"
                        and isinstance(node.value, ast.Dict)
                    ):
                        for k, v in zip(node.value.keys, node.value.values):
                            if isinstance(k, ast.Constant) and isinstance(
                                v, ast.Constant
                            ):
                                action_map[k.value] = v.value
        if not action_map:
            continue
        doc = ast.get_docstring(func) or ""
        # Actions are documented as "- action_name: description (params...)"
        blocks: dict[str, str] = {}
        current: str | None = None
        for line in doc.splitlines():
            head = re.match(r"\s*-\s*([a-z0-9_]+):\s*(.*)", line)
            if head and head.group(1) in action_map:
                current = head.group(1)
                blocks[current] = head.group(2)
            elif current:
                blocks[current] += " " + line.strip()

        for action, command in action_map.items():
            text = blocks.get(action, "")
            doc_params = set(re.findall(r"([a-z0-9_]+)\s*:\s*(?:str|int|float|bool|list|dict|any)", text))
            doc_params |= set(re.findall(r"flat keys:\s*([^()\[\]]*)", text) and re.findall(r"[a-z0-9_]+(?=\s*[,)])", " ".join(re.findall(r"flat keys:\s*([^()\[\]]*)", text))) or [])
            result[command] = {
                "tool": func.name,
                "action": action,
                "doc_params": doc_params,
                "doc": text.strip(),
            }
    return result


# ----------------------------------------------------------------------- report
def build_report() -> tuple[list[dict[str, object]], dict[str, int]]:
    gd = collect_gdscript()
    py = collect_python()
    compact = collect_compact()

    rows: list[dict[str, object]] = []
    stats = {
        "commands": len(gd),
        "py_missing_tool": 0,
        "compact_missing": 0,
        "required_not_sent": 0,
        "dead": 0,
        "missing_optional": 0,
        "doc_gap": 0,
    }

    for command in sorted(gd):
        info = gd[command]
        required: set[str] = info["required"]  # type: ignore[assignment]
        optional: set[str] = info["optional"]  # type: ignore[assignment]
        pentry = py.get(command)
        centry = compact.get(command)

        issues: list[str] = []
        if pentry is None:
            issues.append("NO_PYTHON_TOOL")
            stats["py_missing_tool"] += 1
            sent: set[str] = set()
            dynamic = False
        else:
            sent = pentry["sent"]  # type: ignore[assignment]
            dynamic = bool(pentry["dynamic"])
            if not dynamic:
                not_sent = required - sent
                if not_sent:
                    issues.append(f"REQUIRED_NOT_SENT:{sorted(not_sent)}")
                    stats["required_not_sent"] += 1
                missing_opt = optional - sent
                if missing_opt:
                    issues.append(f"MISSING_OPTIONAL:{sorted(missing_opt)}")
                    stats["missing_optional"] += 1
            dead = sent - required - optional
            if dead:
                issues.append(f"DEAD:{sorted(dead)}")
                stats["dead"] += 1

        if centry is None:
            issues.append("NO_COMPACT_ACTION")
            stats["compact_missing"] += 1
            doc_params: set[str] = set()
        else:
            doc_params = centry["doc_params"]  # type: ignore[assignment]
            doc_gap = required - doc_params
            if doc_gap:
                issues.append(f"COMPACT_DOC_GAP:{sorted(doc_gap)}")
                stats["doc_gap"] += 1

        rows.append(
            {
                "command": command,
                "gd_file": info["file"],
                "required": sorted(required),
                "optional": sorted(optional),
                "py_module": pentry["module"] if pentry else "",
                "py_tool": pentry["tool"] if pentry else "",
                "py_signature": pentry["signature"] if pentry else [],
                "sent": sorted(sent),
                "dynamic": dynamic,
                "compact_tool": centry["tool"] if centry else "",
                "compact_action": centry["action"] if centry else "",
                "doc_params": sorted(doc_params),
                "issues": issues,
            }
        )

    extra = sorted(set(py) - set(gd))
    if extra:
        stats["python_orphans"] = len(extra)
    return rows, stats


def write_markdown(rows: list[dict[str, object]], stats: dict[str, int], out: Path):
    lines: list[str] = []
    lines.append("# 工具全量三方对照审计")
    lines.append("")
    lines.append("由 `server/tools_audit.py` 自动生成。")
    lines.append("")
    lines.append("## 汇总")
    lines.append("")
    for key, value in stats.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    flagged = [r for r in rows if r["issues"]]
    lines.append(f"## 待处理项（{len(flagged)}）")
    lines.append("")
    if flagged:
        lines.append("| 命令 | 问题 |")
        lines.append("|---|---|")
        for r in flagged:
            lines.append(f"| `{r['command']}` | {'<br>'.join(r['issues'])} |")  # type: ignore[arg-type]
    else:
        lines.append("无。")
    lines.append("")

    lines.append("## 全量对照表")
    lines.append("")
    lines.append("| # | 命令 | GD 文件 | 必填 | 可选 | Python 工具 | 紧凑模式 | 状态 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        req = ", ".join(r["required"]) or "-"  # type: ignore[arg-type]
        opt = ", ".join(r["optional"]) or "-"  # type: ignore[arg-type]
        pytool = f"{r['py_tool']}" if r["py_tool"] else "**缺失**"
        cm = (
            f"{r['compact_tool']}.{r['compact_action']}"
            if r["compact_tool"]
            else "**缺失**"
        )
        status = "OK" if not r["issues"] else "⚠"
        lines.append(
            f"| {i} | `{r['command']}` | {r['gd_file']} | {req} | {opt} | "
            f"`{pytool}` | `{cm}` | {status} |"
        )
    lines.append("")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", type=Path, default=None)
    args = parser.parse_args()

    rows, stats = build_report()
    for key, value in stats.items():
        print(f"{key}: {value}")
    flagged = [r for r in rows if r["issues"]]
    print(f"flagged rows: {len(flagged)}")
    for r in flagged:
        print(f"  {r['command']}: {'; '.join(r['issues'])}")  # type: ignore[arg-type]

    if args.md:
        write_markdown(rows, stats, args.md)
        print(f"\nwrote {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())