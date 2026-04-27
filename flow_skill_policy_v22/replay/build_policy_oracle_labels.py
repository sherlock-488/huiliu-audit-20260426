#!/usr/bin/env python3
"""Build v22 policy oracle labels and reports."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v22.common import V1_OUT, V21_ROOT, V22_REPORTS, V22_ROOT, ensure_dirs, get_case_records_path, get_flow_states_path, read_jsonl, relation, top_counter, write_jsonl
from flow_skill_policy_v22.policies.current_turn_intent import classify_current_turn
from flow_skill_policy_v22.policies.safe_context_bridge import enrich_current_intent
from flow_skill_policy_v22.policies.fulfillment_delivery_policy import decide_fulfillment_delivery
from flow_skill_policy_v22.policies.receipt_quality_policy import decide_receipt_quality


def _maps() -> tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]], Any]:
    cases = {row["sample_id"]: row for row in read_jsonl(get_case_records_path())}
    flows = {row["sample_id"]: row for row in read_jsonl(get_flow_states_path())}
    registry_path = V1_OUT / "solution_registry_v1.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else []
    return cases, flows, registry


def _old(path: Path) -> Dict[str, Dict[str, Any]]:
    return {r["sample_id"]: r for r in read_jsonl(path)} if path.exists() else {}


def _current(case: Dict[str, Any], flow: Dict[str, Any]) -> Dict[str, Any]:
    cur = classify_current_turn(case.get("last_user_query") or flow.get("last_user_query") or "")
    bridge = enrich_current_intent(case, flow, cur)
    if bridge.get("bridge_used"):
        cur = dict(cur)
        cur["current_intents"] = bridge["enriched_intents"]
        cur["bridge_used"] = True
        cur["bridge_reason"] = bridge["bridge_reason"]
    else:
        cur = dict(cur)
        cur["bridge_used"] = False
        cur["bridge_reason"] = bridge.get("bridge_reason", [])
    return cur


def _build(replay_path: Path, output_path: Path, policy: Callable, cases: Dict[str, Dict[str, Any]], flows: Dict[str, Dict[str, Any]], registry: Any) -> List[Dict[str, Any]]:
    rows = []
    for replay in read_jsonl(replay_path):
        sid = replay["sample_id"]
        case = cases.get(sid, {})
        flow = flows.get(sid, {})
        decision = policy(case, flow, registry)
        gold_rs = replay.get("gold_response_solution") or case.get("response_solution_raw") or "无"
        gold_agree = replay.get("gold_dialogue_agree_solution") or case.get("dialogue_agree_solution_raw") or "无"
        oracle_rs = decision.get("recommended_response_solution", "无") or "无"
        oracle_agree = decision.get("recommended_dialogue_agree_solution", "无") or "无"
        rel = relation(gold_rs, oracle_rs)
        agree_rel = relation(gold_agree, oracle_agree)
        rows.append(
            {
                "sample_id": sid,
                "scene": replay.get("scene") or case.get("scene"),
                "gold_response_solution": gold_rs,
                "gold_dialogue_agree_solution": gold_agree,
                "oracle_response_solution": oracle_rs,
                "oracle_dialogue_agree_solution": oracle_agree,
                "oracle_decision_type": decision.get("decision_type"),
                "oracle_rule_id": decision.get("priority_rule_id"),
                "gold_oracle_relation": rel,
                "gold_oracle_agree_relation": agree_rel,
                "rationale": decision.get("rationale", []),
                "needs_trainer_review": rel not in {"same", "canonical_same"} or agree_rel not in {"same", "canonical_same"},
                "last_user_query": replay.get("last_user_query", ""),
                "current_turn_intent": _current(case, flow),
                "signals": replay.get("signals", {}),
                "input_without_target": replay.get("input_without_target", ""),
                "no_action_reason": decision.get("no_action_reason", ""),
                "forbidden_solutions": decision.get("forbidden_solutions", []),
            }
        )
    write_jsonl(output_path, rows)
    return rows


def _conflict(rows: List[Dict[str, Any]]) -> int:
    return sum(1 for r in rows if r.get("gold_oracle_relation") not in {"same", "canonical_same"})


def _ong(rows: List[Dict[str, Any]]) -> int:
    return sum(1 for r in rows if r.get("gold_oracle_relation") == "oracle_no_gold_action")


def _over(rows: List[Dict[str, Any]]) -> int:
    n = 0
    for r in rows:
        cur = r.get("current_turn_intent") or {}
        is_confirm = str(r.get("oracle_rule_id", "")).endswith("CONFIRM") or r.get("oracle_decision_type") == "confirm"
        if (cur.get("is_close_or_thanks") or cur.get("is_ack_only") or cur.get("is_transfer_only")) and r.get("oracle_response_solution") != "无" and not is_confirm:
            n += 1
    return n


def _strong_over(rows: List[Dict[str, Any]]) -> int:
    return sum(1 for r in rows if r.get("oracle_dialogue_agree_solution") not in ("", "无", None) and r.get("gold_dialogue_agree_solution") in ("", "无", None))


def _report(name: str, old_rows: Dict[str, Dict[str, Any]], new_rows: List[Dict[str, Any]], path: Path) -> None:
    old_list = list(old_rows.values())
    old_rules = Counter(r.get("oracle_rule_id") for r in old_list if r.get("gold_oracle_relation") not in {"same", "canonical_same"})
    new_rules = Counter(r.get("oracle_rule_id") for r in new_rows if r.get("gold_oracle_relation") not in {"same", "canonical_same"})
    old_action = sum(1 for r in old_list if r.get("oracle_response_solution") != "无")
    new_action = sum(1 for r in new_rows if r.get("oracle_response_solution") != "无")
    lines = [
        f"# {name} Policy v22 Report",
        "",
        f"- conflict_v21: `{_conflict(old_list)}`",
        f"- conflict_v22: `{_conflict(new_rows)}`",
        f"- oracle_no_gold_action_v21: `{_ong(old_list)}`",
        f"- oracle_no_gold_action_v22: `{_ong(new_rows)}`",
        f"- close_ack_transfer_over_action_v22: `{_over(new_rows)}`",
        f"- strong_confirmation_over_trigger_v22: `{_strong_over(new_rows)}`",
        f"- oracle_action_count_v21: `{old_action}`",
        f"- oracle_action_count_v22: `{new_action}`",
        f"- OTHER_count_v21: `{old_rules.get(name.split()[0] == 'Fulfillment' and 'FD-OTHER' or 'RQ-OTHER', 0)}`",
        f"- OTHER_count_v22: `{new_rules.get(name.split()[0] == 'Fulfillment' and 'FD-OTHER' or 'RQ-OTHER', 0)}`",
        "",
        "## V21 Conflict Rules",
        top_counter(old_rules, 20) or "- none",
        "",
        "## V22 Conflict Rules",
        top_counter(new_rules, 20) or "- none",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    cases, flows, registry = _maps()
    fd = _build(V22_ROOT.parent / "flow_skill_mining_v1" / "replay" / "fulfillment_delivery_replay.jsonl", V22_ROOT / "replay" / "fulfillment_delivery_oracle_v22.jsonl", decide_fulfillment_delivery, cases, flows, registry)
    rq = _build(V22_ROOT.parent / "flow_skill_mining_v1" / "replay" / "receipt_quality_replay.jsonl", V22_ROOT / "replay" / "receipt_quality_oracle_v22.jsonl", decide_receipt_quality, cases, flows, registry)
    fd21 = _old(V21_ROOT / "replay" / "fulfillment_delivery_oracle_v21.jsonl")
    rq21 = _old(V21_ROOT / "replay" / "receipt_quality_oracle_v21.jsonl")
    _report("Fulfillment Delivery", fd21, fd, V22_REPORTS / "fulfillment_delivery_policy_v22_report.md")
    _report("Receipt Quality", rq21, rq, V22_REPORTS / "receipt_quality_policy_v22_report.md")
    (V22_REPORTS / "policy_oracle_v22_report.md").write_text(
        "\n".join(
            [
                "# Policy Oracle v22 Summary",
                "",
                f"- FD conflict v21 -> v22: `{_conflict(list(fd21.values()))}` -> `{_conflict(fd)}`",
                f"- RQ conflict v21 -> v22: `{_conflict(list(rq21.values()))}` -> `{_conflict(rq)}`",
                f"- FD oracle_no_gold_action v21 -> v22: `{_ong(list(fd21.values()))}` -> `{_ong(fd)}`",
                f"- RQ oracle_no_gold_action v21 -> v22: `{_ong(list(rq21.values()))}` -> `{_ong(rq)}`",
                f"- close_ack_over_action_v22: `{_over(fd) + _over(rq)}`",
                f"- strong_confirmation_over_trigger_v22: `{_strong_over(fd) + _strong_over(rq)}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
