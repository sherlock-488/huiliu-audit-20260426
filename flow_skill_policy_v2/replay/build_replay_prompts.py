#!/usr/bin/env python3
"""Build baseline and skill prompt inputs for model replay."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v2.common import V2_ROOT, ensure_dirs, read_jsonl, write_jsonl


def insert_skill_prompt(prompt: str, skill_prompt: str) -> str:
    text = prompt or ""
    block = "\n\n### 流程操作规则（Skill）\n" + skill_prompt.strip() + "\n"
    marker = "### 系统信号"
    idx = text.find(marker)
    if idx != -1:
        next_idx = text.find("\n### ", idx + len(marker))
        if next_idx != -1:
            return text[:next_idx] + block + text[next_idx:]
    marker = "## 你查询到的方案列表"
    idx = text.find(marker)
    if idx != -1:
        next_idx = text.find("\n### ", idx + len(marker))
        if next_idx != -1:
            return text[:next_idx] + block + text[next_idx:]
    return block + text


def _build(oracle_path: Path, skill_prompt_path: Path, baseline_out: Path, skill_out: Path) -> tuple[int, int]:
    skill_prompt = skill_prompt_path.read_text(encoding="utf-8")
    baseline_rows = []
    skill_rows = []
    for row in read_jsonl(oracle_path):
        base = {
            "sample_id": row.get("sample_id"),
            "prompt": row.get("input_without_target", ""),
            "gold_response_solution": row.get("gold_response_solution"),
            "gold_dialogue_agree_solution": row.get("gold_dialogue_agree_solution"),
            "oracle_response_solution": row.get("oracle_response_solution"),
            "oracle_dialogue_agree_solution": row.get("oracle_dialogue_agree_solution"),
            "oracle_rule_id": row.get("oracle_rule_id"),
        }
        baseline_rows.append(base)
        skill_item = dict(base)
        skill_item["prompt"] = insert_skill_prompt(base["prompt"], skill_prompt)
        skill_rows.append(skill_item)
    return write_jsonl(baseline_out, baseline_rows), write_jsonl(skill_out, skill_rows)


def main() -> None:
    ensure_dirs()
    fd_base, fd_skill = _build(
        V2_ROOT / "replay" / "fulfillment_delivery_oracle.jsonl",
        V2_ROOT / "skills" / "fulfillment_delivery_policy_v2" / "skill_prompt.md",
        V2_ROOT / "replay" / "fulfillment_delivery_baseline_inputs.jsonl",
        V2_ROOT / "replay" / "fulfillment_delivery_skill_inputs.jsonl",
    )
    rq_base, rq_skill = _build(
        V2_ROOT / "replay" / "receipt_quality_oracle.jsonl",
        V2_ROOT / "skills" / "receipt_quality_policy_v2" / "skill_prompt.md",
        V2_ROOT / "replay" / "receipt_quality_baseline_inputs.jsonl",
        V2_ROOT / "replay" / "receipt_quality_skill_inputs.jsonl",
    )
    (V2_ROOT / "outputs" / "reports" / "replay_prompt_report.md").write_text(
        "\n".join(
            [
                "# Replay Prompt Report",
                "",
                f"- fulfillment_delivery_baseline_inputs: `{fd_base}`",
                f"- fulfillment_delivery_skill_inputs: `{fd_skill}`",
                f"- receipt_quality_baseline_inputs: `{rq_base}`",
                f"- receipt_quality_skill_inputs: `{rq_skill}`",
                "",
                "Skill prompt 插入在原 prompt 的系统信号块之后，不包含 target/gold label。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
