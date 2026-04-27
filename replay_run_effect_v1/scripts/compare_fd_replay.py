#!/usr/bin/env python3
"""Compare FD baseline, skill, and gold-guided eval results."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def rate(num: int, den: int) -> float:
    return 0.0 if den <= 0 else num / den


def summarize(rows: Iterable[Mapping[str, Any]]) -> Dict[str, float]:
    c = Counter()
    for row in rows:
        set_type = row.get("set_type")
        c["global_total"] += 1
        c["global_strong_over"] += int(bool(row.get("strong_confirm_over_trigger")))
        c["global_close_ack"] += int(bool(row.get("close_ack_over_action")))
        if set_type == "stable":
            c["stable_total"] += 1
            c["stable_no_den"] += int(not row.get("gold_action") and not row.get("oracle_action"))
            c["stable_over_action"] += int(bool(row.get("over_action")))
            c["stable_no_correct"] += int((not row.get("gold_action") and not row.get("oracle_action")) and not row.get("pred_action"))
        if set_type == "action":
            c["action_total"] += 1
            c["action_gold_canon"] += int(bool(row.get("gold_canonical_match")))
            c["action_oracle_canon"] += int(bool(row.get("oracle_canonical_match")))
            c["action_gold_den"] += int(bool(row.get("gold_action")))
            c["action_missing_gold"] += int(bool(row.get("missing_gold")))
            c["action_pred"] += int(bool(row.get("pred_action")))
            c["action_wrong"] += int(bool(row.get("wrong_action")))
    return {
        "stable_no_action_precision": rate(c["stable_no_correct"], c["stable_no_den"]),
        "stable_over_action_rate": rate(c["stable_over_action"], c["stable_no_den"]),
        "action_gold_canonical_match_rate": rate(c["action_gold_canon"], c["action_total"]),
        "action_oracle_canonical_match_rate": rate(c["action_oracle_canon"], c["action_total"]),
        "action_missing_gold_rate": rate(c["action_missing_gold"], c["action_gold_den"]),
        "action_wrong_rate": rate(c["action_wrong"], c["action_pred"]),
        "global_strong_confirm_over_trigger_rate": rate(c["global_strong_over"], c["global_total"]),
        "close_ack_over_action_rate": rate(c["global_close_ack"], c["global_total"]),
    }


def fmt(value: float) -> str:
    return f"{value:.4f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-result", required=True)
    parser.add_argument("--skill-result", required=True)
    parser.add_argument("--gold-guided-result", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    baseline = read_jsonl(Path(args.baseline_result))
    skill = read_jsonl(Path(args.skill_result))
    gold = read_jsonl(Path(args.gold_guided_result))
    if not baseline or not skill or not gold:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            "# FD Replay Compare Report\n\n缺少 baseline / skill / gold-guided 任一 eval result，无法比较。\n",
            encoding="utf-8",
        )
        return
    bm, sm, gm = summarize(baseline), summarize(skill), summarize(gold)
    keys = [
        "stable_no_action_precision",
        "stable_over_action_rate",
        "action_gold_canonical_match_rate",
        "action_oracle_canonical_match_rate",
        "action_missing_gold_rate",
        "action_wrong_rate",
        "global_strong_confirm_over_trigger_rate",
        "close_ack_over_action_rate",
    ]
    gate_notes = []
    if not (sm["action_gold_canonical_match_rate"] > bm["action_gold_canonical_match_rate"] or sm["action_oracle_canonical_match_rate"] > bm["action_oracle_canonical_match_rate"]):
        gate_notes.append("skill action gold/oracle canonical match 未高于 baseline。")
    if sm["action_missing_gold_rate"] > bm["action_missing_gold_rate"]:
        gate_notes.append("skill action_missing_gold_rate 高于 baseline。")
    if sm["stable_over_action_rate"] > bm["stable_over_action_rate"] + 0.03:
        gate_notes.append("skill stable_over_action_rate 明显高于 baseline。")
    if sm["global_strong_confirm_over_trigger_rate"] > bm["global_strong_confirm_over_trigger_rate"]:
        gate_notes.append("skill strong confirm over-trigger 高于 baseline。")
    if sm["close_ack_over_action_rate"] > bm["close_ack_over_action_rate"]:
        gate_notes.append("skill close_ack_over_action_rate 高于 baseline。")
    if gm["action_gold_canonical_match_rate"] <= bm["action_gold_canonical_match_rate"]:
        gate_notes.append("gold-guided gold match 未明显高于 baseline，模型格式/方案遵循可能有问题。")
    lines = [
        "# FD Replay Compare Report",
        "",
        "## Baseline vs Skill vs Gold-Guided",
        "| metric | baseline | skill | skill-baseline | gold_guided | gold_guided-skill |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key in keys:
        lines.append(f"| `{key}` | {fmt(bm[key])} | {fmt(sm[key])} | {fmt(sm[key]-bm[key])} | {fmt(gm[key])} | {fmt(gm[key]-sm[key])} |")
    lines.extend(["", "## Interpretation"])
    lines.append("- 如果 gold-guided 仍无法匹配 gold，说明主模型格式遵循或方案输出能力有问题。")
    lines.append("- 如果 gold-guided 很高而 skill 不高，说明 skill policy 信息不足或模型没有从 skill 中推断动作。")
    lines.append("- 如果 skill 接近 gold-guided，说明 skill prompt 对流程动作有效。")
    lines.extend(["", "## Gate"])
    if gate_notes:
        lines.append("- HOLD")
        lines.extend(f"- {note}" for note in gate_notes)
    else:
        lines.append("- PASS")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
