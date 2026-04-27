#!/usr/bin/env python3
"""Build v21 policy oracle labels and policy reports."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v21.common import V1_OUT, V2_ROOT, V21_REPORTS, V21_ROOT, ensure_dirs, get_case_records_path, get_flow_states_path, read_jsonl, relation, top_counter, write_jsonl
from flow_skill_policy_v21.policies.current_turn_intent import classify_current_turn
from flow_skill_policy_v21.policies.fulfillment_delivery_policy import decide_fulfillment_delivery
from flow_skill_policy_v21.policies.receipt_quality_policy import decide_receipt_quality


def _maps() -> tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]], Any]:
    cases = {row["sample_id"]: row for row in read_jsonl(get_case_records_path())}
    flows = {row["sample_id"]: row for row in read_jsonl(get_flow_states_path())}
    registry_path = V1_OUT / "solution_registry_v1.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else []
    return cases, flows, registry


def _old_rows(path: Path) -> Dict[str, Dict[str, Any]]:
    return {row["sample_id"]: row for row in read_jsonl(path)} if path.exists() else {}


def _build_one(
    replay_path: Path,
    output_path: Path,
    policy: Callable[[Dict[str, Any], Dict[str, Any], Any], Dict[str, Any]],
    cases: Dict[str, Dict[str, Any]],
    flows: Dict[str, Dict[str, Any]],
    registry: Any,
) -> List[Dict[str, Any]]:
    out = []
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
        current = classify_current_turn(replay.get("last_user_query") or case.get("last_user_query", ""))
        out.append(
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
                "current_turn_intent": current,
                "signals": replay.get("signals", {}),
                "input_without_target": replay.get("input_without_target", ""),
                "forbidden_solutions": decision.get("forbidden_solutions", []),
                "no_action_reason": decision.get("no_action_reason", ""),
            }
        )
    write_jsonl(output_path, out)
    return out


def _conflict_count(rows: List[Dict[str, Any]]) -> int:
    return sum(1 for r in rows if r.get("gold_oracle_relation") not in {"same", "canonical_same"})


def _oracle_no_gold(rows: List[Dict[str, Any]]) -> int:
    return sum(1 for r in rows if r.get("gold_oracle_relation") == "oracle_no_gold_action")


def _over_action(rows: List[Dict[str, Any]]) -> int:
    n = 0
    for row in rows:
        current = row.get("current_turn_intent") or classify_current_turn(row.get("last_user_query", ""))
        is_pending_confirm = str(row.get("oracle_rule_id", "")).endswith("CONFIRM") or row.get("oracle_decision_type") == "confirm"
        if (current.get("is_close_or_thanks") or current.get("is_ack_only") or current.get("is_transfer_only")) and row.get("oracle_response_solution") != "无" and not is_pending_confirm:
            n += 1
    return n


def _fixed(old: Dict[str, Dict[str, Any]], new_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    fixed = []
    for row in new_rows:
        old_row = old.get(row["sample_id"])
        if not old_row:
            continue
        old_current = classify_current_turn(old_row.get("last_user_query", ""))
        old_over = (old_current.get("is_close_or_thanks") or old_current.get("is_ack_only") or old_current.get("is_transfer_only")) and old_row.get("oracle_response_solution") != "无"
        if old_over and (row.get("oracle_response_solution") == "无" or str(row.get("oracle_rule_id", "")).endswith("CONFIRM")):
            fixed.append(row)
    return fixed


def _write_policy_report(name: str, v2_rows: Dict[str, Dict[str, Any]], v21_rows: List[Dict[str, Any]], path: Path) -> None:
    old_list = list(v2_rows.values())
    fixed = _fixed(v2_rows, v21_rows)
    old_rule_conf = Counter(r.get("oracle_rule_id") for r in old_list if r.get("gold_oracle_relation") not in {"same", "canonical_same"})
    new_rule_conf = Counter(r.get("oracle_rule_id") for r in v21_rows if r.get("gold_oracle_relation") not in {"same", "canonical_same"})
    lines = [
        f"# {name} Policy v21 Report",
        "",
        f"- conflict_v2: `{_conflict_count(old_list)}`",
        f"- conflict_v21: `{_conflict_count(v21_rows)}`",
        f"- oracle_no_gold_action_v2: `{_oracle_no_gold(old_list)}`",
        f"- oracle_no_gold_action_v21: `{_oracle_no_gold(v21_rows)}`",
        f"- close_ack_transfer_over_action_v2: `{_over_action(old_list)}`",
        f"- close_ack_transfer_over_action_v21: `{_over_action(v21_rows)}`",
        f"- close_ack_transfer_fixed: `{len(fixed)}`",
        "",
        "## V2 Conflict Rules",
        top_counter(old_rule_conf, 20) or "- none",
        "",
        "## V21 Conflict Rules",
        top_counter(new_rule_conf, 20) or "- none",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    cases, flows, registry = _maps()
    fd_rows = _build_one(
        V21_ROOT.parent / "flow_skill_mining_v1" / "replay" / "fulfillment_delivery_replay.jsonl",
        V21_ROOT / "replay" / "fulfillment_delivery_oracle_v21.jsonl",
        decide_fulfillment_delivery,
        cases,
        flows,
        registry,
    )
    rq_rows = _build_one(
        V21_ROOT.parent / "flow_skill_mining_v1" / "replay" / "receipt_quality_replay.jsonl",
        V21_ROOT / "replay" / "receipt_quality_oracle_v21.jsonl",
        decide_receipt_quality,
        cases,
        flows,
        registry,
    )
    fd_v2 = _old_rows(V2_ROOT / "replay" / "fulfillment_delivery_oracle.jsonl")
    rq_v2 = _old_rows(V2_ROOT / "replay" / "receipt_quality_oracle.jsonl")
    _write_policy_report("Fulfillment Delivery", fd_v2, fd_rows, V21_REPORTS / "fulfillment_delivery_policy_v21_report.md")
    _write_policy_report("Receipt Quality", rq_v2, rq_rows, V21_REPORTS / "receipt_quality_policy_v21_report.md")
    all_rows = fd_rows + rq_rows
    all_v2 = list(fd_v2.values()) + list(rq_v2.values())
    report = [
        "# Policy Oracle v21 Summary",
        "",
        f"- FD conflict v2 -> v21: `{_conflict_count(list(fd_v2.values()))}` -> `{_conflict_count(fd_rows)}`",
        f"- RQ conflict v2 -> v21: `{_conflict_count(list(rq_v2.values()))}` -> `{_conflict_count(rq_rows)}`",
        f"- FD oracle_no_gold_action v2 -> v21: `{_oracle_no_gold(list(fd_v2.values()))}` -> `{_oracle_no_gold(fd_rows)}`",
        f"- RQ oracle_no_gold_action v2 -> v21: `{_oracle_no_gold(list(rq_v2.values()))}` -> `{_oracle_no_gold(rq_rows)}`",
        f"- close_ack_over_action_fixed: `{len(_fixed(fd_v2, fd_rows)) + len(_fixed(rq_v2, rq_rows))}`",
    ]
    (V21_REPORTS / "policy_oracle_v21_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
