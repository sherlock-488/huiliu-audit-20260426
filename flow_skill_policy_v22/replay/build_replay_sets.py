#!/usr/bin/env python3
"""Build stable/challenge/action-focused replay sets for v22."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v22.common import V22_REPORTS, V22_ROOT, ensure_dirs, read_jsonl, top_counter, write_jsonl


def _is_action(row: Dict[str, Any]) -> bool:
    return row.get("gold_response_solution") != "无" or row.get("oracle_response_solution") != "无"


def _split(path: Path, prefix: str) -> Dict[str, Any]:
    rows = list(read_jsonl(path))
    stable = [r for r in rows if r.get("gold_oracle_relation") in {"same", "canonical_same"}]
    challenge = [r for r in rows if r.get("gold_oracle_relation") not in {"same", "canonical_same"}]
    action = [r for r in stable + challenge if _is_action(r)]
    write_jsonl(V22_ROOT / "replay" / f"{prefix}_stable_replay.jsonl", stable)
    write_jsonl(V22_ROOT / "replay" / f"{prefix}_challenge_replay.jsonl", challenge)
    write_jsonl(V22_ROOT / "replay" / f"{prefix}_action_focused_replay.jsonl", action)
    return {
        "stable": stable,
        "challenge": challenge,
        "action": action,
        "stable_response": Counter(r.get("gold_response_solution") for r in stable),
        "action_response": Counter(r.get("gold_response_solution") for r in action),
        "rule_challenge": Counter(r.get("oracle_rule_id") for r in challenge),
        "intent_action": Counter(",".join(r.get("current_turn_intent", {}).get("current_intents") or ["<NONE>"]) for r in action),
    }


def _agree_non_empty(rows: List[Dict[str, Any]]) -> int:
    return sum(1 for r in rows if r.get("gold_dialogue_agree_solution") not in ("", "无", None) or r.get("oracle_dialogue_agree_solution") not in ("", "无", None))


def _close_ack(rows: List[Dict[str, Any]]) -> int:
    return sum(1 for r in rows if (r.get("current_turn_intent") or {}).get("is_close_or_thanks") or (r.get("current_turn_intent") or {}).get("is_ack_only") or (r.get("current_turn_intent") or {}).get("is_transfer_only"))


def main() -> None:
    ensure_dirs()
    fd = _split(V22_ROOT / "replay" / "fulfillment_delivery_oracle_v22.jsonl", "fulfillment_delivery")
    rq = _split(V22_ROOT / "replay" / "receipt_quality_oracle_v22.jsonl", "receipt_quality")
    lines = [
        "# Replay Sets v22 Report",
        "",
        f"- fulfillment_delivery stable/action/challenge: `{len(fd['stable'])}` / `{len(fd['action'])}` / `{len(fd['challenge'])}`",
        f"- receipt_quality stable/action/challenge: `{len(rq['stable'])}` / `{len(rq['action'])}` / `{len(rq['challenge'])}`",
        f"- FD DialogueAgree non-empty stable/action/challenge: `{_agree_non_empty(fd['stable'])}` / `{_agree_non_empty(fd['action'])}` / `{_agree_non_empty(fd['challenge'])}`",
        f"- RQ DialogueAgree non-empty stable/action/challenge: `{_agree_non_empty(rq['stable'])}` / `{_agree_non_empty(rq['action'])}` / `{_agree_non_empty(rq['challenge'])}`",
        f"- FD close/ack/transfer stable/action/challenge: `{_close_ack(fd['stable'])}` / `{_close_ack(fd['action'])}` / `{_close_ack(fd['challenge'])}`",
        f"- RQ close/ack/transfer stable/action/challenge: `{_close_ack(rq['stable'])}` / `{_close_ack(rq['action'])}` / `{_close_ack(rq['challenge'])}`",
        "",
        "## FD Stable ResponseSolution",
        top_counter(fd["stable_response"], 30) or "- none",
        "",
        "## FD Action Intent Distribution",
        top_counter(fd["intent_action"], 30) or "- none",
        "",
        "## FD Challenge Rule Distribution",
        top_counter(fd["rule_challenge"], 30) or "- none",
        "",
        "## RQ Stable ResponseSolution",
        top_counter(rq["stable_response"], 30) or "- none",
        "",
        "## RQ Action Intent Distribution",
        top_counter(rq["intent_action"], 30) or "- none",
        "",
        "## RQ Challenge Rule Distribution",
        top_counter(rq["rule_challenge"], 30) or "- none",
    ]
    (V22_REPORTS / "replay_sets_v22_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
