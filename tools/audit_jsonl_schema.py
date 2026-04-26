#!/usr/bin/env python3
"""
Audit JSONL schemas under a directory and write machine/human-readable reports.

The script is intentionally conservative:
- It reports field names seen in files instead of assigning business meaning.
- Samples are masked and truncated before being written to reports.
- Distribution counters are capped to avoid large memory use.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


PHONE_RE = re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")
ID_RE = re.compile(r"(?<!\d)(?:\d{17}[\dXx]|\d{15})(?!\d)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
NAME_FIELD_RE = re.compile(r"(姓名|联系人|收货人|骑手姓名|用户姓名)([:：=]\s*)([\u4e00-\u9fffA-Za-z·]{1,12})")
NAME_SUFFIX_RE = re.compile(r"([\u4e00-\u9fff]{1,4})(先生|女士|小姐|师傅|同学)")
ADDRESS_FIELD_RE = re.compile(
    r"(地址|收货地址|配送地址|详细地址|门牌号)([:：=]\s*)([^,，。；;\n]{4,120})"
)
ADDRESS_HINT_RE = re.compile(
    r"[\u4e00-\u9fff]{2,30}(省|市|区|县|镇|乡|街道|路|街|巷|号楼|栋|单元|室)[^,，。；;\n]{0,80}"
)

MAX_SAMPLE_CHARS = 900
MAX_COUNTER_KEYS = 5000


def mask_text(text: str) -> str:
    text = PHONE_RE.sub("1**********", text)
    text = ID_RE.sub("[身份证已脱敏]", text)
    text = EMAIL_RE.sub("[邮箱已脱敏]", text)
    text = NAME_FIELD_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}某某", text)
    text = NAME_SUFFIX_RE.sub(lambda m: f"某{m.group(2)}", text)
    text = ADDRESS_FIELD_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}[地址已脱敏]", text)
    text = ADDRESS_HINT_RE.sub("[地址已脱敏]", text)
    return text


def mask_value(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return "[TRUNCATED]"
    if isinstance(value, str):
        masked = mask_text(value)
        if len(masked) > MAX_SAMPLE_CHARS:
            return masked[:MAX_SAMPLE_CHARS] + "...[截断]"
        return masked
    if isinstance(value, dict):
        return {str(k): mask_value(v, depth + 1) for k, v in list(value.items())[:80]}
    if isinstance(value, list):
        return [mask_value(v, depth + 1) for v in value[:20]]
    return value


def safe_json_loads(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.startswith("```json"):
        text = text[7:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    try:
        return json.loads(text)
    except Exception:
        try:
            return ast.literal_eval(text)
        except Exception:
            return None


def stringify_for_counter(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    text = mask_text(text).replace("\n", "\\n")
    if len(text) > 220:
        text = text[:220] + "...[截断]"
    return text


def update_counter(counter: Counter, value: Any) -> None:
    if len(counter) < MAX_COUNTER_KEYS or stringify_for_counter(value) in counter:
        counter[stringify_for_counter(value)] += 1


def get_nested(data: dict[str, Any], path: str) -> Any:
    cur: Any = data
    for part in path.split("."):
        if isinstance(cur, str):
            cur = safe_json_loads(cur)
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def iter_jsonl_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.jsonl")):
        if path.is_file():
            yield path


def signal_text_candidates(data: dict[str, Any]) -> list[tuple[str, Any]]:
    candidates: list[tuple[str, Any]] = []
    for key, value in data.items():
        key_lower = str(key).lower()
        if "signal" in key_lower or "信号" in str(key):
            candidates.append((str(key), value))
        if key_lower in {"input", "prompt", "input_prompt"}:
            candidates.append((str(key), value))
    return candidates


def assess_signal_candidate(name: str, value: Any) -> dict[str, Any]:
    result = {
        "source": name,
        "type": type(value).__name__,
        "structured": False,
        "reason": "",
        "extracted_count": 0,
    }
    if isinstance(value, dict):
        result["structured"] = True
        result["extracted_count"] = len(value)
        return result
    if isinstance(value, list):
        result["structured"] = True
        result["extracted_count"] = len(value)
        return result
    parsed = safe_json_loads(value)
    if isinstance(parsed, (dict, list)):
        result["structured"] = True
        result["type"] = f"{type(value).__name__}->parsed_{type(parsed).__name__}"
        result["extracted_count"] = len(parsed)
        return result
    if isinstance(value, str):
        brace_signals = re.findall(r"\{[^{}]{1,300}:[^{}]{1,500}\}", value)
        if brace_signals:
            result["reason"] = "text contains {key:value}-like fragments; not JSON/dict structured"
            result["extracted_count"] = len(brace_signals)
        elif "系统信号" in value or "signal" in value.lower():
            result["reason"] = "signal appears in free text, but no parseable dict/list or {key:value} fragments found"
        else:
            result["reason"] = "no signal marker found in text"
    else:
        result["reason"] = "not dict/list/string"
    return result


def audit_file(path: Path, root: Path) -> dict[str, Any]:
    total = 0
    parsed_count = 0
    failed_count = 0
    parse_errors: Counter[str] = Counter()
    field_counts: Counter[str] = Counter()
    field_types: dict[str, Counter[str]] = defaultdict(Counter)
    samples: list[dict[str, Any]] = []
    top_fields: set[str] = set()

    session_values: list[str] = []
    session_exact_exists = False
    session_candidate: str | None = None

    distributions: dict[str, Counter[str]] = {
        "scene_like": Counter(),
        "label_like": Counter(),
        "ResponseSolution": Counter(),
        "DialogueAgreeSolution": Counter(),
        "model_name": Counter(),
    }
    signal_assessments: list[dict[str, Any]] = []
    signal_seen_summary: Counter[str] = Counter()

    scene_keys = {"scene", "场景", "问题场景"}
    label_keys = {"label", "标签", "标注", "label_type"}
    model_keys = {"model_name", "模型名称", "modelName"}
    session_keys = ["session_id", "sessionId", "sessionID", "session"]

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            total += 1
            text = line.strip()
            if not text:
                failed_count += 1
                parse_errors["empty line"] += 1
                continue
            try:
                data = json.loads(text)
            except Exception as exc:
                failed_count += 1
                parse_errors[type(exc).__name__] += 1
                continue
            if not isinstance(data, dict):
                failed_count += 1
                parse_errors[f"top-level {type(data).__name__}"] += 1
                continue

            parsed_count += 1
            top_fields.update(str(k) for k in data.keys())
            for key, value in data.items():
                key_s = str(key)
                field_counts[key_s] += 1
                field_types[key_s][type(value).__name__] += 1
                if key_s in scene_keys:
                    update_counter(distributions["scene_like"], value)
                if key_s in label_keys:
                    update_counter(distributions["label_like"], value)
                if key_s in model_keys:
                    update_counter(distributions["model_name"], value)

            if "session_id" in data:
                session_exact_exists = True
            if session_candidate is None:
                for key in session_keys:
                    if key in data:
                        session_candidate = key
                        break
            if session_candidate and session_candidate in data:
                session_values.append(stringify_for_counter(data.get(session_candidate)))

            for path_name in (
                "ResponseSolution",
                "response_solution",
                "target.ResponseSolution",
                "target.response_solution",
            ):
                value = get_nested(data, path_name) if "." in path_name else data.get(path_name)
                if value not in (None, ""):
                    update_counter(distributions["ResponseSolution"], value)

            for path_name in ("DialogueAgreeSolution", "target.DialogueAgreeSolution"):
                value = get_nested(data, path_name) if "." in path_name else data.get(path_name)
                if value not in (None, ""):
                    update_counter(distributions["DialogueAgreeSolution"], value)

            if len(signal_assessments) < 20:
                for source, value in signal_text_candidates(data):
                    assessment = assess_signal_candidate(source, value)
                    signal_assessments.append(assessment)
                    signal_seen_summary[assessment["reason"] or "structured"] += 1

            if len(samples) < 3:
                samples.append(
                    {
                        "line": line_num,
                        "data": mask_value(data),
                    }
                )

    session_stats: dict[str, Any] = {
        "session_id_exists": session_exact_exists,
        "session_field_used_for_stats": session_candidate,
        "unique_session_count": None,
        "duplicate_session_count": None,
        "max_duplicate_count": None,
    }
    if session_candidate:
        counter = Counter(session_values)
        session_stats.update(
            {
                "unique_session_count": len(counter),
                "duplicate_session_count": sum(1 for c in counter.values() if c > 1),
                "max_duplicate_count": max(counter.values()) if counter else 0,
                "top_duplicates": counter.most_common(10),
            }
        )

    fields = {}
    for field in sorted(top_fields):
        count = field_counts[field]
        missing = parsed_count - count
        fields[field] = {
            "count": count,
            "missing_count": missing,
            "missing_rate": (missing / parsed_count) if parsed_count else None,
            "types": dict(field_types[field].most_common()),
        }

    def top(counter: Counter, n: int) -> list[dict[str, Any]]:
        return [{"value": k, "count": v} for k, v in counter.most_common(n)]

    return {
        "file_path": str(path.relative_to(root)),
        "total_lines": total,
        "parsed_lines": parsed_count,
        "failed_lines": failed_count,
        "parse_errors": dict(parse_errors.most_common()),
        "top_level_fields": sorted(top_fields),
        "fields": fields,
        "samples": samples,
        "session": session_stats,
        "distributions": {
            "scene_or_场景_top30": top(distributions["scene_like"], 30),
            "label_or_标签_top30": top(distributions["label_like"], 30),
            "ResponseSolution_top50": top(distributions["ResponseSolution"], 50),
            "DialogueAgreeSolution_top50": top(distributions["DialogueAgreeSolution"], 50),
            "model_name_or_模型名称_top30": top(distributions["model_name"], 30),
        },
        "signals": {
            "candidate_assessments_sample": signal_assessments[:10],
            "assessment_summary": dict(signal_seen_summary.most_common()),
        },
    }


def write_json_report(results: dict[str, Any], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown_report(results: dict[str, Any], output_file: Path) -> None:
    lines: list[str] = []
    lines.append("# JSONL Schema Audit\n")
    lines.append(f"- Root: `{results['root']}`")
    lines.append(f"- Files scanned: {len(results['files'])}")
    lines.append(f"- Total lines: {results['summary']['total_lines']}")
    lines.append(f"- Parsed lines: {results['summary']['parsed_lines']}")
    lines.append(f"- Failed lines: {results['summary']['failed_lines']}\n")

    for item in results["files"]:
        lines.append(f"## {item['file_path']}\n")
        lines.append(f"- Total lines: {item['total_lines']}")
        lines.append(f"- Parsed lines: {item['parsed_lines']}")
        lines.append(f"- Failed lines: {item['failed_lines']}")
        if item["parse_errors"]:
            lines.append(f"- Parse errors: `{json.dumps(item['parse_errors'], ensure_ascii=False)}`")
        lines.append(f"- Top-level fields: `{', '.join(item['top_level_fields'])}`")
        session = item["session"]
        lines.append(f"- Exact `session_id` exists: {session['session_id_exists']}")
        lines.append(f"- Session field used for stats: `{session['session_field_used_for_stats']}`")
        if session["session_field_used_for_stats"]:
            lines.append(f"- Unique sessions: {session['unique_session_count']}")
            lines.append(f"- Sessions with duplicates: {session['duplicate_session_count']}")
            lines.append(f"- Max duplicate count: {session['max_duplicate_count']}")
            if session.get("top_duplicates"):
                dup_text = ", ".join(f"{sid}({cnt})" for sid, cnt in session["top_duplicates"][:5])
                lines.append(f"- Top duplicate sessions: {dup_text}")

        lines.append("\n### Field Presence\n")
        lines.append("| Field | Count | Missing Rate | Types |")
        lines.append("|---|---:|---:|---|")
        for field, info in item["fields"].items():
            miss = "" if info["missing_rate"] is None else f"{info['missing_rate']:.2%}"
            lines.append(
                f"| `{field}` | {info['count']} | {miss} | `{json.dumps(info['types'], ensure_ascii=False)}` |"
            )

        dist_names = [
            ("scene_or_场景_top30", "Scene/场景 Top 30"),
            ("label_or_标签_top30", "Label/标签 Top 30"),
            ("ResponseSolution_top50", "ResponseSolution Top 50"),
            ("DialogueAgreeSolution_top50", "DialogueAgreeSolution Top 50"),
            ("model_name_or_模型名称_top30", "Model Name Top 30"),
        ]
        for key, title in dist_names:
            values = item["distributions"].get(key, [])
            if not values:
                continue
            lines.append(f"\n### {title}\n")
            lines.append("| Value | Count |")
            lines.append("|---|---:|")
            for row in values:
                lines.append(f"| `{row['value']}` | {row['count']} |")

        lines.append("\n### Signal Structure Assessment\n")
        summary = item["signals"].get("assessment_summary", {})
        lines.append(f"- Summary: `{json.dumps(summary, ensure_ascii=False)}`")
        for assessment in item["signals"].get("candidate_assessments_sample", [])[:5]:
            lines.append(
                f"- `{assessment['source']}`: structured={assessment['structured']}, "
                f"type={assessment['type']}, extracted_count={assessment['extracted_count']}, "
                f"reason={assessment['reason'] or 'structured'}"
            )

        lines.append("\n### Masked Samples\n")
        for sample in item["samples"]:
            lines.append(f"Line {sample['line']}:")
            lines.append("```json")
            lines.append(json.dumps(sample["data"], ensure_ascii=False, indent=2))
            lines.append("```")
        lines.append("")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit JSONL schema recursively.")
    parser.add_argument("root", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("--json-output", default="analysis_outputs/data_audit.json")
    parser.add_argument("--md-output", default="analysis_outputs/data_audit_report.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = [audit_file(path, root) for path in iter_jsonl_files(root)]
    summary = {
        "total_lines": sum(item["total_lines"] for item in files),
        "parsed_lines": sum(item["parsed_lines"] for item in files),
        "failed_lines": sum(item["failed_lines"] for item in files),
    }
    results = {"root": str(root), "summary": summary, "files": files}

    write_json_report(results, Path(args.json_output))
    write_markdown_report(results, Path(args.md_output))
    print(f"Wrote {args.json_output}")
    print(f"Wrote {args.md_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
