#!/usr/bin/env python3
"""Mine draft state -> action rules."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import OUT_DIR, REPORT_DIR, compact_counter, ensure_dirs, load_jsonl_list, sha1_text, write_jsonl


FLOW_PATH = OUT_DIR / "flow_states.jsonl"
NO_ACTION_PATH = OUT_DIR / "no_action_labeled.jsonl"
OUTPUT_PATH = OUT_DIR / "state_action_rules_draft.jsonl"
REPORT_PATH = REPORT_DIR / "state_action_rules_report.md"

HIGH_VALUE_ACTIONS = ["取消订单", "小象单商品退款", "操作赔付", "会员卡退款", "催促退款审核", "外呼"]
FINE_FIELDS = [
    "scene",
    "user_intent",
    "order_status",
    "rider_status",
    "timeout_state",
    "has_timeout_risk",
    "can_cancel",
    "can_compensate",
    "already_compensated",
    "refund_state",
    "selected_sku_state",
    "image_state",
    "has_rider_phone",
    "pending_confirmation_solution",
]


def _action_key(state: Dict[str, Any], no_action_reason: str) -> Tuple[str, str, str]:
    return (
        state.get("response_solution_raw", "无"),
        state.get("dialogue_agree_solution_raw", "无"),
        no_action_reason,
    )


def _group_key(state: Dict[str, Any], fields: List[str]) -> Tuple[Tuple[str, Any], ...]:
    return tuple((field, state.get(field)) for field in fields)


def _pattern_from_key(key: Tuple[Tuple[str, Any], ...]) -> Dict[str, Any]:
    return {field: value for field, value in key if value not in (None, "", [], {})}


def _patch_type(response_solution: str, agree_solution: str, no_action_reason: str) -> str:
    if agree_solution and agree_solution != "无":
        return "confirmation_rule"
    if no_action_reason:
        if no_action_reason.startswith("ask_") or no_action_reason == "clarify_intent":
            return "clarify_rule"
        return "no_action_rule"
    if any(word in response_solution for word in ["不得", "不可", "不能"]):
        return "guard"
    if response_solution and response_solution != "无":
        return "tool_rule"
    return "priority_rule"


def _is_high_value(action: Tuple[str, str, str]) -> bool:
    text = " ".join(action)
    return any(word in text for word in HIGH_VALUE_ACTIONS)


def _mine(groups: Dict[Any, List[Dict[str, Any]]], level: str) -> List[Dict[str, Any]]:
    rules = []
    for key, rows in groups.items():
        action_ctr = collections.Counter(row["_action"] for row in rows)
        support = len(rows)
        if not action_ctr:
            continue
        best_action, best_count = action_ctr.most_common(1)[0]
        if support < 3 and not (_is_high_value(best_action) and support >= 2):
            continue
        confidence = best_count / support
        if confidence < 0.5 and support < 10:
            continue
        pattern = _pattern_from_key(key)
        rule_id = "rule_" + sha1_text(level + json.dumps(pattern, ensure_ascii=False, sort_keys=True) + str(best_action))[:12]
        conflicts = [
            {"action": list(action), "count": count}
            for action, count in action_ctr.most_common(8)
            if action != best_action
        ]
        rules.append(
            {
                "rule_id": rule_id,
                "scene": pattern.get("scene", ""),
                "state_pattern": pattern,
                "expected_response_solution": best_action[0],
                "expected_dialogue_agree_solution": best_action[1],
                "no_action_reason": best_action[2],
                "support": support,
                "confidence": round(confidence, 4),
                "example_sample_ids": [row.get("sample_id", "") for row in rows[:20]],
                "conflicting_actions": conflicts,
                "candidate_skill_patch_type": _patch_type(*best_action),
                "aggregation_level": level,
            }
        )
    return rules


def main() -> None:
    ensure_dirs()
    states = load_jsonl_list(FLOW_PATH)
    no_action = {r.get("sample_id"): r for r in load_jsonl_list(NO_ACTION_PATH)}
    enriched = []
    for state in states:
        reason = no_action.get(state.get("sample_id"), {}).get("no_action_reason", "")
        row = dict(state)
        row["_action"] = _action_key(state, reason)
        row["_possible_missing_action"] = no_action.get(state.get("sample_id"), {}).get("possible_missing_action", False)
        enriched.append(row)

    coarse_groups = collections.defaultdict(list)
    fine_groups = collections.defaultdict(list)
    for row in enriched:
        coarse_groups[_group_key(row, ["scene", "user_intent"])].append(row)
        fine_groups[_group_key(row, FINE_FIELDS)].append(row)

    rules = _mine(coarse_groups, "coarse") + _mine(fine_groups, "fine")
    rules.sort(key=lambda r: (-r["confidence"], -r["support"], r["scene"]))
    write_jsonl(OUTPUT_PATH, rules)

    strong = [r for r in rules if r["confidence"] >= 0.7]
    conflict = [r for r in rules if r["confidence"] < 0.7]
    strong_scene_ctr = collections.Counter(r["scene"] for r in strong)
    conflict_scene_ctr = collections.Counter(r["scene"] for r in conflict)
    divergent = sorted(rules, key=lambda r: (len(r["conflicting_actions"]), r["support"]), reverse=True)[:50]
    missing_action_patterns = [row for row in enriched if row.get("_possible_missing_action")]
    confirmation_rules = [r for r in rules if r["expected_dialogue_agree_solution"] != "无"]

    md = []
    md.append("# State -> Action 规则挖掘报告")
    md.append("")
    md.append(f"- draft rules: `{len(rules)}`")
    md.append(f"- strong rules (confidence >= 0.7): `{len(strong)}`")
    md.append(f"- conflict/ambiguous rules: `{len(conflict)}`")
    md.append(f"- confirmation rules: `{len(confirmation_rules)}`")
    md.append(f"- ResponseSolution=无 疑似漏操作样本: `{len(missing_action_patterns)}`")
    md.append("")
    md.append("## 按 scene 的 strong rule 数")
    md.append(compact_counter(strong_scene_ctr, 50))
    md.append("")
    md.append("## 按 scene 的 conflict rule 数")
    md.append(compact_counter(conflict_scene_ctr, 50))
    md.append("")
    md.append("## 同一 state 下 action 分歧最大的 TOP 50")
    for r in divergent[:50]:
        md.append(
            f"- `{r['rule_id']}` scene=`{r['scene']}` support={r['support']} conf={r['confidence']} "
            f"expected=`{r['expected_response_solution']}` conflicts={r['conflicting_actions'][:3]}"
        )
    md.append("")
    md.append("## DialogueAgreeSolution 非空的 confirmation rules")
    for r in confirmation_rules[:80]:
        md.append(
            f"- `{r['rule_id']}` scene=`{r['scene']}` agree=`{r['expected_dialogue_agree_solution']}` "
            f"support={r['support']} conf={r['confidence']}"
        )
    md.append("")
    md.append("## 需要训练师确认的规则")
    for r in conflict[:80]:
        md.append(
            f"- `{r['rule_id']}` scene=`{r['scene']}` state={r['state_pattern']} "
            f"expected=`{r['expected_response_solution']}` confidence={r['confidence']}"
        )
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"rules": len(rules), "strong": len(strong), "conflict": len(conflict), "report": str(REPORT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
