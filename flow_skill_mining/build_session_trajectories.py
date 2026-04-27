#!/usr/bin/env python3
"""Build session trajectories and DialogueAgreeSolution linkage."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import (
    OUT_DIR,
    REPORT_DIR,
    compact_counter,
    ensure_dirs,
    initial_requires_agreement,
    load_jsonl_list,
    same_solution_or_type,
    split_components,
    write_jsonl,
)


INPUT_PATH = OUT_DIR / "case_records.jsonl"
OUTPUT_PATH = OUT_DIR / "session_trajectories.jsonl"
REPORT_PATH = REPORT_DIR / "session_trajectory_report.md"


def _components_match(left: List[str], right: List[str]) -> str:
    for a in left:
        for b in right:
            if same_solution_or_type(a, b):
                return a
    return ""


def _find_agree_match(records: List[Dict[str, Any]], idx: int) -> Tuple[str, str]:
    agree = records[idx].get("dialogue_agree_solution_components", [])
    if not agree:
        return "", ""
    if idx > 0:
        matched = _components_match(agree, records[idx - 1].get("response_solution_components", []))
        if matched:
            return matched, "previous"
    matched = _components_match(agree, records[idx].get("response_solution_components", []))
    if matched:
        return matched, "current"
    start = max(0, idx - 3)
    for prev_idx in range(idx - 1, start - 1, -1):
        matched = _components_match(agree, records[prev_idx].get("response_solution_components", []))
        if matched:
            return matched, "recent3"
    return "", "unmatched"


def main() -> None:
    ensure_dirs()
    records = load_jsonl_list(INPUT_PATH)
    sessions: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        sessions[record.get("session_id", "")].append(record)

    rows = []
    agree_solution_ctr = collections.Counter()
    pending_ctr = collections.Counter()
    match_type_ctr = collections.Counter()
    unmatched = 0
    agree_nonempty = 0

    for session_id, session_records in sessions.items():
        session_records.sort(key=lambda r: r.get("source_line", 0))
        count = len(session_records)
        for idx, record in enumerate(session_records):
            prev = session_records[idx - 1] if idx > 0 else {}
            next_row = session_records[idx + 1] if idx + 1 < count else {}
            agree_components = record.get("dialogue_agree_solution_components", [])
            prev_resp_components = prev.get("response_solution_components", [])
            pending_solution = ""
            if prev_resp_components and agree_components:
                prev_needs_confirm = any(initial_requires_agreement(comp) is True for comp in prev_resp_components)
                matched_prev = _components_match(agree_components, prev_resp_components)
                if prev_needs_confirm and matched_prev:
                    pending_solution = matched_prev
                    pending_ctr[matched_prev] += 1

            matched_solution, match_type = _find_agree_match(session_records, idx)
            if agree_components:
                agree_nonempty += 1
                for comp in agree_components:
                    agree_solution_ctr[comp] += 1
                match_type_ctr[match_type] += 1
                if match_type == "unmatched":
                    unmatched += 1

            augmented = dict(record)
            augmented.update(
                {
                    "turn_index": idx,
                    "prev_response_solution_raw": prev.get("response_solution_raw", ""),
                    "prev_response_solution_components": prev.get("response_solution_components", []),
                    "prev_dialogue_agree_solution_raw": prev.get("dialogue_agree_solution_raw", ""),
                    "prev_dialogue_agree_solution_components": prev.get(
                        "dialogue_agree_solution_components", []
                    ),
                    "prev_response": prev.get("response", ""),
                    "next_last_user_query": next_row.get("last_user_query", ""),
                    "session_turn_count": count,
                    "pending_confirmation_solution": pending_solution,
                    "dialogue_agree_match_solution": matched_solution,
                    "dialogue_agree_match_type": match_type if agree_components else "",
                    "unmatched_dialogue_agree": bool(agree_components and match_type == "unmatched"),
                }
            )
            rows.append(augmented)

    write_jsonl(OUTPUT_PATH, rows)
    session_lengths = [len(v) for v in sessions.values()]
    avg_turns = sum(session_lengths) / len(session_lengths) if session_lengths else 0
    md = []
    md.append("# Session Trajectory 报告")
    md.append("")
    md.append(f"- session 数: `{len(sessions)}`")
    md.append(f"- 平均 turn 数: `{avg_turns:.2f}`")
    md.append(f"- 最大 turn 数: `{max(session_lengths, default=0)}`")
    md.append(f"- DialogueAgreeSolution 非空样本数: `{agree_nonempty}`")
    matched = agree_nonempty - unmatched
    matched_rate = matched / agree_nonempty if agree_nonempty else 0.0
    md.append(f"- 能匹配到前置/本轮/近 3 轮方案: `{matched}` ({matched_rate:.2%})")
    md.append(f"- unmatched_dialogue_agree 样本数: `{unmatched}`")
    md.append("")
    md.append("## DialogueAgreeSolution match type")
    md.append(compact_counter(match_type_ctr, 20))
    md.append("")
    md.append("## DialogueAgreeSolution 出现次数")
    md.append(compact_counter(agree_solution_ctr, 80))
    md.append("")
    md.append("## pending confirmation 被确认方案")
    md.append(compact_counter(pending_ctr, 80))
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "sessions": len(sessions), "report": str(REPORT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
