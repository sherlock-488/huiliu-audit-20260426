#!/usr/bin/env python3
"""Evaluate future model replay outputs against gold and policy oracle."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v2.common import canonical_components, canonicalize_solution, explicit_confirm, read_jsonl, relation, write_jsonl


STRONG_CANONICAL = {"取消订单", "小象单商品退款-xx%", "小象整单申请退款", "会员卡退款", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元"}


def _load_outputs(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    return {row.get("sample_id"): row for row in read_jsonl(path)}


def _canonical_match(a: str, b: str) -> bool:
    return relation(a or "无", b or "无") in {"same", "canonical_same"}


def _component_f1(pred: str, gold: str) -> float:
    p = set(canonical_components(pred))
    g = set(canonical_components(gold))
    if not p and not g:
        return 1.0
    if not p or not g:
        return 0.0
    inter = len(p & g)
    precision = inter / len(p)
    recall = inter / len(g)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _has_strong(solution: str) -> bool:
    return any(comp in STRONG_CANONICAL for comp in canonical_components(solution))


def evaluate(oracle_path: Path, model_outputs: Path, output: Path, report: Path) -> None:
    oracle_rows = list(read_jsonl(oracle_path))
    outputs = _load_outputs(model_outputs)
    if not outputs:
        report.parent.mkdir(parents=True, exist_ok=True)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("", encoding="utf-8")
        report.write_text(
            f"# Replay Eval Report v2\n\nNo model outputs found at `{model_outputs}`. This evaluator is ready for future replay runs.\n",
            encoding="utf-8",
        )
        return

    rows = []
    counters = Counter()
    by_rule: Dict[str, Counter] = defaultdict(Counter)
    by_scene: Dict[str, Counter] = defaultdict(Counter)
    for oracle in oracle_rows:
        sid = oracle["sample_id"]
        pred = outputs.get(sid, {})
        pred_rs = pred.get("ResponseSolution", "无")
        pred_agree = pred.get("DialogueAgreeSolution", "无")
        gold_rs = oracle.get("gold_response_solution", "无")
        gold_agree = oracle.get("gold_dialogue_agree_solution", "无")
        oracle_rs = oracle.get("oracle_response_solution", "无")
        oracle_agree = oracle.get("oracle_dialogue_agree_solution", "无")
        gold_exact = pred_rs == gold_rs
        gold_canon = _canonical_match(pred_rs, gold_rs)
        oracle_exact = pred_rs == oracle_rs
        oracle_canon = _canonical_match(pred_rs, oracle_rs)
        strong_agree_pred = _has_strong(pred_agree)
        strong_agree_gold = _has_strong(gold_agree) or _has_strong(oracle_agree)
        over_trigger = strong_agree_pred and not strong_agree_gold
        forbidden = oracle.get("oracle_decision_type") == "guard" and pred_rs != "无"
        ineligible = oracle.get("oracle_response_solution") == "无" and pred_rs != "无" and oracle.get("oracle_decision_type") in {"guard", "no_action"}
        missing = oracle.get("oracle_response_solution") != "无" and pred_rs == "无"
        result = {
            "sample_id": sid,
            "scene": oracle.get("scene"),
            "oracle_rule_id": oracle.get("oracle_rule_id"),
            "pred_response_solution": pred_rs,
            "pred_dialogue_agree_solution": pred_agree,
            "gold_response_solution": gold_rs,
            "oracle_response_solution": oracle_rs,
            "gold_response_exact": gold_exact,
            "gold_response_canonical": gold_canon,
            "oracle_response_exact": oracle_exact,
            "oracle_response_canonical": oracle_canon,
            "response_component_f1_vs_gold": _component_f1(pred_rs, gold_rs),
            "dialogue_agree_exact_vs_gold": pred_agree == gold_agree,
            "dialogue_agree_precision_strong_confirmation": None if not strong_agree_pred else bool(strong_agree_gold),
            "dialogue_agree_over_trigger": over_trigger,
            "forbidden_action": forbidden,
            "ineligible_action": ineligible,
            "missing_eligible_action": missing,
            "gold_oracle_relation": oracle.get("gold_oracle_relation"),
        }
        rows.append(result)
        for key in ["gold_response_exact", "gold_response_canonical", "oracle_response_exact", "oracle_response_canonical", "dialogue_agree_over_trigger", "forbidden_action", "ineligible_action", "missing_eligible_action"]:
            counters[key] += int(bool(result[key]))
            by_rule[oracle.get("oracle_rule_id", "")][key] += int(bool(result[key]))
            by_scene[oracle.get("scene", "")][key] += int(bool(result[key]))
        counters["total"] += 1
        by_rule[oracle.get("oracle_rule_id", "")]["total"] += 1
        by_scene[oracle.get("scene", "")]["total"] += 1
    write_jsonl(output, rows)

    total = counters["total"] or 1
    lines = [
        "# Replay Eval Report v2",
        "",
        f"- total: `{counters['total']}`",
        f"- gold ResponseSolution exact match: `{counters['gold_response_exact'] / total:.4f}`",
        f"- gold ResponseSolution canonical match: `{counters['gold_response_canonical'] / total:.4f}`",
        f"- oracle ResponseSolution exact match: `{counters['oracle_response_exact'] / total:.4f}`",
        f"- oracle ResponseSolution canonical match: `{counters['oracle_response_canonical'] / total:.4f}`",
        f"- DialogueAgreeSolution over-trigger rate: `{counters['dialogue_agree_over_trigger'] / total:.4f}`",
        f"- forbidden_action_rate: `{counters['forbidden_action'] / total:.4f}`",
        f"- ineligible_action_rate: `{counters['ineligible_action'] / total:.4f}`",
        f"- missing_eligible_action_rate: `{counters['missing_eligible_action'] / total:.4f}`",
        "",
        "## By Oracle Rule",
    ]
    for rule, counter in sorted(by_rule.items(), key=lambda kv: kv[1]["total"], reverse=True)[:50]:
        t = counter["total"] or 1
        lines.append(f"- `{rule}` total=`{counter['total']}` oracle_canonical=`{counter['oracle_response_canonical']/t:.3f}` forbidden=`{counter['forbidden_action']/t:.3f}` missing=`{counter['missing_eligible_action']/t:.3f}`")
    lines.extend(["", "## By Scene"])
    for scene, counter in sorted(by_scene.items(), key=lambda kv: kv[1]["total"], reverse=True):
        t = counter["total"] or 1
        lines.append(f"- `{scene}` total=`{counter['total']}` oracle_canonical=`{counter['oracle_response_canonical']/t:.3f}`")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle", default="flow_skill_policy_v2/replay/fulfillment_delivery_oracle.jsonl")
    parser.add_argument("--model-outputs", default="flow_skill_policy_v2/replay/model_outputs.jsonl")
    parser.add_argument("--output", default="flow_skill_policy_v2/replay/replay_eval_result_v2.jsonl")
    parser.add_argument("--report", default="flow_skill_policy_v2/replay/replay_eval_report_v2.md")
    args = parser.parse_args()
    evaluate(Path(args.oracle), Path(args.model_outputs), Path(args.output), Path(args.report))


if __name__ == "__main__":
    main()
