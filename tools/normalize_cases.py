#!/usr/bin/env python3
"""
Build a conservative, sample-sized CaseRecord JSONL from available JSONL files.

This is a draft normalizer for audit purposes. It avoids inventing fields:
- turn_index is only filled from explicit turn/round fields.
- signals and available_solutions are retained only when already structured.
- prompt-embedded signals/tools are reported but not parsed into structures.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PHONE_RE = re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")
ID_RE = re.compile(r"(?<!\d)(?:\d{17}[\dXx]|\d{15})(?!\d)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
NAME_FIELD_RE = re.compile(r"(姓名|联系人|收货人|骑手姓名|用户姓名)([:：=]\s*)([\u4e00-\u9fffA-Za-z·]{1,12})")
NAME_SUFFIX_RE = re.compile(r"([\u4e00-\u9fff]{1,4})(先生|女士|小姐|师傅|同学)")
ADDRESS_FIELD_RE = re.compile(r"(地址|收货地址|配送地址|详细地址|门牌号)([:：=]\s*)([^,，。；;\n]{4,120})")
ADDRESS_HINT_RE = re.compile(r"[\u4e00-\u9fff]{2,30}(省|市|区|县|镇|乡|街道|路|街|巷|号楼|栋|单元|室)[^,，。；;\n]{0,80}")


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
    if depth > 6:
        return "[TRUNCATED]"
    if isinstance(value, str):
        return mask_text(value)
    if isinstance(value, dict):
        return {str(k): mask_value(v, depth + 1) for k, v in value.items()}
    if isinstance(value, list):
        return [mask_value(v, depth + 1) for v in value]
    return value


def safe_parse_jsonish(value: Any) -> Any:
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


def get_first(data: dict[str, Any], paths: list[str]) -> Any:
    for path in paths:
        cur: Any = data
        found = True
        for part in path.split("."):
            if isinstance(cur, str):
                cur = safe_parse_jsonish(cur)
            if not isinstance(cur, dict) or part not in cur:
                found = False
                break
            cur = cur[part]
        if found and cur not in (None, ""):
            return cur
    return None


def parse_target(data: dict[str, Any]) -> dict[str, Any]:
    target = data.get("target")
    parsed = safe_parse_jsonish(target)
    if isinstance(parsed, dict):
        return parsed
    return {}


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def extract_dialogue_history(input_text: str) -> tuple[str, str]:
    if not input_text:
        return "", ""

    history = ""
    patterns = [
        r"## 你与用户的对话历史\n(.*?)(?:\nThinking|\nAssistant:|\n## |\Z)",
        r"\[历史对话上下文\]\n(.*?)(?:\n\n\[当前客服回复\]|\Z)",
        r"【context】\n(.*?)(?:\n\n【reply】|\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, input_text, re.DOTALL)
        if match:
            history = match.group(1).strip()
            break

    if not history:
        lines = []
        for line in input_text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("User:", "用户:", "用户：", "Assistant:", "客服:", "客服：")):
                lines.append(stripped)
        history = "\n".join(lines)

    user_query = ""
    for line in history.splitlines():
        stripped = line.strip()
        if stripped.startswith(("User:", "用户:", "用户：")):
            if ":" in stripped:
                user_query = stripped.split(":", 1)[1].strip()
            elif "：" in stripped:
                user_query = stripped.split("：", 1)[1].strip()
            else:
                user_query = stripped

    return history, user_query


def structured_signals(data: dict[str, Any]) -> tuple[dict[str, Any], str]:
    for key in ("signals", "系统信号", "signal"):
        value = data.get(key)
        if isinstance(value, dict):
            return value, f"direct field `{key}`"
    prompt = as_text(get_first(data, ["input", "prompt", "input_prompt"]))
    if "系统信号" in prompt or re.search(r"\{[^{}]{1,120}:[^{}]{1,240}\}", prompt):
        return {}, "signals appear in prompt text; not parsed"
    return {}, "not found"


def structured_available_solutions(data: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    for key in ("available_solutions", "solutions", "tools", "方案列表"):
        value = data.get(key)
        if isinstance(value, list):
            normalized = []
            for item in value:
                if isinstance(item, dict):
                    normalized.append(
                        {
                            "name": item.get("name") or item.get("名称") or "",
                            "description": item.get("description") or item.get("描述") or "",
                        }
                    )
                else:
                    normalized.append({"name": as_text(item), "description": ""})
            return normalized, f"direct list field `{key}`"
    prompt = as_text(get_first(data, ["input", "prompt", "input_prompt"]))
    if "方案列表" in prompt:
        return [], "available solutions appear in prompt text; not parsed"
    return [], "not found"


def explicit_turn_index(data: dict[str, Any]) -> Any:
    value = get_first(data, ["turn_index", "turnIndex", "turn_id", "round_index", "轮次"])
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return value


def build_sample_id(
    data: dict[str, Any],
    source_file: str,
    source_line: int,
    session_id: str,
    user_query: str,
    response: str,
    response_solution: str,
) -> tuple[str, str]:
    explicit = get_first(data, ["request_id", "trace_id", "turn_id", "requestId", "traceId", "turnId", "metadata.request_id", "metadata.trace_id", "metadata.turn_id"])
    if explicit not in (None, ""):
        return str(explicit), "explicit_id"
    base = f"{source_file}\t{source_line}\t{session_id}\t{user_query}\t{response}\t{response_solution}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest(), "sha1"


def normalize_record(data: dict[str, Any], source_file: str, source_line: int) -> tuple[dict[str, Any], dict[str, str]]:
    target = parse_target(data)
    input_text = as_text(get_first(data, ["input", "input_prompt", "prompt"]))
    dialogue_history = as_text(get_first(data, ["dialogue_history", "context", "history"]))
    parsed_history, parsed_user_query = extract_dialogue_history(input_text)
    if not dialogue_history:
        dialogue_history = parsed_history

    user_query = as_text(get_first(data, ["user_query", "query", "question", "user_reply"]))
    if not user_query:
        user_query = parsed_user_query

    response = as_text(get_first(data, ["response", "Response"]))
    if not response:
        response = as_text(target.get("Response") or target.get("response"))

    response_solution = as_text(get_first(data, ["response_solution", "ResponseSolution"]))
    if not response_solution:
        response_solution = as_text(target.get("ResponseSolution") or target.get("response_solution"))

    dialogue_agree_solution = as_text(get_first(data, ["dialogue_agree_solution", "DialogueAgreeSolution"]))
    if not dialogue_agree_solution:
        dialogue_agree_solution = as_text(target.get("DialogueAgreeSolution") or target.get("dialogue_agree_solution"))

    session_id = as_text(get_first(data, ["session_id", "sessionId", "sessionID", "session"]))
    model_name = as_text(get_first(data, ["model_name", "modelName", "模型名称", "metadata.model_name"]))
    scene = as_text(get_first(data, ["scene", "场景", "问题场景"]))
    signals, signals_note = structured_signals(data)
    available_solutions, solutions_note = structured_available_solutions(data)
    label = as_text(get_first(data, ["label_type", "label", "标签", "annotation_type", "metadata.annotation_type"]))
    label_type = label if label in {"unknown", "good", "bad", "human_annotated"} else "unknown"

    sample_id, sample_id_source = build_sample_id(
        data, source_file, source_line, session_id, user_query, response, response_solution
    )

    record = {
        "sample_id": sample_id,
        "source_file": source_file,
        "source_line": source_line,
        "session_id": session_id,
        "turn_index": explicit_turn_index(data),
        "model_name": model_name,
        "scene": scene,
        "user_query": mask_text(user_query),
        "dialogue_history": mask_text(dialogue_history),
        "signals": mask_value(signals),
        "available_solutions": mask_value(available_solutions),
        "response": mask_text(response),
        "response_solution": mask_text(response_solution),
        "dialogue_agree_solution": mask_text(dialogue_agree_solution),
        "label_type": label_type,
        "raw": mask_value(data),
    }
    notes = {
        "sample_id_source": sample_id_source,
        "signals_note": signals_note,
        "available_solutions_note": solutions_note,
    }
    return record, notes


def iter_input_files(root_file: Path, sample_outputs_dir: Path) -> list[Path]:
    files = []
    if root_file.exists():
        files.append(root_file)
    if sample_outputs_dir.exists():
        for path in sorted(sample_outputs_dir.glob("*.jsonl")):
            if path.is_file() and path not in files:
                files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a CaseRecord sample JSONL.")
    parser.add_argument("--root-jsonl", default="xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl")
    parser.add_argument("--pipeline-dir", default="analysis_outputs/pipeline_sample_outputs")
    parser.add_argument("--output", default="analysis_outputs/normalized_cases_sample.jsonl")
    parser.add_argument("--report", default="analysis_outputs/normalized_schema_report.md")
    parser.add_argument("--max-per-file", type=int, default=50)
    parser.add_argument("--max-total", type=int, default=200)
    args = parser.parse_args()

    files = iter_input_files(Path(args.root_jsonl), Path(args.pipeline_dir))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    per_file_stats: dict[str, Counter] = defaultdict(Counter)
    notes_counter: Counter[str] = Counter()
    sample_id_sources: Counter[str] = Counter()

    for path in files:
        rel = str(path)
        taken = 0
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                if taken >= args.max_per_file or len(records) >= args.max_total:
                    break
                text = line.strip()
                if not text:
                    per_file_stats[rel]["empty_lines"] += 1
                    continue
                try:
                    data = json.loads(text)
                except Exception:
                    per_file_stats[rel]["parse_failed"] += 1
                    continue
                if not isinstance(data, dict):
                    per_file_stats[rel]["non_object"] += 1
                    continue
                record, notes = normalize_record(data, rel, line_num)
                records.append(record)
                taken += 1
                per_file_stats[rel]["normalized"] += 1
                for key, value in notes.items():
                    notes_counter[f"{key}: {value}"] += 1
                sample_id_sources[notes["sample_id_source"]] += 1
        per_file_stats[rel]["sample_limit"] = args.max_per_file

    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    report_lines = [
        "# Normalized CaseRecord Draft Report",
        "",
        f"- Output: `{args.output}`",
        f"- Records written: {len(records)}",
        f"- Max per file: {args.max_per_file}",
        f"- Max total: {args.max_total}",
        "- Text fields and `raw` are PII-masked in this sample output.",
        "",
        "## Input Files",
        "",
        "| File | Normalized | Parse Failed | Notes |",
        "|---|---:|---:|---|",
    ]
    for path in files:
        rel = str(path)
        stats = per_file_stats[rel]
        report_lines.append(
            f"| `{rel}` | {stats.get('normalized', 0)} | {stats.get('parse_failed', 0)} | sample_limit={stats.get('sample_limit', args.max_per_file)} |"
        )

    report_lines.extend(
        [
            "",
            "## Mapping Notes",
            "",
            "- `sample_id`: uses explicit `request_id` / `trace_id` / `turn_id` only when present; otherwise SHA1 of source_file, source_line, session_id, user_query, response, and response_solution.",
            "- `turn_index`: only filled from explicit turn/round fields; no inferred order was generated.",
            "- `signals`: direct structured dict fields are retained. Prompt-embedded signal text is not parsed.",
            "- `available_solutions`: direct structured list fields are retained. Prompt-embedded方案列表 is not parsed.",
            "- `label_type`: only normalized when the source already has one of `unknown/good/bad/human_annotated`; otherwise `unknown`.",
            "",
            "## Counters",
            "",
            f"- sample_id sources: `{json.dumps(dict(sample_id_sources), ensure_ascii=False)}`",
            "",
            "### Notes",
            "",
        ]
    )
    for note, count in notes_counter.most_common():
        report_lines.append(f"- {note}: {count}")

    report_lines.extend(["", "## Output Fields", ""])
    if records:
        for key in records[0].keys():
            present = sum(1 for rec in records if rec.get(key) not in (None, "", [], {}))
            report_lines.append(f"- `{key}`: populated in {present}/{len(records)} records")

    Path(args.report).write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
