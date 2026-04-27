#!/usr/bin/env python3
"""Build fulfillment-delivery baseline/skill/gold-guided replay inputs.

Gold/oracle labels are intentionally retained as JSON metadata for analysis,
while baseline and skill prompt strings are checked to avoid direct label
leakage. Gold-guided prompts append labels by design and are only for
upper-bound experiments.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[2]

REPLAY = ROOT / "flow_skill_policy_v22" / "replay"
SKILL_PROMPT = ROOT / "flow_skill_policy_v22" / "skills" / "fulfillment_delivery_policy_v22" / "skill_prompt.md"
OUT = ROOT / "replay_run_effect_v1"
INPUTS = OUT / "inputs"
REPORTS = OUT / "reports"

REQUIRED = [
    REPLAY / "fulfillment_delivery_stable_baseline_inputs.jsonl",
    REPLAY / "fulfillment_delivery_stable_skill_inputs.jsonl",
    REPLAY / "fulfillment_delivery_action_baseline_inputs.jsonl",
    REPLAY / "fulfillment_delivery_action_skill_inputs.jsonl",
    REPLAY / "fulfillment_delivery_challenge_baseline_inputs.jsonl",
    REPLAY / "fulfillment_delivery_challenge_skill_inputs.jsonl",
    REPLAY / "fulfillment_delivery_stable_replay.jsonl",
    REPLAY / "fulfillment_delivery_action_focused_replay.jsonl",
    REPLAY / "fulfillment_delivery_challenge_replay.jsonl",
    SKILL_PROMPT,
]

LEAK_MARKERS = [
    "gold_response_solution",
    "oracle_response_solution",
    "gold_dialogue_agree_solution",
    "oracle_dialogue_agree_solution",
    "gold_oracle_relation",
    "流程参考标签",
    "训练师标注 ResponseSolution",
    "策略 oracle ResponseSolution",
    "target_parse_error",
    "target label",
    "gold label",
    "oracle label",
]


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
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


def check_required() -> None:
    missing = [path for path in REQUIRED if not path.exists()]
    REPORTS.mkdir(parents=True, exist_ok=True)
    if missing:
        lines = ["# Missing Files", "", "| missing_file | blocking_level |", "|---|---|"]
        lines.extend(f"| `{path}` | P0 |" for path in missing)
        (REPORTS / "missing_files.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise SystemExit(2)
    (REPORTS / "missing_files.md").write_text("无缺失。\n", encoding="utf-8")


def oracle_maps() -> Dict[str, Dict[str, Dict[str, Any]]]:
    groups = {
        "stable": REPLAY / "fulfillment_delivery_stable_replay.jsonl",
        "action": REPLAY / "fulfillment_delivery_action_focused_replay.jsonl",
        "challenge": REPLAY / "fulfillment_delivery_challenge_replay.jsonl",
    }
    return {name: {row["sample_id"]: row for row in read_jsonl(path)} for name, path in groups.items()}


def normalize_row(row: Dict[str, Any], set_type: str, oracle_by_id: Dict[str, Dict[str, Any]], prompt: str) -> Dict[str, Any]:
    sid = row.get("sample_id", "")
    oracle = oracle_by_id.get(sid, {})
    return {
        "sample_id": sid,
        "set_type": set_type,
        "prompt": prompt,
        "gold_response_solution": row.get("gold_response_solution", oracle.get("gold_response_solution", "无")),
        "gold_dialogue_agree_solution": row.get("gold_dialogue_agree_solution", oracle.get("gold_dialogue_agree_solution", "无")),
        "oracle_response_solution": row.get("oracle_response_solution", oracle.get("oracle_response_solution", "无")),
        "oracle_dialogue_agree_solution": row.get("oracle_dialogue_agree_solution", oracle.get("oracle_dialogue_agree_solution", "无")),
        "oracle_rule_id": row.get("oracle_rule_id", oracle.get("oracle_rule_id", "")),
        "gold_oracle_relation": oracle.get("gold_oracle_relation", row.get("gold_oracle_relation", "")),
        "scene": row.get("scene", oracle.get("scene", "")),
        "last_user_query": row.get("last_user_query", oracle.get("last_user_query", "")),
    }


def gold_guided_prompt(base_prompt: str, row: Dict[str, Any]) -> str:
    block = f"""

## 流程参考标签（仅用于离线 gold-guided upper-bound 实验）
- 训练师标注 ResponseSolution: {row['gold_response_solution']}
- 训练师标注 DialogueAgreeSolution: {row['gold_dialogue_agree_solution']}
- 策略 oracle ResponseSolution: {row['oracle_response_solution']}
- 策略 oracle DialogueAgreeSolution: {row['oracle_dialogue_agree_solution']}
- 规则编号: {row['oracle_rule_id']}

请优先保证输出 JSON 中的 ResponseSolution / DialogueAgreeSolution 与上述流程参考标签一致；如果 gold 与 oracle 不一致，优先使用训练师标注 gold。Response 可自然生成，但不能改变方案字段。
"""
    return base_prompt.rstrip() + block


def merge_inputs(stable_path: Path, action_path: Path, oracle: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    for set_type, path in [("stable", stable_path), ("action", action_path)]:
        for row in read_jsonl(path):
            sid = row.get("sample_id")
            if not sid or sid in seen:
                continue
            seen.add(sid)
            rows.append(normalize_row(row, set_type, oracle[set_type], row.get("prompt", "")))
    return rows


def challenge_inputs(path: Path, oracle: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    return [normalize_row(row, "challenge", oracle["challenge"], row.get("prompt", "")) for row in read_jsonl(path)]


def prompt_leaks(rows: List[Dict[str, Any]]) -> List[Tuple[str, List[str]]]:
    out = []
    for row in rows:
        prompt = row.get("prompt", "")
        lower = prompt.lower()
        hits = [marker for marker in LEAK_MARKERS if marker.lower() in lower]
        if hits:
            out.append((row.get("sample_id", ""), hits))
    return out


def distribution(rows: List[Dict[str, Any]], key: str, limit: int = 20) -> List[str]:
    counter = Counter(row.get(key, "") for row in rows)
    return [f"- `{name}`: `{count}`" for name, count in counter.most_common(limit)]


def avg_len(rows: List[Dict[str, Any]]) -> int:
    return int(mean([len(row.get("prompt", "")) for row in rows])) if rows else 0


def build() -> None:
    check_required()
    INPUTS.mkdir(parents=True, exist_ok=True)
    oracle = oracle_maps()
    baseline = merge_inputs(
        REPLAY / "fulfillment_delivery_stable_baseline_inputs.jsonl",
        REPLAY / "fulfillment_delivery_action_baseline_inputs.jsonl",
        oracle,
    )
    skill = merge_inputs(
        REPLAY / "fulfillment_delivery_stable_skill_inputs.jsonl",
        REPLAY / "fulfillment_delivery_action_skill_inputs.jsonl",
        oracle,
    )
    # Gold-guided uses the skill prompt variant as base, then appends labels.
    gold_guided = [dict(row, prompt=gold_guided_prompt(row["prompt"], row)) for row in skill]
    challenge_baseline = challenge_inputs(REPLAY / "fulfillment_delivery_challenge_baseline_inputs.jsonl", oracle)
    challenge_skill = challenge_inputs(REPLAY / "fulfillment_delivery_challenge_skill_inputs.jsonl", oracle)
    challenge_gold = [dict(row, prompt=gold_guided_prompt(row["prompt"], row)) for row in challenge_skill]

    outputs = {
        "FD_BASELINE_INPUTS.jsonl": baseline,
        "FD_SKILL_INPUTS.jsonl": skill,
        "FD_GOLD_GUIDED_INPUTS.jsonl": gold_guided,
        "FD_CHALLENGE_BASELINE_INPUTS.jsonl": challenge_baseline,
        "FD_CHALLENGE_SKILL_INPUTS.jsonl": challenge_skill,
        "FD_CHALLENGE_GOLD_GUIDED_INPUTS.jsonl": challenge_gold,
    }
    for name, rows in outputs.items():
        write_jsonl(INPUTS / name, rows)

    b_leaks = prompt_leaks(baseline)
    s_leaks = prompt_leaks(skill)
    g_leaks = prompt_leaks(gold_guided)
    skill_inserted = sum("【履约配送流程规则 v22】" in row.get("prompt", "") for row in skill)
    set_counter = Counter(row["set_type"] for row in baseline + challenge_baseline)
    report = [
        "# Input Build Report",
        "",
        "## Counts",
        f"- baseline_main_count: `{len(baseline)}`",
        f"- skill_main_count: `{len(skill)}`",
        f"- gold_guided_main_count: `{len(gold_guided)}`",
        f"- challenge_baseline_count: `{len(challenge_baseline)}`",
        f"- challenge_skill_count: `{len(challenge_skill)}`",
        f"- challenge_gold_guided_count: `{len(challenge_gold)}`",
        f"- stable/action/challenge_distribution: `{dict(set_counter)}`",
        "",
        "## ResponseSolution Distribution (main baseline)",
        *distribution(baseline, "gold_response_solution"),
        "",
        "## DialogueAgreeSolution",
        f"- main_gold_dialogue_agree_non_empty: `{sum(row['gold_dialogue_agree_solution'] != '无' for row in baseline)}`",
        f"- main_oracle_dialogue_agree_non_empty: `{sum(row['oracle_dialogue_agree_solution'] != '无' for row in baseline)}`",
        "",
        "## Prompt Leakage",
        f"- baseline_prompt_has_gold_or_oracle: `{len(b_leaks)}`",
        f"- skill_prompt_has_gold_or_oracle: `{len(s_leaks)}`",
        f"- gold_guided_prompt_has_gold_or_oracle: `{len(g_leaks)}`",
        "- Note: gold-guided leaks are expected by design; baseline/skill should be 0.",
        "",
        "## Prompt Length",
        f"- baseline_avg_prompt_len: `{avg_len(baseline)}`",
        f"- skill_avg_prompt_len: `{avg_len(skill)}`",
        f"- gold_guided_avg_prompt_len: `{avg_len(gold_guided)}`",
        f"- skill_prompt_inserted_success_count: `{skill_inserted}`",
        "",
        "## Gold-Guided Base Choice",
        "- Gold-guided prompts use the skill-prompt variant as base, then append the reference-label block. They are upper-bound prompts, not formal effect metrics.",
    ]
    if b_leaks or s_leaks:
        report.extend(["", "## Leakage Examples"])
        for sid, hits in (b_leaks + s_leaks)[:30]:
            report.append(f"- `{sid}` hits=`{hits}`")
    (REPORTS / "input_build_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
