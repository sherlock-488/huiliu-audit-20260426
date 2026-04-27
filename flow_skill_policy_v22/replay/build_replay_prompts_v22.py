#!/usr/bin/env python3
"""Build baseline/skill replay input prompts for v22."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v22.common import V22_REPORTS, V22_ROOT, ensure_dirs, read_jsonl, write_jsonl


def insert_skill_prompt(prompt: str, skill_prompt: str) -> str:
    block = "\n\n### 流程操作规则（Skill）\n" + skill_prompt.strip() + "\n"
    text = prompt or ""
    for marker in ["### 系统信号", "## 你查询到的方案列表"]:
        idx = text.find(marker)
        if idx != -1:
            next_idx = text.find("\n### ", idx + len(marker))
            if next_idx != -1:
                return text[:next_idx] + block + text[next_idx:]
    return block + text


def _build(prefix: str, set_type: str, skill_prompt: str) -> tuple[int, int]:
    source = V22_ROOT / "replay" / f"{prefix}_{set_type}_replay.jsonl"
    rows = list(read_jsonl(source)) if source.exists() else []
    baseline = []
    skill = []
    for r in rows:
        base = {
            "sample_id": r.get("sample_id"),
            "prompt": r.get("input_without_target", ""),
            "gold_response_solution": r.get("gold_response_solution"),
            "gold_dialogue_agree_solution": r.get("gold_dialogue_agree_solution"),
            "oracle_response_solution": r.get("oracle_response_solution"),
            "oracle_dialogue_agree_solution": r.get("oracle_dialogue_agree_solution"),
            "oracle_rule_id": r.get("oracle_rule_id"),
            "set_type": "action" if set_type == "action_focused" else set_type,
        }
        baseline.append(base)
        s = dict(base)
        s["prompt"] = insert_skill_prompt(s["prompt"], skill_prompt)
        skill.append(s)
    out_set = "action" if set_type == "action_focused" else set_type
    b = write_jsonl(V22_ROOT / "replay" / f"{prefix}_{out_set}_baseline_inputs.jsonl", baseline)
    s = write_jsonl(V22_ROOT / "replay" / f"{prefix}_{out_set}_skill_inputs.jsonl", skill)
    return b, s


def main() -> None:
    ensure_dirs()
    fd_prompt = (V22_ROOT / "skills" / "fulfillment_delivery_policy_v22" / "skill_prompt.md").read_text(encoding="utf-8")
    rq_prompt = (V22_ROOT / "skills" / "receipt_quality_policy_v22" / "skill_prompt.md").read_text(encoding="utf-8")
    counts = {}
    for set_type in ["stable", "action_focused", "challenge"]:
        counts[f"fd_{set_type}"] = _build("fulfillment_delivery", set_type, fd_prompt)
        counts[f"rq_{set_type}"] = _build("receipt_quality", set_type, rq_prompt)
    lines = ["# Replay Prompt v22 Report", ""]
    for key, (b, s) in counts.items():
        lines.append(f"- `{key}` baseline/skill: `{b}` / `{s}`")
    lines.append("\nNo target/gold/oracle labels are inserted into prompt text; labels are separate metadata fields.")
    (V22_REPORTS / "replay_prompt_v22_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
