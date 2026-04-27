#!/usr/bin/env python3
"""Evaluate FD baseline/skill/gold-guided model outputs when available."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from flow_skill_policy_v22.common import canonical_components, relation  # noqa: E402
from output_parser import parse_model_output_row  # noqa: E402


STRONG = {
    "取消订单",
    "小象单商品退款-xx%",
    "小象整单申请退款",
    "会员卡退款",
    "操作赔付-优惠券-xx元",
    "操作赔付-运费券-3元",
}


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def is_action(value: str) -> bool:
    return value not in ("", "无", None)


def canonical_match(pred: str, target: str) -> bool:
    return relation(pred or "无", target or "无") in {"same", "canonical_same"}


def is_strong(value: str) -> bool:
    return bool(set(canonical_components(value or "无")) & STRONG)


def rate(num: int, den: int) -> float:
    return 0.0 if den <= 0 else num / den


def output_map(path: Path) -> Dict[str, Dict[str, Any]]:
    out = {}
    for row in read_jsonl(path):
        sid = row.get("sample_id")
        if not sid:
            continue
        parsed = parse_model_output_row(row)
        parsed["sample_id"] = sid
        parsed["raw_row"] = row
        out[sid] = parsed
    return out


def eval_group(label: str, inputs: List[Dict[str, Any]], outputs: Dict[str, Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Counter, Dict[str, Counter]]:
    rows = []
    c = Counter()
    by_rule: Dict[str, Counter] = defaultdict(Counter)
    for item in inputs:
        sid = item.get("sample_id")
        pred = outputs.get(sid or "", {})
        parsed = bool(pred)
        pred_rs = str(pred.get("ResponseSolution", "无") or "无")
        pred_agree = str(pred.get("DialogueAgreeSolution", "无") or "无")
        gold_rs = str(item.get("gold_response_solution", "无") or "无")
        oracle_rs = str(item.get("oracle_response_solution", "无") or "无")
        gold_agree = str(item.get("gold_dialogue_agree_solution", "无") or "无")
        oracle_agree = str(item.get("oracle_dialogue_agree_solution", "无") or "无")
        gold_match = canonical_match(pred_rs, gold_rs)
        oracle_match = canonical_match(pred_rs, oracle_rs)
        gold_or_oracle_no_action = not is_action(gold_rs) and not is_action(oracle_rs)
        pred_action = is_action(pred_rs)
        strong_over = is_strong(pred_agree) and not (is_strong(gold_agree) or is_strong(oracle_agree))
        row = {
            "sample_id": sid,
            "label": label,
            "set_type": item.get("set_type"),
            "oracle_rule_id": item.get("oracle_rule_id"),
            "gold_response_solution": gold_rs,
            "oracle_response_solution": oracle_rs,
            "pred_response_solution": pred_rs,
            "gold_dialogue_agree_solution": gold_agree,
            "oracle_dialogue_agree_solution": oracle_agree,
            "pred_dialogue_agree_solution": pred_agree,
            "parsed_output": parsed,
            "parse_error": pred.get("parse_error", "missing_output") if not parsed else pred.get("parse_error", ""),
            "gold_response_canonical_match": gold_match,
            "oracle_response_canonical_match": oracle_match,
            "dialogue_agree_gold_exact": pred_agree == gold_agree,
            "dialogue_agree_oracle_exact": pred_agree == oracle_agree,
            "pred_action": pred_action,
            "gold_action": is_action(gold_rs),
            "oracle_action": is_action(oracle_rs),
            "over_action": pred_action and gold_or_oracle_no_action,
            "missing_gold_action": is_action(gold_rs) and not pred_action,
            "missing_oracle_action": is_action(oracle_rs) and not pred_action,
            "wrong_action": pred_action and not gold_match and not oracle_match,
            "strong_confirm_over_trigger": strong_over,
        }
        rows.append(row)
        c["total"] += 1
        c["parsed"] += int(parsed and not row["parse_error"])
        for key in [
            "gold_response_canonical_match",
            "oracle_response_canonical_match",
            "dialogue_agree_gold_exact",
            "dialogue_agree_oracle_exact",
            "pred_action",
            "over_action",
            "missing_gold_action",
            "missing_oracle_action",
            "wrong_action",
            "strong_confirm_over_trigger",
        ]:
            c[key] += int(row[key])
        c["gold_or_oracle_no_action"] += int(gold_or_oracle_no_action)
        c["gold_action"] += int(row["gold_action"])
        c["oracle_action"] += int(row["oracle_action"])
        rule = str(item.get("oracle_rule_id") or "")
        by_rule[rule]["total"] += 1
        by_rule[rule]["gold_match"] += int(gold_match)
        by_rule[rule]["oracle_match"] += int(oracle_match)
        by_rule[rule]["wrong_action"] += int(row["wrong_action"])
    return rows, c, by_rule


def metrics(c: Counter) -> Dict[str, Any]:
    total = c["total"]
    pred_action = c["pred_action"]
    no_action_den = c["gold_or_oracle_no_action"]
    return {
        "total": total,
        "parse_success_rate": rate(c["parsed"], total),
        "gold_response_canonical_match_rate": rate(c["gold_response_canonical_match"], total),
        "oracle_response_canonical_match_rate": rate(c["oracle_response_canonical_match"], total),
        "dialogue_agree_gold_exact_rate": rate(c["dialogue_agree_gold_exact"], total),
        "dialogue_agree_oracle_exact_rate": rate(c["dialogue_agree_oracle_exact"], total),
        "action_trigger_rate": rate(c["pred_action"], total),
        "no_action_precision": rate(no_action_den - c["over_action"], no_action_den),
        "over_action_rate": rate(c["over_action"], no_action_den),
        "missing_gold_action_rate": rate(c["missing_gold_action"], c["gold_action"]),
        "missing_oracle_action_rate": rate(c["missing_oracle_action"], c["oracle_action"]),
        "wrong_action_rate": rate(c["wrong_action"], pred_action),
        "strong_confirm_over_trigger_rate": rate(c["strong_confirm_over_trigger"], total),
    }


def delta_lines(base: Mapping[str, Any], skill: Mapping[str, Any], gold: Mapping[str, Any]) -> List[str]:
    keys = sorted(set(base) | set(skill) | set(gold))
    lines = ["| metric | baseline | skill | skill-baseline | gold_guided |", "|---|---:|---:|---:|---:|"]
    for key in keys:
        b = float(base.get(key, 0.0))
        s = float(skill.get(key, 0.0))
        g = float(gold.get(key, 0.0))
        lines.append(f"| `{key}` | {b:.4f} | {s:.4f} | {s-b:+.4f} | {g:.4f} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-input", default="replay_run_effect_v1/inputs/FD_BASELINE_INPUTS.jsonl")
    parser.add_argument("--skill-input", default="replay_run_effect_v1/inputs/FD_SKILL_INPUTS.jsonl")
    parser.add_argument("--gold-guided-input", default="replay_run_effect_v1/inputs/FD_GOLD_GUIDED_INPUTS.jsonl")
    parser.add_argument("--baseline-output", default="replay_run_effect_v1/model_outputs/FD_BASELINE_OUTPUTS.jsonl")
    parser.add_argument("--skill-output", default="replay_run_effect_v1/model_outputs/FD_SKILL_OUTPUTS.jsonl")
    parser.add_argument("--gold-guided-output", default="replay_run_effect_v1/model_outputs/FD_GOLD_GUIDED_OUTPUTS.jsonl")
    parser.add_argument("--output", default="replay_run_effect_v1/eval/FD_EFFECT_eval_result.jsonl")
    parser.add_argument("--report", default="replay_run_effect_v1/eval/FD_EFFECT_eval_report.md")
    args = parser.parse_args()

    groups = {
        "baseline": (read_jsonl(Path(args.baseline_input)), output_map(Path(args.baseline_output))),
        "skill": (read_jsonl(Path(args.skill_input)), output_map(Path(args.skill_output))),
        "gold_guided": (read_jsonl(Path(args.gold_guided_input)), output_map(Path(args.gold_guided_output))),
    }
    if not any(outputs for _, outputs in groups.values()):
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text("", encoding="utf-8")
        Path(args.report).write_text(
            "# FD Effect Eval Report\n\nNo model outputs found. Evaluation scripts are ready; no metrics are fabricated.\n",
            encoding="utf-8",
        )
        return
    all_rows: List[Dict[str, Any]] = []
    all_metrics: Dict[str, Dict[str, Any]] = {}
    by_rule_all: Dict[str, Dict[str, Counter]] = {}
    for label, (inputs, outputs) in groups.items():
        rows, counters, by_rule = eval_group(label, inputs, outputs)
        all_rows.extend(rows)
        all_metrics[label] = metrics(counters)
        by_rule_all[label] = by_rule
    write_jsonl(Path(args.output), all_rows)
    lines = ["# FD Effect Eval Report", "", "## Metrics", *delta_lines(all_metrics["baseline"], all_metrics["skill"], all_metrics["gold_guided"])]
    lines.extend(["", "## By Oracle Rule (skill)", "| oracle_rule_id | total | gold_match | oracle_match | wrong_action |", "|---|---:|---:|---:|---:|"])
    for rule, counter in sorted(by_rule_all["skill"].items(), key=lambda kv: kv[1]["total"], reverse=True)[:50]:
        total = counter["total"] or 1
        lines.append(f"| `{rule}` | {counter['total']} | {rate(counter['gold_match'], total):.3f} | {rate(counter['oracle_match'], total):.3f} | {rate(counter['wrong_action'], total):.3f} |")
    Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
