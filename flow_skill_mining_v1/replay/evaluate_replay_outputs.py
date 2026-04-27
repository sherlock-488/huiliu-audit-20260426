#!/usr/bin/env python3
"""Evaluate future model outputs against replay sets. Does not call any model."""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_mining_v1.common_v1 import V1_OUT, canonical_components, canonicalize_solution, confirmation_level, load_jsonl, write_jsonl


def f1(pred: Set[str], gold: Set[str]) -> float:
    if not pred and not gold:
        return 1.0
    if not pred or not gold:
        return 0.0
    inter = len(pred & gold)
    p = inter / len(pred)
    r = inter / len(gold)
    return 2 * p * r / (p + r) if p + r else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", required=True)
    parser.add_argument("--model-outputs", required=True)
    parser.add_argument("--output", default=str(V1_OUT / "replay_eval_result.jsonl"))
    parser.add_argument("--report", default=str(V1_OUT / "reports" / "replay_eval_report.md"))
    args = parser.parse_args()

    replay = {r["sample_id"]: r for r in load_jsonl(Path(args.replay))}
    outputs = load_jsonl(Path(args.model_outputs))
    rows = []
    buckets = collections.defaultdict(lambda: collections.Counter())
    totals = collections.Counter()
    for out in outputs:
        sid = out.get("sample_id")
        gold = replay.get(sid)
        if not gold:
            continue
        pred_resp = out.get("ResponseSolution", "无")
        pred_agree = out.get("DialogueAgreeSolution", "无")
        gold_resp = gold.get("gold_response_solution", "无")
        gold_agree = gold.get("gold_dialogue_agree_solution", "无")
        pred_resp_comps = set(canonical_components(pred_resp)[0])
        gold_resp_comps = set(canonical_components(gold_resp)[0])
        pred_agree_comps = set(canonical_components(pred_agree)[0])
        gold_agree_comps = set(canonical_components(gold_agree)[0])
        resp_exact = pred_resp == gold_resp
        resp_canon = pred_resp_comps == gold_resp_comps
        agree_exact = pred_agree == gold_agree
        strong_pred = {x for x in pred_agree_comps if confirmation_level(x) == "strong_confirmation_required"}
        strong_gold = {x for x in gold_agree_comps if confirmation_level(x) == "strong_confirmation_required"}
        strong_precision = len(strong_pred & strong_gold) / len(strong_pred) if strong_pred else 1.0
        forbidden = False
        signals = gold.get("signals", {})
        if signals.get("订单是否可赔付") == "否" and any("操作赔付" in x for x in pred_resp_comps | pred_agree_comps):
            forbidden = True
        if signals.get("是否可取消订单") == "否" and "取消订单" in pred_resp_comps | pred_agree_comps:
            forbidden = True
        missing_warning = bool(not pred_resp_comps and gold_resp_comps)
        row = {
            "sample_id": sid,
            "scene": gold.get("scene"),
            "skill_id": gold.get("skill_id"),
            "response_exact_match": resp_exact,
            "response_canonical_match": resp_canon,
            "response_component_f1": f1(pred_resp_comps, gold_resp_comps),
            "dialogue_agree_exact_match": agree_exact,
            "strong_confirmation_precision": strong_precision,
            "forbidden_action": forbidden,
            "missing_action_warning": missing_warning,
            "no_action_reason_consistency": (not pred_resp_comps) == (gold_resp == "无"),
        }
        rows.append(row)
        for key, value in row.items():
            if isinstance(value, bool):
                totals[key] += int(value)
        totals["n"] += 1
        bucket = (gold.get("scene"), gold.get("gold_response_solution"), tuple(gold.get("expected_checker_focus", [])))
        buckets[bucket]["n"] += 1
        buckets[bucket]["response_canonical_match"] += int(resp_canon)
    write_jsonl(Path(args.output), rows)
    n = totals["n"]
    md = ["# Replay Eval Report", "", f"- evaluated rows: `{n}`"]
    for key in [
        "response_exact_match",
        "response_canonical_match",
        "dialogue_agree_exact_match",
        "forbidden_action",
        "missing_action_warning",
        "no_action_reason_consistency",
    ]:
        md.append(f"- {key}: `{totals[key]}/{n}` ({totals[key] / n:.2%} if nonzero)")
    md.append("")
    md.append("## Bucket metrics")
    for bucket, ctr in sorted(buckets.items(), key=lambda kv: -kv[1]["n"])[:80]:
        md.append(f"- `{bucket}` n={ctr['n']} response_canonical_match={ctr['response_canonical_match'] / ctr['n']:.2%}")
    Path(args.report).write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"evaluated": n, "report": args.report}, ensure_ascii=False))


if __name__ == "__main__":
    main()

