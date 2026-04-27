#!/usr/bin/env python3
"""Build v21 stable/challenge replay sets and prompt inputs."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v21.common import V21_REPORTS, V21_ROOT, ensure_dirs, read_jsonl, top_counter, write_jsonl


def insert_skill_prompt(prompt: str, skill_prompt: str) -> str:
    block = "\n\n### 流程操作规则（Skill）\n" + skill_prompt.strip() + "\n"
    text = prompt or ""
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


def _split(oracle_path: Path, prefix: str, skill_prompt_path: Path) -> Dict[str, int]:
    rows = list(read_jsonl(oracle_path))
    stable = [r for r in rows if r.get("gold_oracle_relation") in {"same", "canonical_same"}]
    challenge = [r for r in rows if r.get("gold_oracle_relation") not in {"same", "canonical_same"}]
    stable_path = V21_ROOT / "replay" / f"{prefix}_stable_replay.jsonl"
    challenge_path = V21_ROOT / "replay" / f"{prefix}_challenge_replay.jsonl"
    write_jsonl(stable_path, stable)
    write_jsonl(challenge_path, challenge)
    skill_prompt = skill_prompt_path.read_text(encoding="utf-8")
    for kind, subset in [("stable", stable), ("challenge", challenge)]:
        baseline = []
        skill = []
        for r in subset:
            base = {
                "sample_id": r.get("sample_id"),
                "prompt": r.get("input_without_target", ""),
                "gold_response_solution": r.get("gold_response_solution"),
                "gold_dialogue_agree_solution": r.get("gold_dialogue_agree_solution"),
                "oracle_response_solution": r.get("oracle_response_solution"),
                "oracle_dialogue_agree_solution": r.get("oracle_dialogue_agree_solution"),
                "oracle_rule_id": r.get("oracle_rule_id"),
                "gold_oracle_relation": r.get("gold_oracle_relation"),
            }
            baseline.append(base)
            s = dict(base)
            s["prompt"] = insert_skill_prompt(s["prompt"], skill_prompt)
            skill.append(s)
        write_jsonl(V21_ROOT / "replay" / f"{prefix}_{kind}_baseline_inputs.jsonl", baseline)
        write_jsonl(V21_ROOT / "replay" / f"{prefix}_{kind}_skill_inputs.jsonl", skill)
    return {
        "stable": len(stable),
        "challenge": len(challenge),
        "agree_non_empty_stable": sum(1 for r in stable if r.get("gold_dialogue_agree_solution") not in ("", "无", None) or r.get("oracle_dialogue_agree_solution") not in ("", "无", None)),
        "agree_non_empty_challenge": sum(1 for r in challenge if r.get("gold_dialogue_agree_solution") not in ("", "无", None) or r.get("oracle_dialogue_agree_solution") not in ("", "无", None)),
        "response_dist_stable": Counter(r.get("gold_response_solution") for r in stable),
        "response_dist_challenge": Counter(r.get("gold_response_solution") for r in challenge),
        "conflict_rules": Counter(r.get("oracle_rule_id") for r in challenge),
    }


def main() -> None:
    ensure_dirs()
    fd = _split(V21_ROOT / "replay" / "fulfillment_delivery_oracle_v21.jsonl", "fulfillment_delivery", V21_ROOT / "skills" / "fulfillment_delivery_policy_v21" / "skill_prompt.md")
    rq = _split(V21_ROOT / "replay" / "receipt_quality_oracle_v21.jsonl", "receipt_quality", V21_ROOT / "skills" / "receipt_quality_policy_v21" / "skill_prompt.md")
    lines = [
        "# Replay Sets v21 Report",
        "",
        f"- fulfillment_delivery stable/challenge: `{fd['stable']}` / `{fd['challenge']}`",
        f"- receipt_quality stable/challenge: `{rq['stable']}` / `{rq['challenge']}`",
        f"- FD DialogueAgree non-empty stable/challenge: `{fd['agree_non_empty_stable']}` / `{fd['agree_non_empty_challenge']}`",
        f"- RQ DialogueAgree non-empty stable/challenge: `{rq['agree_non_empty_stable']}` / `{rq['agree_non_empty_challenge']}`",
        "",
        "## FD Stable ResponseSolution",
        top_counter(fd["response_dist_stable"], 20) or "- none",
        "",
        "## FD Challenge Conflict Rules",
        top_counter(fd["conflict_rules"], 20) or "- none",
        "",
        "## RQ Stable ResponseSolution",
        top_counter(rq["response_dist_stable"], 20) or "- none",
        "",
        "## RQ Challenge Conflict Rules",
        top_counter(rq["conflict_rules"], 20) or "- none",
    ]
    (V21_REPORTS / "replay_sets_v21_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
