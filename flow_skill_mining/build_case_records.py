#!/usr/bin/env python3
"""Build normalized CaseRecord JSONL from trainer goodcase data."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import (
    DATA_FILE,
    OUT_DIR,
    REPORT_DIR,
    compact_counter,
    ensure_dirs,
    parse_target_json,
    pct,
    scene_parts,
    sha1_text,
    split_components,
    top_counter,
)
from flow_skill_mining.parsers.parse_prompt import parse_all_scene_prompt


CASE_RECORDS_PATH = OUT_DIR / "case_records.jsonl"
REPORT_PATH = REPORT_DIR / "case_record_report.md"


def build_records(input_path: Path = DATA_FILE) -> Iterable[Dict[str, Any]]:
    source_file = str(input_path)
    with input_path.open("r", encoding="utf-8", errors="replace") as f:
        for source_line, line in enumerate(f, 1):
            raw_line = line.rstrip("\n")
            try:
                obj = json.loads(raw_line)
            except Exception as exc:
                # Keep a parse-failed row as a CaseRecord-shaped diagnostic.
                sample_id = sha1_text(f"{source_file}{source_line}{raw_line}")
                yield {
                    "sample_id": sample_id,
                    "source_file": source_file,
                    "source_line": source_line,
                    "session_id": "",
                    "scene_raw": "",
                    "scene": "<MISSING>",
                    "scene_l1": "<MISSING>",
                    "scene_l2": "",
                    "source": "",
                    "current_time": "",
                    "available_solutions": [],
                    "signals": {},
                    "items": [],
                    "selected_item_info": {},
                    "dialogue_history": "",
                    "last_user_query": "",
                    "last_assistant_response": "",
                    "response": "",
                    "response_solution_raw": "无",
                    "response_solution_components": [],
                    "dialogue_agree_solution_raw": "无",
                    "dialogue_agree_solution_components": [],
                    "target_parse_error": f"source json parse error: {exc}",
                    "prompt_parse_errors": ["source json parse failed"],
                    "label_type": "trainer_goodcase",
                }
                continue

            scene_raw, scene, scene_l1, scene_l2 = scene_parts(obj.get("问题场景"))
            parsed_prompt = parse_all_scene_prompt(obj.get("input", ""))
            target_obj, target_error = parse_target_json(obj.get("target", ""))

            response = str(target_obj.get("Response", "")) if target_obj else ""
            response_solution_raw = str(target_obj.get("ResponseSolution", "无")) if target_obj else "无"
            dialogue_agree_solution_raw = (
                str(target_obj.get("DialogueAgreeSolution", "无")) if target_obj else "无"
            )
            session_id = str(obj.get("sessionId", ""))
            sample_id = sha1_text(
                source_file
                + str(source_line)
                + session_id
                + scene
                + parsed_prompt.get("dialogue_history", "")
                + str(obj.get("target", ""))
            )

            yield {
                "sample_id": sample_id,
                "source_file": source_file,
                "source_line": source_line,
                "session_id": session_id,
                "scene_raw": scene_raw,
                "scene": scene,
                "scene_l1": scene_l1,
                "scene_l2": scene_l2,
                "source": obj.get("source", ""),
                "current_time": parsed_prompt.get("current_time", ""),
                "available_solutions": parsed_prompt.get("available_solutions", []),
                "signals": parsed_prompt.get("signals", {}),
                "items": parsed_prompt.get("items", []),
                "selected_item_info": parsed_prompt.get("selected_item_info", {}),
                "dialogue_history": parsed_prompt.get("dialogue_history", ""),
                "last_user_query": parsed_prompt.get("last_user_query", ""),
                "last_assistant_response": parsed_prompt.get("last_assistant_response", ""),
                "response": response,
                "response_solution_raw": response_solution_raw,
                "response_solution_components": split_components(response_solution_raw),
                "dialogue_agree_solution_raw": dialogue_agree_solution_raw,
                "dialogue_agree_solution_components": split_components(dialogue_agree_solution_raw),
                "target_parse_error": target_error,
                "prompt_parse_errors": parsed_prompt.get("parse_errors", []),
                "label_type": "trainer_goodcase",
            }


def write_report(records: List[Dict[str, Any]]) -> None:
    total = len(records)
    target_ok = sum(1 for r in records if not r.get("target_parse_error"))
    prompt_no_errors = sum(1 for r in records if not r.get("prompt_parse_errors"))
    available_nonempty = sum(1 for r in records if r.get("available_solutions"))
    signals_nonempty = sum(1 for r in records if r.get("signals"))
    items_nonempty = sum(1 for r in records if r.get("items"))
    history_nonempty = sum(1 for r in records if r.get("dialogue_history"))
    last_user_nonempty = sum(1 for r in records if r.get("last_user_query"))

    scene_raw_ctr = collections.Counter(r.get("scene_raw", "") for r in records)
    scene_ctr = collections.Counter(r.get("scene", "") for r in records)
    scene_l1_ctr = collections.Counter(r.get("scene_l1", "") for r in records)
    missing_scene = scene_ctr.get("<MISSING>", 0)
    response_raw_ctr = collections.Counter(r.get("response_solution_raw", "") for r in records)
    response_comp_ctr = collections.Counter(
        comp for r in records for comp in r.get("response_solution_components", [])
    )
    agree_raw_ctr = collections.Counter(r.get("dialogue_agree_solution_raw", "") for r in records)
    agree_comp_ctr = collections.Counter(
        comp for r in records for comp in r.get("dialogue_agree_solution_components", [])
    )
    avail_name_ctr = collections.Counter(
        sol.get("name", "")
        for r in records
        for sol in r.get("available_solutions", [])
        if sol.get("name")
    )
    signal_key_ctr = collections.Counter(key for r in records for key in r.get("signals", {}).keys())
    session_ctr = collections.Counter(r.get("session_id", "") for r in records if r.get("session_id"))
    duplicate_sessions = sum(1 for _, count in session_ctr.items() if count > 1)
    max_session_rows = max(session_ctr.values(), default=0)

    summary = {
        "total_rows": total,
        "target_parse_ok": target_ok,
        "prompt_no_error_rows": prompt_no_errors,
        "available_solutions_nonempty": available_nonempty,
        "signals_nonempty": signals_nonempty,
        "items_nonempty": items_nonempty,
        "dialogue_history_nonempty": history_nonempty,
        "last_user_query_nonempty": last_user_nonempty,
        "scene_raw_value_count": len(scene_raw_ctr),
        "scene_value_count": len(scene_ctr),
        "missing_scene": missing_scene,
        "session_count": len(session_ctr),
        "duplicate_session_count": duplicate_sessions,
        "max_session_rows": max_session_rows,
        "scene_l1_distribution": top_counter(scene_l1_ctr, 100),
        "scene_top30": top_counter(scene_ctr, 30),
        "response_solution_raw_top50": top_counter(response_raw_ctr, 50),
        "response_solution_component_top50": top_counter(response_comp_ctr, 50),
        "dialogue_agree_solution_raw_top50": top_counter(agree_raw_ctr, 50),
        "dialogue_agree_solution_component_top50": top_counter(agree_comp_ctr, 50),
        "available_solution_name_top50": top_counter(avail_name_ctr, 50),
        "signals_key_top100": top_counter(signal_key_ctr, 100),
    }
    (REPORT_DIR / "case_record_report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = []
    md.append("# CaseRecord 构建报告")
    md.append("")
    md.append(f"- 总行数: `{total}`")
    md.append(f"- target 成功解析行数: `{target_ok}` ({pct(target_ok, total)})")
    md.append(f"- input prompt 无解析错误行数: `{prompt_no_errors}` ({pct(prompt_no_errors, total)})")
    md.append(f"- available_solutions 非空率: `{available_nonempty}` ({pct(available_nonempty, total)})")
    md.append(f"- signals 非空率: `{signals_nonempty}` ({pct(signals_nonempty, total)})")
    md.append(f"- items 非空率: `{items_nonempty}` ({pct(items_nonempty, total)})")
    md.append(f"- dialogue_history 非空率: `{history_nonempty}` ({pct(history_nonempty, total)})")
    md.append(f"- last_user_query 非空率: `{last_user_nonempty}` ({pct(last_user_nonempty, total)})")
    md.append(f"- scene_raw 取值数: `{len(scene_raw_ctr)}`")
    md.append(f"- scene 去空白后取值数: `{len(scene_ctr)}`")
    md.append(f"- 缺失 scene 数: `{missing_scene}`")
    md.append(f"- session 数: `{len(session_ctr)}`")
    md.append(f"- 重复 session 数: `{duplicate_sessions}`")
    md.append(f"- 最大 session 行数: `{max_session_rows}`")
    md.append("")
    md.append("## 与已知统计对比")
    md.append(f"- 总行数已知约 13,524；本次 `{total}`。")
    md.append(f"- scene 去尾部空白后已知约 54；本次 `{len(scene_ctr)}`。")
    md.append(f"- 缺失 scene 已知约 549；本次 `{missing_scene}`。")
    if total != 13524 or len(scene_ctr) != 54 or missing_scene != 549:
        md.append("- 存在不一致，请检查输入文件版本或 scene 清洗规则。")
    else:
        md.append("- 三项关键统计一致。")
    md.append("")
    md.append("## scene_l1 分布")
    md.append(compact_counter(scene_l1_ctr, 50))
    md.append("")
    md.append("## scene top 30")
    md.append(compact_counter(scene_ctr, 30))
    md.append("")
    md.append("## ResponseSolution raw top 50")
    md.append(compact_counter(response_raw_ctr, 50))
    md.append("")
    md.append("## ResponseSolution component top 50")
    md.append(compact_counter(response_comp_ctr, 50))
    md.append("")
    md.append("## DialogueAgreeSolution raw top 50")
    md.append(compact_counter(agree_raw_ctr, 50))
    md.append("")
    md.append("## DialogueAgreeSolution component top 50")
    md.append(compact_counter(agree_comp_ctr, 50))
    md.append("")
    md.append("## available solution name top 50")
    md.append(compact_counter(avail_name_ctr, 50))
    md.append("")
    md.append("## signals key top 100")
    md.append(compact_counter(signal_key_ctr, 100))
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    records = list(build_records(DATA_FILE))
    CASE_RECORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CASE_RECORDS_PATH.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    write_report(records)
    print(
        json.dumps(
            {
                "case_records": len(records),
                "output": str(CASE_RECORDS_PATH),
                "report": str(REPORT_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
