#!/usr/bin/env python3
"""Compare baseline and skill replay eval results."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flow_skill_policy_v22.common import read_jsonl  # noqa: E402


def _rate(num: int, den: int) -> float:
    return 0.0 if den <= 0 else num / den


def _load(path: Path) -> list[dict[str, Any]]:
    return list(read_jsonl(path)) if path.exists() else []


def _summarize(rows: Iterable[Mapping[str, Any]]) -> tuple[Dict[str, float], Dict[str, Counter]]:
    counters = Counter()
    by_rule: Dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        set_type = row.get("set_type")
        rule = str(row.get("oracle_rule_id") or "")
        if set_type == "stable":
            counters["stable_total"] += 1
            counters["stable_gold_match"] += int(bool(row.get("gold_response_canonical_match")))
            counters["stable_oracle_match"] += int(bool(row.get("oracle_response_canonical_match")))
            counters["stable_no_action_den"] += int(bool(row.get("stable_gold_or_oracle_no_action")))
            counters["stable_over_action"] += int(bool(row.get("stable_over_action")))
            counters["close_ack_over_action"] += int(bool(row.get("close_ack_over_action")))
            counters["strong_confirm_over_trigger"] += int(bool(row.get("strong_confirm_over_trigger")))
        elif set_type == "action":
            counters["action_total"] += 1
            counters["action_pred"] += int(bool(row.get("pred_action")))
            counters["action_gold_match"] += int(bool(row.get("gold_response_canonical_match")))
            counters["action_oracle_match"] += int(bool(row.get("oracle_response_canonical_match")))
            counters["action_gold_den"] += int(bool(row.get("gold_action")))
            counters["action_oracle_den"] += int(bool(row.get("oracle_action")))
            counters["action_missing_gold"] += int(bool(row.get("action_missing_gold")))
            counters["action_missing_oracle"] += int(bool(row.get("action_missing_oracle")))
            counters["action_wrong"] += int(bool(row.get("action_wrong")))
            counters["action_wrong_den"] += int(bool(row.get("pred_action")))
            by_rule[rule]["total"] += 1
            by_rule[rule]["gold_match"] += int(bool(row.get("gold_response_canonical_match")))
            by_rule[rule]["oracle_match"] += int(bool(row.get("oracle_response_canonical_match")))
            by_rule[rule]["missing_gold"] += int(bool(row.get("action_missing_gold")))
            by_rule[rule]["wrong"] += int(bool(row.get("action_wrong")))
    stable_total = counters["stable_total"]
    action_total = counters["action_total"]
    stable_no_den = counters["stable_no_action_den"]
    metrics = {
        "stable_gold_response_canonical_match_rate": _rate(counters["stable_gold_match"], stable_total),
        "stable_oracle_response_canonical_match_rate": _rate(counters["stable_oracle_match"], stable_total),
        "stable_no_action_precision": _rate(stable_no_den - counters["stable_over_action"], stable_no_den),
        "stable_over_action_rate": _rate(counters["stable_over_action"], stable_no_den),
        "close_ack_over_action_rate": _rate(counters["close_ack_over_action"], stable_total),
        "strong_confirm_over_trigger_rate": _rate(counters["strong_confirm_over_trigger"], stable_total),
        "action_trigger_rate": _rate(counters["action_pred"], action_total),
        "action_gold_match_rate": _rate(counters["action_gold_match"], action_total),
        "action_oracle_match_rate": _rate(counters["action_oracle_match"], action_total),
        "action_missing_gold_rate": _rate(counters["action_missing_gold"], counters["action_gold_den"]),
        "action_missing_oracle_rate": _rate(counters["action_missing_oracle"], counters["action_oracle_den"]),
        "action_wrong_rate": _rate(counters["action_wrong"], counters["action_wrong_den"]),
    }
    return metrics, by_rule


def _delta(skill: float, baseline: float) -> float:
    return skill - baseline


def _gate(metrics_b: Mapping[str, float], metrics_s: Mapping[str, float]) -> tuple[str, list[str]]:
    notes = []
    pass_gate = True
    if _delta(metrics_s["close_ack_over_action_rate"], metrics_b["close_ack_over_action_rate"]) > 0.01:
        pass_gate = False
        notes.append("close_ack_over_action_rate 上升超过 1%。")
    if metrics_s["strong_confirm_over_trigger_rate"] > 0.01:
        pass_gate = False
        notes.append("strong_confirm_over_trigger_rate 未接近 0。")
    if _delta(metrics_s["stable_over_action_rate"], metrics_b["stable_over_action_rate"]) > 0.03:
        pass_gate = False
        notes.append("stable_over_action_rate 明显上升。")
    if not (
        metrics_s["action_gold_match_rate"] > metrics_b["action_gold_match_rate"]
        or metrics_s["action_oracle_match_rate"] > metrics_b["action_oracle_match_rate"]
    ):
        pass_gate = False
        notes.append("action_gold_match_rate / action_oracle_match_rate 均未提升。")
    if _delta(metrics_s["action_wrong_rate"], metrics_b["action_wrong_rate"]) > 0.03:
        pass_gate = False
        notes.append("action_wrong_rate 明显上升。")
    return ("PASS" if pass_gate else "HOLD"), notes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    baseline_rows = _load(Path(args.baseline))
    skill_rows = _load(Path(args.skill))
    if not baseline_rows or not skill_rows:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            "# FD Baseline vs Skill Report\n\n"
            "缺少 baseline 或 skill eval result，无法比较。请先运行两组模型输出评估。\n",
            encoding="utf-8",
        )
        return
    b_metrics, b_rules = _summarize(baseline_rows)
    s_metrics, s_rules = _summarize(skill_rows)
    gate, gate_notes = _gate(b_metrics, s_metrics)
    lines = [
        "# FD Baseline vs Skill Report",
        "",
        f"- recommendation_gate: `{gate}`",
        "",
        "## Metrics",
        "| metric | baseline | skill | skill-baseline |",
        "|---|---:|---:|---:|",
    ]
    for key in sorted(b_metrics):
        lines.append(f"| `{key}` | {b_metrics[key]:.4f} | {s_metrics[key]:.4f} | {_delta(s_metrics[key], b_metrics[key]):+.4f} |")
    lines.extend(["", "## Gate Notes"])
    if gate_notes:
        lines.extend(f"- {note}" for note in gate_notes)
    else:
        lines.append("- 硬 gate 通过，可考虑进入小流量前的人工复核。")

    lines.extend(["", "## Oracle Rule Improvements", "| oracle_rule_id | baseline_oracle_match | skill_oracle_match | delta | total |", "|---|---:|---:|---:|---:|"])
    all_rules = sorted(set(b_rules) | set(s_rules))
    rows = []
    for rule in all_rules:
        bt = b_rules[rule]["total"] or 1
        st = s_rules[rule]["total"] or 1
        b_rate = b_rules[rule]["oracle_match"] / bt
        s_rate = s_rules[rule]["oracle_match"] / st
        rows.append((s_rate - b_rate, rule, b_rate, s_rate, max(b_rules[rule]["total"], s_rules[rule]["total"])))
    for delta, rule, b_rate, s_rate, total in sorted(rows, reverse=True)[:30]:
        lines.append(f"| `{rule}` | {b_rate:.3f} | {s_rate:.3f} | {delta:+.3f} | {total} |")
    lines.extend(["", "## Oracle Rule Regressions", "| oracle_rule_id | baseline_oracle_match | skill_oracle_match | delta | total |", "|---|---:|---:|---:|---:|"])
    for delta, rule, b_rate, s_rate, total in sorted(rows)[:30]:
        lines.append(f"| `{rule}` | {b_rate:.3f} | {s_rate:.3f} | {delta:+.3f} | {total} |")
    lines.extend(
        [
            "",
            "## Small Traffic Recommendation",
            "- 只有当 gate 为 PASS，且 action-focused 的 gold/oracle match 至少一个提升、stable 安全指标不退化时，才建议进入小流量实验。",
        ]
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
