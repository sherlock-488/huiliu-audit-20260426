#!/usr/bin/env python3
"""Small replay-run intent patch for fulfillment delivery.

This keeps the reviewed v22 policy artifacts immutable and records the
additional replay-only interpretation requested for delivery phrases such as
"怎么还没配送": they should be both ETA questions and delivery urges.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flow_skill_policy_v22.common import read_jsonl  # noqa: E402
from flow_skill_policy_v22.policies.current_turn_intent import classify_current_turn  # noqa: E402


DUAL_ETA_URGE_PATTERNS = [
    "怎么还没配送",
    "怎么还没送",
    "怎么还没送到",
    "还没配送",
    "还没送到",
    "不是还没送到吗",
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def classify_current_turn_v23(last_user_query: str) -> Dict[str, Any]:
    """Apply the replay_run_v1 delivery patch on top of v22 classifier."""
    result = dict(classify_current_turn(last_user_query))
    intents = list(result.get("current_intents") or [])
    text = _norm(last_user_query)
    if any(pattern in text for pattern in DUAL_ETA_URGE_PATTERNS):
        changed = False
        for intent in ("eta_question", "delivery_urge"):
            if intent not in intents:
                intents.append(intent)
                changed = True
        if changed:
            result["current_intents"] = intents
            result["has_new_action_intent"] = not (
                result.get("is_close_or_thanks")
                or result.get("is_ack_only")
                or result.get("is_transfer_only")
            )
            result.setdefault("debug_reason", []).append("replay_v1_dual_eta_urge_patch")
    return result


def _iter_fd_oracle_rows() -> Iterable[Dict[str, Any]]:
    for name in [
        "fulfillment_delivery_stable_replay.jsonl",
        "fulfillment_delivery_action_focused_replay.jsonl",
        "fulfillment_delivery_challenge_replay.jsonl",
    ]:
        path = ROOT / "flow_skill_policy_v22" / "replay" / name
        if path.exists():
            yield from read_jsonl(path)


def build_report() -> None:
    rows = list(_iter_fd_oracle_rows())
    total = len(rows)
    changed = []
    phrase_hits = Counter()
    before_counter = Counter()
    after_counter = Counter()
    close_ack_transfer_triggered = 0
    for row in rows:
        query = row.get("last_user_query", "")
        before = row.get("current_turn_intent") or classify_current_turn(query)
        after = classify_current_turn_v23(query)
        before_intents = set(before.get("current_intents") or [])
        after_intents = set(after.get("current_intents") or [])
        for intent in before_intents:
            before_counter[intent] += 1
        for intent in after_intents:
            after_counter[intent] += 1
        text = _norm(query)
        for phrase in DUAL_ETA_URGE_PATTERNS:
            if phrase in text:
                phrase_hits[phrase] += 1
        if before_intents != after_intents:
            changed.append(
                {
                    "sample_id": row.get("sample_id"),
                    "last_user_query": query,
                    "before": sorted(before_intents),
                    "after": sorted(after_intents),
                    "oracle_rule_id": row.get("oracle_rule_id"),
                    "gold_response_solution": row.get("gold_response_solution"),
                    "oracle_response_solution": row.get("oracle_response_solution"),
                }
            )
        if (
            after.get("is_close_or_thanks")
            or after.get("is_ack_only")
            or after.get("is_transfer_only")
        ) and ("delivery_urge" in after_intents or "eta_question" in after_intents):
            close_ack_transfer_triggered += 1

    report = ROOT / "replay_run_v1" / "reports" / "current_turn_patch_report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = [
        "# Current Turn Patch Report",
        "",
        "## Patch",
        "- Added replay-only dual intent mapping: `怎么还没配送 / 怎么还没送 / 怎么还没送到 / 还没配送 / 还没送到 / 不是还没送到吗` -> `eta_question + delivery_urge`.",
        "- Kept v22 close/ack/transfer gates unchanged.",
        "- Kept weak confirmation blocking unchanged: weak confirm plus question/progress/reject terms is not pure confirmation.",
        "",
        "## Impact On v22 Fulfillment Delivery Oracle Rows",
        f"- scanned_fd_oracle_rows: `{total}`",
        f"- changed_rows: `{len(changed)}`",
        f"- close_ack_transfer_rows_newly_triggered: `{close_ack_transfer_triggered}`",
        "",
        "## Phrase Hits",
    ]
    if phrase_hits:
        lines.extend(f"- `{k}`: `{v}`" for k, v in phrase_hits.most_common())
    else:
        lines.append("- No exact phrase hits in current FD replay rows.")
    lines.extend(["", "## Intent Count Delta"])
    for intent in sorted(set(before_counter) | set(after_counter)):
        before_n = before_counter[intent]
        after_n = after_counter[intent]
        if before_n != after_n:
            lines.append(f"- `{intent}`: `{before_n}` -> `{after_n}`")
    lines.extend(["", "## Changed Examples"])
    for row in changed[:50]:
        lines.append(
            f"- `{row['sample_id']}` `{row['last_user_query']}`: `{row['before']}` -> `{row['after']}` "
            f"gold=`{row['gold_response_solution']}` oracle=`{row['oracle_response_solution']}` rule=`{row['oracle_rule_id']}`"
        )
    if not changed:
        lines.append("- No FD oracle row changed under the exact replay patch.")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(classify_current_turn_v23(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))
    else:
        build_report()
