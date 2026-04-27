#!/usr/bin/env python3
"""Evaluate v22 model outputs on stable/action/challenge sets."""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v22.common import canonical_components, read_jsonl, relation, write_jsonl


STRONG = {"取消订单", "小象单商品退款-xx%", "小象整单申请退款", "会员卡退款", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元"}


def _load(path: Path) -> List[Dict[str, Any]]:
    return list(read_jsonl(path)) if path.exists() else []


def _outputs(path: Path) -> Dict[str, Dict[str, Any]]:
    return {r.get("sample_id"): r for r in read_jsonl(path)} if path.exists() else {}


def _strong(solution: str) -> bool:
    return any(x in STRONG for x in canonical_components(solution))


def _eval(rows: List[Dict[str, Any]], outputs: Dict[str, Dict[str, Any]], set_type: str) -> tuple[List[Dict[str, Any]], Counter, Dict[str, Counter]]:
    out = []
    c = Counter()
    by_rule = defaultdict(Counter)
    for r in rows:
        pred = outputs.get(r["sample_id"], {})
        pred_rs = pred.get("ResponseSolution", "无")
        pred_agree = pred.get("DialogueAgreeSolution", "无")
        oracle_rs = r.get("oracle_response_solution", "无")
        gold_rs = r.get("gold_response_solution", "无")
        cur = r.get("current_turn_intent") or {}
        item = {
            "sample_id": r["sample_id"],
            "set_type": set_type,
            "scene": r.get("scene"),
            "oracle_rule_id": r.get("oracle_rule_id"),
            "gold_response_solution": gold_rs,
            "oracle_response_solution": oracle_rs,
            "pred_response_solution": pred_rs,
            "pred_dialogue_agree_solution": pred_agree,
            "gold_response_canonical": relation(pred_rs, gold_rs) in {"same", "canonical_same"},
            "oracle_response_canonical": relation(pred_rs, oracle_rs) in {"same", "canonical_same"},
            "is_action_case": oracle_rs != "无" or gold_rs != "无",
            "pred_action": pred_rs != "无",
            "pred_no_action": pred_rs == "无",
            "oracle_no_action": oracle_rs == "无",
            "close_ack_over_action": bool((cur.get("is_close_or_thanks") or cur.get("is_ack_only") or cur.get("is_transfer_only")) and pred_rs != "无"),
            "strong_confirm_over_trigger": bool(_strong(pred_agree) and not _strong(r.get("oracle_dialogue_agree_solution", "无"))),
            "ineligible_action": bool(r.get("oracle_decision_type") == "guard" and pred_rs != "无"),
        }
        out.append(item)
        for key in ["gold_response_canonical", "oracle_response_canonical", "close_ack_over_action", "strong_confirm_over_trigger", "ineligible_action"]:
            c[key] += int(item[key])
            by_rule[r.get("oracle_rule_id", "")][key] += int(item[key])
        c["total"] += 1
        c["action_cases"] += int(item["is_action_case"])
        c["action_recalled"] += int(item["is_action_case"] and item["pred_action"])
        c["oracle_no_action"] += int(item["oracle_no_action"])
        c["no_action_correct"] += int(item["oracle_no_action"] and item["pred_no_action"])
        by_rule[r.get("oracle_rule_id", "")]["total"] += 1
    return out, c, by_rule


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--stable-oracle", required=True)
    p.add_argument("--action-oracle", required=True)
    p.add_argument("--challenge-oracle", required=True)
    p.add_argument("--model-outputs", required=True)
    p.add_argument("--output", default="flow_skill_policy_v22/replay/replay_eval_result_v22.jsonl")
    p.add_argument("--report", default="flow_skill_policy_v22/replay/replay_eval_report_v22.md")
    args = p.parse_args()
    outputs = _outputs(Path(args.model_outputs))
    if not outputs:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text("", encoding="utf-8")
        Path(args.report).write_text("# Replay Eval Report v22\n\nNo model outputs provided. Stable/action/challenge evaluator is ready.\n", encoding="utf-8")
        return
    stable_eval, stable_c, by_rule = _eval(_load(Path(args.stable_oracle)), outputs, "stable")
    action_eval, action_c, _ = _eval(_load(Path(args.action_oracle)), outputs, "action")
    challenge_eval, challenge_c, _ = _eval(_load(Path(args.challenge_oracle)), outputs, "challenge")
    write_jsonl(Path(args.output), stable_eval + action_eval + challenge_eval)
    st = stable_c["total"] or 1
    act = action_c["action_cases"] or 1
    no = stable_c["oracle_no_action"] or 1
    lines = [
        "# Replay Eval Report v22",
        "",
        "Main metrics use stable replay; action-focused is separate; challenge is analysis only.",
        f"- stable_total: `{stable_c['total']}`",
        f"- stable_oracle_canonical: `{stable_c['oracle_response_canonical']/st:.4f}`",
        f"- no_action_precision_on_stable: `{stable_c['no_action_correct']/no:.4f}`",
        f"- close_ack_over_action_rate: `{stable_c['close_ack_over_action']/st:.4f}`",
        f"- strong_confirm_over_trigger_rate: `{stable_c['strong_confirm_over_trigger']/st:.4f}`",
        f"- ineligible_action_rate: `{stable_c['ineligible_action']/st:.4f}`",
        f"- action_focused_total: `{action_c['total']}`",
        f"- action_recall_on_action_focused: `{action_c['action_recalled']/act:.4f}`",
        f"- challenge_total: `{challenge_c['total']}`",
        "",
        "## By Oracle Rule (stable)",
    ]
    for rule, counter in sorted(by_rule.items(), key=lambda kv: kv[1]["total"], reverse=True)[:50]:
        t = counter["total"] or 1
        lines.append(f"- `{rule}` total=`{counter['total']}` oracle_canonical=`{counter['oracle_response_canonical']/t:.3f}` close_ack_over=`{counter['close_ack_over_action']/t:.3f}`")
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
