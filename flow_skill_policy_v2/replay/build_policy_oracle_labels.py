#!/usr/bin/env python3
"""Build policy-oracle labels for v1 replay cases."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v2.common import (
    V1_OUT,
    V2_REPORTS,
    V2_ROOT,
    canonical_components,
    ensure_dirs,
    get_case_records_path,
    get_flow_states_path,
    read_jsonl,
    relation,
    top_counter,
    write_jsonl,
)
from flow_skill_policy_v2.policies.fulfillment_delivery_policy import decide_fulfillment_delivery
from flow_skill_policy_v2.policies.receipt_quality_policy import decide_receipt_quality


def _maps() -> tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]], Any]:
    cases = {row["sample_id"]: row for row in read_jsonl(get_case_records_path())}
    flows = {row["sample_id"]: row for row in read_jsonl(get_flow_states_path())}
    registry_path = V1_OUT / "solution_registry_v1.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else []
    return cases, flows, registry


def _build_one(
    replay_path: Path,
    output_path: Path,
    policy: Callable[[Dict[str, Any], Dict[str, Any], Any], Dict[str, Any]],
    cases: Dict[str, Dict[str, Any]],
    flows: Dict[str, Dict[str, Any]],
    registry: Any,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
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
        needs_review = rel not in {"same", "canonical_same"} or agree_rel not in {"same", "canonical_same"}
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
                "needs_trainer_review": needs_review,
                "last_user_query": replay.get("last_user_query", ""),
                "signals": replay.get("signals", {}),
                "input_without_target": replay.get("input_without_target", ""),
            }
        )
    write_jsonl(output_path, out)
    return out


def main() -> None:
    ensure_dirs()
    cases, flows, registry = _maps()
    fd_rows = _build_one(
        V2_ROOT.parent / "flow_skill_mining_v1" / "replay" / "fulfillment_delivery_replay.jsonl",
        V2_ROOT / "replay" / "fulfillment_delivery_oracle.jsonl",
        decide_fulfillment_delivery,
        cases,
        flows,
        registry,
    )
    rq_rows = _build_one(
        V2_ROOT.parent / "flow_skill_mining_v1" / "replay" / "receipt_quality_replay.jsonl",
        V2_ROOT / "replay" / "receipt_quality_oracle.jsonl",
        decide_receipt_quality,
        cases,
        flows,
        registry,
    )
    all_rows = fd_rows + rq_rows
    relation_counts = Counter(row["gold_oracle_relation"] for row in all_rows)
    rule_conflicts = Counter(row["oracle_rule_id"] for row in all_rows if row["needs_trainer_review"])
    fd_gold_no_oracle_action = [
        row for row in fd_rows if row["gold_response_solution"] == "无" and row["oracle_response_solution"] in {"系统催单", "加急调度"}
    ]
    rq_gold_refund_guard = [
        row
        for row in rq_rows
        if canonical_components(row["gold_response_solution"]) == ["小象单商品退款-xx%"]
        and row["oracle_response_solution"] == "无"
        and row["oracle_rule_id"] in {"RQ-01", "RQ-02", "RQ-03", "RQ-04", "RQ-05", "RQ-06"}
    ]
    rq_gold_no_oracle_action = [row for row in rq_rows if row["gold_response_solution"] == "无" and row["oracle_response_solution"] != "无"]
    report = [
        "# Policy Oracle Report",
        "",
        f"- fulfillment_delivery_oracle_cases: `{len(fd_rows)}`",
        f"- receipt_quality_oracle_cases: `{len(rq_rows)}`",
        f"- needs_trainer_review: `{sum(1 for r in all_rows if r['needs_trainer_review'])}`",
        "",
        "## Gold / Oracle Relation",
        top_counter(relation_counts, 20) or "- none",
        "",
        "## Conflict Rules",
        top_counter(rule_conflicts, 30) or "- none",
        "",
        f"- fulfillment_delivery gold=无 but oracle=系统催单/加急调度: `{len(fd_gold_no_oracle_action)}`",
        f"- receipt_quality gold=退款 but oracle 前置 guard: `{len(rq_gold_refund_guard)}`",
        f"- receipt_quality gold=无 but oracle action: `{len(rq_gold_no_oracle_action)}`",
        "",
        "这些冲突不是自动判 gold 错，而是进入训练师校准包。",
    ]
    (V2_REPORTS / "policy_oracle_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
