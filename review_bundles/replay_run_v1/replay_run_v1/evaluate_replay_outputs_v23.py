#!/usr/bin/env python3
"""Evaluate fulfillment-delivery replay outputs with stricter v23 metrics."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flow_skill_policy_v22.common import canonical_components, read_jsonl, relation, write_jsonl  # noqa: E402


STRONG_CONFIRMATION = {
    "取消订单",
    "小象单商品退款-xx%",
    "小象整单申请退款",
    "会员卡退款",
    "操作赔付-优惠券-xx元",
    "操作赔付-运费券-3元",
}


def _is_none(value: Any) -> bool:
    return value in (None, "", "无")


def _solution_text(value: Any) -> str:
    if value is None:
        return "无"
    text = str(value).strip()
    return text if text else "无"


def _canonical_set(value: Any) -> set[str]:
    if _is_none(value):
        return set()
    return set(canonical_components(value))


def _canonical_match(pred: Any, expected: Any) -> bool:
    pred = _solution_text(pred)
    expected = _solution_text(expected)
    return relation(pred, expected) in {"same", "canonical_same"}


def _strong(value: Any) -> bool:
    return bool(_canonical_set(value) & STRONG_CONFIRMATION)


def _parse_output_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    raw_output = row.get("raw_output")
    if isinstance(row.get("output"), str):
        raw_output = row.get("output")
        try:
            payload = json.loads(row["output"])
            if isinstance(payload, dict):
                parsed.update(payload)
        except json.JSONDecodeError:
            parsed["parse_error"] = "output_json_parse_error"
    for key in ("Response", "ResponseSolution", "DialogueAgreeSolution"):
        if key in row:
            parsed[key] = row.get(key)
    parsed.setdefault("Response", "")
    parsed["ResponseSolution"] = _solution_text(parsed.get("ResponseSolution"))
    parsed["DialogueAgreeSolution"] = _solution_text(parsed.get("DialogueAgreeSolution"))
    parsed.setdefault("parse_error", row.get("parse_error", ""))
    parsed["raw_output"] = raw_output if raw_output is not None else row.get("output", "")
    return parsed


def _load_outputs(path: Path) -> Dict[str, Dict[str, Any]]:
    outputs: Dict[str, Dict[str, Any]] = {}
    if not path.exists():
        return outputs
    for row in read_jsonl(path):
        sid = row.get("sample_id")
        if not sid:
            continue
        parsed = _parse_output_row(row)
        parsed["sample_id"] = sid
        parsed["set_type"] = row.get("set_type", "")
        outputs[sid] = parsed
    return outputs


def _load_eligibility(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for row in read_jsonl(path):
        sid = row.get("sample_id")
        if sid:
            out[sid] = row
    return out


def _eligible_sets(row: Mapping[str, Any], eligibility: Mapping[str, Any]) -> Tuple[set[str], set[str]]:
    eligible = set()
    ineligible = set()
    for value in eligibility.get("eligible_solutions") or []:
        eligible.update(_canonical_set(value))
    for item in eligibility.get("ineligible_solutions") or []:
        if isinstance(item, dict):
            ineligible.update(_canonical_set(item.get("solution")))
        else:
            ineligible.update(_canonical_set(item))
    for value in row.get("forbidden_solutions") or []:
        ineligible.update(_canonical_set(value))
    return eligible, ineligible


def _is_ineligible_action(pred_solution: str, row: Mapping[str, Any], eligibility: Mapping[str, Any]) -> bool:
    pred_set = _canonical_set(pred_solution)
    if not pred_set:
        return False
    eligible, ineligible = _eligible_sets(row, eligibility)
    if pred_set & ineligible:
        return True
    if eligible and not (pred_set & eligible):
        # The prompt may contain many available-but-not-executable tools. If
        # current eligibility says a non-empty action is outside the eligible
        # set, flag it as ineligible rather than only looking at guard rows.
        return True
    return bool(row.get("oracle_decision_type") == "guard")


def _iter_bucket_keys(row: Mapping[str, Any]) -> Dict[str, str]:
    return {
        "gold_response_solution": _solution_text(row.get("gold_response_solution")),
        "oracle_response_solution": _solution_text(row.get("oracle_response_solution")),
        "oracle_rule_id": str(row.get("oracle_rule_id") or ""),
        "scene": str(row.get("scene") or ""),
    }


def _eval_rows(
    rows: Sequence[Dict[str, Any]],
    outputs: Mapping[str, Dict[str, Any]],
    set_type: str,
    eligibility_by_id: Mapping[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Counter, Dict[str, Counter]]:
    result_rows: List[Dict[str, Any]] = []
    counters: Counter = Counter()
    buckets: Dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        sid = row.get("sample_id")
        pred = outputs.get(sid or "", {})
        pred_solution = _solution_text(pred.get("ResponseSolution"))
        pred_agree = _solution_text(pred.get("DialogueAgreeSolution"))
        gold_solution = _solution_text(row.get("gold_response_solution"))
        oracle_solution = _solution_text(row.get("oracle_response_solution"))
        gold_agree = _solution_text(row.get("gold_dialogue_agree_solution"))
        oracle_agree = _solution_text(row.get("oracle_dialogue_agree_solution"))
        cur = row.get("current_turn_intent") or {}
        eligibility = eligibility_by_id.get(sid or "", {})
        pred_action = pred_solution != "无"
        gold_action = gold_solution != "无"
        oracle_action = oracle_solution != "无"
        gold_match = _canonical_match(pred_solution, gold_solution)
        oracle_match = _canonical_match(pred_solution, oracle_solution)
        agree_exact = pred_agree == gold_agree
        strong_pred = _strong(pred_agree)
        strong_expected = _strong(gold_agree) or _strong(oracle_agree)
        close_ack_transfer = bool(cur.get("is_close_or_thanks") or cur.get("is_ack_only") or cur.get("is_transfer_only"))
        item = {
            "sample_id": sid,
            "set_type": set_type,
            "oracle_rule_id": row.get("oracle_rule_id"),
            "gold_response_solution": gold_solution,
            "oracle_response_solution": oracle_solution,
            "pred_response_solution": pred_solution,
            "gold_dialogue_agree_solution": gold_agree,
            "oracle_dialogue_agree_solution": oracle_agree,
            "pred_dialogue_agree_solution": pred_agree,
            "gold_response_canonical_match": gold_match,
            "oracle_response_canonical_match": oracle_match,
            "pred_action": pred_action,
            "gold_action": gold_action,
            "oracle_action": oracle_action,
            "stable_gold_or_oracle_no_action": not gold_action and not oracle_action,
            "stable_over_action": pred_action and not gold_action and not oracle_action,
            "close_ack_over_action": close_ack_transfer and pred_action,
            "strong_confirm_over_trigger": strong_pred and not strong_expected,
            "dialogue_agree_exact_match": agree_exact,
            "dialogue_agree_strong_precision_hit": strong_pred and strong_expected,
            "ineligible_action": _is_ineligible_action(pred_solution, row, eligibility),
            "action_missing_gold": gold_action and not pred_action,
            "action_missing_oracle": oracle_action and not pred_action,
            "action_wrong": pred_action and not gold_match and not oracle_match,
            "challenge_closer_to_gold": gold_match and not oracle_match,
            "challenge_closer_to_oracle": oracle_match and not gold_match,
            "parse_error": pred.get("parse_error", "missing_output") if not pred else pred.get("parse_error", ""),
        }
        result_rows.append(item)
        counters["total"] += 1
        counters["has_output"] += int(bool(pred))
        for key in [
            "gold_response_canonical_match",
            "oracle_response_canonical_match",
            "stable_over_action",
            "close_ack_over_action",
            "strong_confirm_over_trigger",
            "dialogue_agree_exact_match",
            "dialogue_agree_strong_precision_hit",
            "ineligible_action",
            "action_missing_gold",
            "action_missing_oracle",
            "action_wrong",
            "challenge_closer_to_gold",
            "challenge_closer_to_oracle",
        ]:
            counters[key] += int(bool(item[key]))
        counters["stable_gold_or_oracle_no_action"] += int(item["stable_gold_or_oracle_no_action"])
        counters["pred_action"] += int(pred_action)
        counters["gold_action"] += int(gold_action)
        counters["oracle_action"] += int(oracle_action)
        counters["pred_strong_agree"] += int(strong_pred)
        counters["expected_strong_agree"] += int(strong_expected)
        for bucket_name, bucket_value in _iter_bucket_keys(row).items():
            prefix = f"{bucket_name}={bucket_value}"
            buckets[prefix]["total"] += 1
            buckets[prefix]["gold_match"] += int(gold_match)
            buckets[prefix]["oracle_match"] += int(oracle_match)
            buckets[prefix]["missing_gold"] += int(item["action_missing_gold"])
            buckets[prefix]["missing_oracle"] += int(item["action_missing_oracle"])
            buckets[prefix]["wrong"] += int(item["action_wrong"])
    return result_rows, counters, buckets


def _rate(num: int, den: int) -> float:
    return 0.0 if den <= 0 else num / den


def _metrics(stable: Counter, action: Counter, challenge: Counter) -> Dict[str, Any]:
    stable_total = stable["total"]
    stable_no_den = stable["stable_gold_or_oracle_no_action"]
    stable_strong_den = stable["pred_strong_agree"]
    action_total = action["total"]
    action_gold_den = action["gold_action"]
    action_oracle_den = action["oracle_action"]
    action_pred_den = action["pred_action"]
    challenge_total = challenge["total"]
    return {
        "stable_total": stable_total,
        "stable_gold_response_canonical_match_rate": _rate(stable["gold_response_canonical_match"], stable_total),
        "stable_oracle_response_canonical_match_rate": _rate(stable["oracle_response_canonical_match"], stable_total),
        "stable_no_action_precision": _rate(stable_no_den - stable["stable_over_action"], stable_no_den),
        "stable_over_action_rate": _rate(stable["stable_over_action"], stable_no_den),
        "close_ack_over_action_rate": _rate(stable["close_ack_over_action"], stable_total),
        "strong_confirm_over_trigger_rate": _rate(stable["strong_confirm_over_trigger"], stable_total),
        "dialogue_agree_exact_match_rate": _rate(stable["dialogue_agree_exact_match"], stable_total),
        "dialogue_agree_precision_for_strong_confirmation": _rate(stable["dialogue_agree_strong_precision_hit"], stable_strong_den),
        "stable_ineligible_action_rate": _rate(stable["ineligible_action"], stable_total),
        "action_total": action_total,
        "action_trigger_rate": _rate(action["pred_action"], action_total),
        "action_gold_match_rate": _rate(action["gold_response_canonical_match"], action_total),
        "action_oracle_match_rate": _rate(action["oracle_response_canonical_match"], action_total),
        "action_missing_gold_rate": _rate(action["action_missing_gold"], action_gold_den),
        "action_missing_oracle_rate": _rate(action["action_missing_oracle"], action_oracle_den),
        "action_wrong_rate": _rate(action["action_wrong"], action_pred_den),
        "action_ineligible_action_rate": _rate(action["ineligible_action"], action_total),
        "challenge_total": challenge_total,
        "challenge_closer_to_gold": challenge["challenge_closer_to_gold"],
        "challenge_closer_to_oracle": challenge["challenge_closer_to_oracle"],
    }


def _format_metrics(metrics: Mapping[str, Any], title: str) -> List[str]:
    lines = [f"## {title}"]
    for key, value in metrics.items():
        if isinstance(value, float):
            lines.append(f"- {key}: `{value:.4f}`")
        else:
            lines.append(f"- {key}: `{value}`")
    return lines


def _bucket_lines(buckets: Mapping[str, Counter], title: str, limit: int = 80) -> List[str]:
    lines = ["", f"## {title}", "| bucket | total | gold_match | oracle_match | missing_gold | missing_oracle | wrong |", "|---|---:|---:|---:|---:|---:|---:|"]
    for bucket, counter in sorted(buckets.items(), key=lambda kv: kv[1]["total"], reverse=True)[:limit]:
        total = counter["total"] or 1
        lines.append(
            f"| `{bucket}` | {counter['total']} | {_rate(counter['gold_match'], total):.3f} | "
            f"{_rate(counter['oracle_match'], total):.3f} | {_rate(counter['missing_gold'], total):.3f} | "
            f"{_rate(counter['missing_oracle'], total):.3f} | {_rate(counter['wrong'], total):.3f} |"
        )
    return lines


def evaluate(args: argparse.Namespace) -> Tuple[List[Dict[str, Any]], Dict[str, Any], str]:
    outputs = _load_outputs(Path(args.model_outputs))
    if not outputs:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text("", encoding="utf-8")
        text = (
            "# Replay Eval Report v23\n\n"
            f"No model outputs found at `{args.model_outputs}`. "
            "Generated an empty result file; no metrics are fabricated.\n"
        )
        Path(args.report).write_text(text, encoding="utf-8")
        return [], {}, text
    eligibility = _load_eligibility(Path(args.eligibility_results))
    stable_rows = list(read_jsonl(Path(args.stable_oracle)))
    action_rows = list(read_jsonl(Path(args.action_oracle)))
    challenge_rows = list(read_jsonl(Path(args.challenge_oracle)))
    stable_eval, stable_c, stable_buckets = _eval_rows(stable_rows, outputs, "stable", eligibility)
    action_eval, action_c, action_buckets = _eval_rows(action_rows, outputs, "action", eligibility)
    challenge_eval, challenge_c, challenge_buckets = _eval_rows(challenge_rows, outputs, "challenge", eligibility)
    metrics = _metrics(stable_c, action_c, challenge_c)
    all_rows = stable_eval + action_eval + challenge_eval
    write_jsonl(Path(args.output), all_rows)
    label = args.label or Path(args.model_outputs).stem
    lines = [
        "# Replay Eval Report v23",
        "",
        f"- label: `{label}`",
        f"- model_outputs: `{args.model_outputs}`",
        f"- parsed_outputs: `{len(outputs)}`",
        f"- eligibility_results_loaded: `{len(eligibility)}`",
        "",
        "主指标只看 stable；action-focused 单独看动作召回；challenge 只做 gold/oracle conflict 分析。",
        "",
        *(_format_metrics(metrics, f"{label} Metrics")),
        "",
        "## Baseline / Skill / Delta",
        "This single-run report contains one side only. Use `compare_baseline_skill.py` to produce baseline, skill, and skill-baseline deltas.",
    ]
    lines.extend(_bucket_lines(action_buckets, "Action-Focused Buckets"))
    lines.extend(_bucket_lines(challenge_buckets, "Challenge Buckets"))
    report_text = "\n".join(lines) + "\n"
    Path(args.report).write_text(report_text, encoding="utf-8")
    summary = {"label": label, **metrics}
    summary_path = Path(args.report).with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return all_rows, metrics, report_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stable-oracle", required=True)
    parser.add_argument("--action-oracle", required=True)
    parser.add_argument("--challenge-oracle", required=True)
    parser.add_argument("--model-outputs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--eligibility-results", default="flow_skill_policy_v22/outputs/eligibility_results_v22.jsonl")
    parser.add_argument("--label", default="")
    args = parser.parse_args()
    evaluate(args)


if __name__ == "__main__":
    main()
