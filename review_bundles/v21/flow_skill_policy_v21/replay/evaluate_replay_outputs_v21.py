#!/usr/bin/env python3
"""Evaluate v21 replay outputs with stable/challenge separation."""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v21.common import canonical_components, read_jsonl, relation, write_jsonl


STRONG = {"取消订单", "小象单商品退款-xx%", "小象整单申请退款", "会员卡退款", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元"}


def _load_outputs(path: Path) -> Dict[str, Dict[str, Any]]:
    return {row.get("sample_id"): row for row in read_jsonl(path)} if path.exists() else {}


def _strong(solution: str) -> bool:
    return any(x in STRONG for x in canonical_components(solution))


def _eval_rows(rows: List[Dict[str, Any]], outputs: Dict[str, Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Counter, Dict[str, Counter]]:
    out = []
    c = Counter()
    by_rule = defaultdict(Counter)
    for row in rows:
        pred = outputs.get(row["sample_id"], {})
        pred_rs = pred.get("ResponseSolution", "无")
        pred_agree = pred.get("DialogueAgreeSolution", "无")
        oracle_rs = row.get("oracle_response_solution", "无")
        gold_rs = row.get("gold_response_solution", "无")
        current = row.get("current_turn_intent") or {}
        close_over = current.get("is_close_or_thanks") and pred_rs != "无"
        ack_over = current.get("is_ack_only") and pred_rs != "无"
        transfer_over = current.get("is_transfer_only") and pred_rs != "无"
        over_trigger = _strong(pred_agree) and not _strong(row.get("oracle_dialogue_agree_solution", "无"))
        item = {
            "sample_id": row["sample_id"],
            "scene": row.get("scene"),
            "oracle_rule_id": row.get("oracle_rule_id"),
            "gold_response_solution": gold_rs,
            "oracle_response_solution": oracle_rs,
            "pred_response_solution": pred_rs,
            "pred_dialogue_agree_solution": pred_agree,
            "gold_response_exact": pred_rs == gold_rs,
            "gold_response_canonical": relation(pred_rs, gold_rs) in {"same", "canonical_same"},
            "oracle_response_exact": pred_rs == oracle_rs,
            "oracle_response_canonical": relation(pred_rs, oracle_rs) in {"same", "canonical_same"},
            "close_over_action": bool(close_over),
            "ack_over_action": bool(ack_over),
            "transfer_over_action": bool(transfer_over),
            "dialogue_agree_over_trigger": bool(over_trigger),
        }
        out.append(item)
        for key in ["gold_response_exact", "gold_response_canonical", "oracle_response_exact", "oracle_response_canonical", "close_over_action", "ack_over_action", "transfer_over_action", "dialogue_agree_over_trigger"]:
            c[key] += int(item[key])
            by_rule[row.get("oracle_rule_id", "")][key] += int(item[key])
        c["total"] += 1
        by_rule[row.get("oracle_rule_id", "")]["total"] += 1
    return out, c, by_rule


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stable-oracle", required=True)
    parser.add_argument("--challenge-oracle", required=True)
    parser.add_argument("--model-outputs", required=True)
    parser.add_argument("--output", default="flow_skill_policy_v21/replay/replay_eval_result_v21.jsonl")
    parser.add_argument("--report", default="flow_skill_policy_v21/replay/replay_eval_report_v21.md")
    args = parser.parse_args()
    stable = list(read_jsonl(Path(args.stable_oracle)))
    challenge = list(read_jsonl(Path(args.challenge_oracle)))
    outputs = _load_outputs(Path(args.model_outputs))
    if not outputs:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text("", encoding="utf-8")
        Path(args.report).write_text("# Replay Eval Report v21\n\nNo model outputs provided. Main metrics will run on stable replay only when outputs are available.\n", encoding="utf-8")
        return
    stable_eval, stable_c, by_rule = _eval_rows(stable, outputs)
    challenge_eval, challenge_c, _ = _eval_rows(challenge, outputs)
    write_jsonl(Path(args.output), stable_eval + challenge_eval)
    total = stable_c["total"] or 1
    lines = [
        "# Replay Eval Report v21",
        "",
        "Main metrics use stable replay only. Challenge replay is reported separately.",
        "",
        f"- stable_total: `{stable_c['total']}`",
        f"- stable_gold_exact: `{stable_c['gold_response_exact']/total:.4f}`",
        f"- stable_oracle_canonical: `{stable_c['oracle_response_canonical']/total:.4f}`",
        f"- close_over_action_rate: `{stable_c['close_over_action']/total:.4f}`",
        f"- ack_over_action_rate: `{stable_c['ack_over_action']/total:.4f}`",
        f"- transfer_over_action_rate: `{stable_c['transfer_over_action']/total:.4f}`",
        f"- dialogue_agree_over_trigger_rate: `{stable_c['dialogue_agree_over_trigger']/total:.4f}`",
        f"- challenge_total: `{challenge_c['total']}`",
        "",
        "## By Oracle Rule (stable)",
    ]
    for rule, counter in sorted(by_rule.items(), key=lambda kv: kv[1]["total"], reverse=True)[:50]:
        t = counter["total"] or 1
        lines.append(f"- `{rule}` total=`{counter['total']}` oracle_canonical=`{counter['oracle_response_canonical']/t:.3f}` close_over=`{counter['close_over_action']/t:.3f}` ack_over=`{counter['ack_over_action']/t:.3f}`")
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
