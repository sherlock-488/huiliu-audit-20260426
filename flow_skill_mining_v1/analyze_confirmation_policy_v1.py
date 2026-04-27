#!/usr/bin/env python3
"""Recalibrate DialogueAgreeSolution semantics with three confirmation levels."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_mining_v1.common_v1 import (
    V1_OUT,
    V1_REPORTS,
    canonical_components,
    canonicalize_solution,
    dump_json,
    ensure_dirs,
    get_v0_session_trajectories_path,
    has_confirm_expression,
    load_jsonl,
    read_jsonl,
    top_counter,
    user_request_matches_action,
)


REGISTRY = V1_OUT / "solution_registry_v1.json"
OUTPUT = V1_OUT / "confirmation_policy_v1.json"
REPORT = V1_REPORTS / "confirmation_policy_v1_report.md"


def main() -> None:
    ensure_dirs()
    registry = {r["canonical_name"]: r for r in json.loads(REGISTRY.read_text(encoding="utf-8"))}
    stats: Dict[str, Dict[str, Any]] = {}

    def touch(name: str) -> Dict[str, Any]:
        canonical, _, _ = canonicalize_solution(name)
        if canonical not in stats:
            reg = registry.get(canonical, {})
            stats[canonical] = {
                "solution_name": canonical,
                "requires_confirmation_level": reg.get("requires_confirmation_level", "unclear"),
                "response_count": 0,
                "agree_count": 0,
                "agree_rate": 0.0,
                "matched_previous_or_current_or_recent3": 0,
                "matched_user_request_count": 0,
                "unmatched_count": 0,
                "warning_count": 0,
                "evidence_examples": [],
                "notes": [],
                "needs_trainer_confirmation": False,
            }
        return stats[canonical]

    for canonical in registry:
        touch(canonical)

    unmatched_rows = []
    weak_confirm_rows = []
    no_confirm_agree_rows = []
    for row in read_jsonl(get_v0_session_trajectories_path()):
        response_components, _ = canonical_components(row.get("response_solution_raw", "无"))
        agree_components, _ = canonical_components(row.get("dialogue_agree_solution_raw", "无"))
        for comp in response_components:
            touch(comp)["response_count"] += 1
        for comp in agree_components:
            item = touch(comp)
            item["agree_count"] += 1
            match_type = row.get("dialogue_agree_match_type", "")
            matched = match_type in {"previous", "current", "recent3"} or bool(row.get("pending_confirmation_solution"))
            user_match = user_request_matches_action(row.get("last_user_query", ""), item["solution_name"])
            if matched:
                item["matched_previous_or_current_or_recent3"] += 1
            elif user_match:
                item["matched_user_request_count"] += 1
            else:
                item["unmatched_count"] += 1
                unmatched_rows.append(
                    {
                        "sample_id": row.get("sample_id"),
                        "scene": row.get("scene"),
                        "solution": item["solution_name"],
                        "last_user_query": row.get("last_user_query", ""),
                        "match_type": match_type,
                    }
                )
            if item["requires_confirmation_level"] == "strong_confirmation_required" and not has_confirm_expression(row.get("last_user_query", "")):
                item["warning_count"] += 1
                weak_confirm_rows.append(unmatched_rows[-1] if unmatched_rows else {"sample_id": row.get("sample_id"), "solution": item["solution_name"]})
            if item["requires_confirmation_level"] == "no_confirmation_required":
                item["warning_count"] += 1
                no_confirm_agree_rows.append({"sample_id": row.get("sample_id"), "solution": item["solution_name"], "scene": row.get("scene")})
            if len(item["evidence_examples"]) < 10:
                item["evidence_examples"].append(
                    {
                        "sample_id": row.get("sample_id"),
                        "scene": row.get("scene"),
                        "last_user_query": row.get("last_user_query", ""),
                        "match_type": match_type,
                    }
                )

    level_summary = collections.defaultdict(lambda: {"solutions": 0, "response_count": 0, "agree_count": 0})
    for item in stats.values():
        if item["response_count"]:
            item["agree_rate"] = round(item["agree_count"] / item["response_count"], 4)
        if item["unmatched_count"] > 0:
            item["notes"].append("has unmatched DialogueAgreeSolution")
        if item["requires_confirmation_level"] == "no_confirmation_required" and item["agree_count"] > 0:
            item["needs_trainer_confirmation"] = True
            item["notes"].append("no-confirm solution appears in DialogueAgreeSolution")
        level = item["requires_confirmation_level"]
        level_summary[level]["solutions"] += 1
        level_summary[level]["response_count"] += item["response_count"]
        level_summary[level]["agree_count"] += item["agree_count"]

    output = {
        "level_summary": level_summary,
        "solutions": sorted(stats.values(), key=lambda x: (-x["agree_count"], -x["response_count"], x["solution_name"])),
        "unmatched_dialogue_agree_top": unmatched_rows[:50],
        "weak_confirmation_examples": weak_confirm_rows[:50],
        "no_confirmation_agree_examples": no_confirm_agree_rows[:50],
    }
    dump_json(OUTPUT, output)

    md = []
    md.append("# Confirmation Policy v1 报告")
    md.append("")
    md.append("## 三分层汇总")
    for level, item in level_summary.items():
        rate = item["agree_count"] / item["response_count"] if item["response_count"] else 0
        md.append(f"- `{level}`: solutions={item['solutions']} response={item['response_count']} agree={item['agree_count']} rate={rate:.2%}")
    md.append("")
    for title, level in [
        ("strong confirmation 方案", "strong_confirmation_required"),
        ("user request is enough 方案", "user_request_is_enough"),
        ("no confirmation 方案", "no_confirmation_required"),
    ]:
        md.append(f"## {title}")
        for item in sorted([x for x in stats.values() if x["requires_confirmation_level"] == level], key=lambda x: -x["response_count"]):
            md.append(f"- `{item['solution_name']}` response={item['response_count']} agree={item['agree_count']} rate={item['agree_rate']}")
        md.append("")
    md.append("## unmatched DialogueAgreeSolution TOP 50")
    if unmatched_rows:
        for row in unmatched_rows[:50]:
            md.append(f"- `{row['sample_id']}` scene=`{row['scene']}` solution=`{row['solution']}` query=`{row['last_user_query']}`")
    else:
        md.append("- 暂无。")
    md.append("")
    md.append("## 需要训练师确认")
    if no_confirm_agree_rows:
        md.append("- no_confirmation_required 方案仍出现在 DialogueAgreeSolution，需要确认是否标注口径变更。")
    if weak_confirm_rows:
        md.append("- 部分 strong_confirmation_required 的 DialogueAgreeSolution 缺少显式确认词，需要抽样判断口语确认覆盖。")
    md.append("- user_request_is_enough 类方案可将 DialogueAgreeSolution 视为授权证据，但不要求非空。")
    REPORT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"policy": str(OUTPUT), "unmatched": len(unmatched_rows), "report": str(REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

