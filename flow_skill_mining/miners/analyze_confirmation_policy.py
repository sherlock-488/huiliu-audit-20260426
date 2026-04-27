#!/usr/bin/env python3
"""Analyze DialogueAgreeSolution confirmation semantics."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import (
    OUT_DIR,
    REPORT_DIR,
    compact_counter,
    dump_json,
    ensure_dirs,
    initial_requires_agreement,
    load_jsonl_list,
    normalize_solution_name,
    safe_div,
)


TRAJ_PATH = OUT_DIR / "session_trajectories.jsonl"
REGISTRY_PATH = OUT_DIR / "solution_registry.json"
OUTPUT_PATH = OUT_DIR / "confirmation_policy_draft.json"
REPORT_PATH = REPORT_DIR / "confirmation_policy_report.md"


def main() -> None:
    ensure_dirs()
    rows = load_jsonl_list(TRAJ_PATH)
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")) if REGISTRY_PATH.exists() else []
    stats: Dict[str, Dict[str, Any]] = {}

    def touch(raw_name: str) -> Dict[str, Any]:
        norm, _ = normalize_solution_name(raw_name)
        if norm not in stats:
            stats[norm] = {
                "solution_name": norm,
                "response_solution_count": 0,
                "dialogue_agree_solution_count": 0,
                "dialogue_agree_rate": 0.0,
                "matched_to_previous_offer_count": 0,
                "matched_to_current_offer_count": 0,
                "unmatched_count": 0,
                "likely_requires_confirmation": None,
                "evidence_examples": [],
                "needs_trainer_confirmation": False,
                "notes": [],
            }
        return stats[norm]

    for entry in registry:
        touch(entry.get("normalized_name", ""))

    for row in rows:
        for comp in row.get("response_solution_components", []):
            touch(comp)["response_solution_count"] += 1
        for comp in row.get("dialogue_agree_solution_components", []):
            item = touch(comp)
            item["dialogue_agree_solution_count"] += 1
            match_type = row.get("dialogue_agree_match_type", "")
            if match_type == "previous" or row.get("pending_confirmation_solution"):
                item["matched_to_previous_offer_count"] += 1
            elif match_type == "current":
                item["matched_to_current_offer_count"] += 1
            elif match_type == "unmatched":
                item["unmatched_count"] += 1
            if len(item["evidence_examples"]) < 12:
                item["evidence_examples"].append(
                    {
                        "sample_id": row.get("sample_id", ""),
                        "session_id": row.get("session_id", ""),
                        "turn_index": row.get("turn_index", 0),
                        "last_user_query": row.get("last_user_query", ""),
                        "match_type": match_type,
                    }
                )

    must_confirm = []
    no_confirm = []
    unclear = []
    conflicts = []
    for item in stats.values():
        resp = item["response_solution_count"]
        agree = item["dialogue_agree_solution_count"]
        rate = safe_div(agree, resp)
        item["dialogue_agree_rate"] = round(rate, 4)
        rule = initial_requires_agreement(item["solution_name"])
        if agree >= 3 and (item["matched_to_previous_offer_count"] + item["matched_to_current_offer_count"]) / max(agree, 1) >= 0.5:
            item["likely_requires_confirmation"] = True
        elif resp >= 10 and agree <= 1:
            item["likely_requires_confirmation"] = False
        elif rule is not None:
            item["likely_requires_confirmation"] = rule
        else:
            item["likely_requires_confirmation"] = None
        if rule is not None and item["likely_requires_confirmation"] is not None and rule != item["likely_requires_confirmation"]:
            item["needs_trainer_confirmation"] = True
            item["notes"].append("initial rule conflicts with data behavior")
            conflicts.append(item)
        if item["unmatched_count"] > 0:
            item["notes"].append("has unmatched DialogueAgreeSolution examples")
            if item["unmatched_count"] >= 3:
                item["needs_trainer_confirmation"] = True
        if item["likely_requires_confirmation"] is True:
            must_confirm.append(item["solution_name"])
        elif item["likely_requires_confirmation"] is False:
            no_confirm.append(item["solution_name"])
        else:
            unclear.append(item["solution_name"])

    output = {
        "solutions": sorted(stats.values(), key=lambda x: (-x["dialogue_agree_solution_count"], -x["response_solution_count"], x["solution_name"])),
        "must_confirm": sorted(must_confirm),
        "no_confirm": sorted(no_confirm),
        "unclear": sorted(unclear),
    }
    dump_json(OUTPUT_PATH, output)

    agree_ctr = collections.Counter(
        item["solution_name"] for item in stats.values() for _ in range(item["dialogue_agree_solution_count"])
    )
    md = []
    md.append("# Confirmation Policy 报告")
    md.append("")
    md.append(f"- likely_requires_confirmation=true solution 数: `{len(must_confirm)}`")
    md.append(f"- likely_requires_confirmation=false solution 数: `{len(no_confirm)}`")
    md.append(f"- 语义不清 solution 数: `{len(unclear)}`")
    md.append("")
    md.append("## DialogueAgreeSolution 是否是执行确认强信号")
    md.append("- 数据上，DialogueAgreeSolution 非空通常应被视为进入“用户确认/执行确认”态；但仍存在 unmatched 或规则冲突样本，需要训练师确认。")
    md.append("- 不能把 DialogueAgreeSolution 简单复制 ResponseSolution；它更像“用户已同意上一轮或本轮待确认方案”的结构化标签。")
    md.append("")
    md.append("## 必须/疑似需要用户同意")
    for name in must_confirm:
        md.append(f"- `{name}`")
    md.append("")
    md.append("## 通常不需要用户同意")
    for name in no_confirm:
        md.append(f"- `{name}`")
    md.append("")
    md.append("## 语义不清/样本不足")
    for name in unclear:
        md.append(f"- `{name}`")
    md.append("")
    md.append("## 数据表现和初始规则冲突")
    if conflicts:
        for item in conflicts:
            md.append(f"- `{item['solution_name']}` response={item['response_solution_count']} agree={item['dialogue_agree_solution_count']} rate={item['dialogue_agree_rate']}")
    else:
        md.append("- 暂无显著冲突。")
    md.append("")
    md.append("## DialogueAgreeSolution top")
    md.append(compact_counter(agree_ctr, 80))
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"policy": str(OUTPUT_PATH), "likely_confirm": len(must_confirm), "report": str(REPORT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
