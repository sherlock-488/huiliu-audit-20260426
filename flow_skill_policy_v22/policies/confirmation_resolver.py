#!/usr/bin/env python3
"""Resolve v22 pending confirmation with stricter pure-confirm rules."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v22.common import V1_OUT, V21_ROOT, V22_REPORTS, canonicalize_solution, ensure_dirs, get_case_records_path, get_flow_states_path, read_jsonl, split_solution_raw
from flow_skill_policy_v22.policies.current_turn_intent import classify_current_turn


STRONG_CONFIRMATION = {"取消订单", "小象单商品退款-xx%", "小象整单申请退款", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元", "会员卡退款"}
USER_REQUEST_ENOUGH = {"外呼骑手-xx", "再次外呼骑手-xx", "外呼门店-xx", "再次外呼门店-xx", "催促退款审核", "加急催促退款审核"}
BLOCK_CONFIRM = ["什么时候", "多久", "到账", "还没", "怎么", "为什么", "太少", "少吗", "不行", "不接受", "不能接受", "再", "多退", "投诉"]


def _first(raw_values: List[Any], allowed: set[str]) -> str:
    for value in raw_values:
        for comp in split_solution_raw(value):
            canonical, _, _ = canonicalize_solution(comp)
            if canonical in allowed:
                return canonical
    return ""


def resolve_pending_confirmation(case_record: Dict[str, Any], flow_state: Dict[str, Any] | None, current_turn_intent: Dict[str, Any], solution_registry: Any = None) -> Dict[str, Any]:
    flow_state = flow_state or {}
    debug: List[str] = []
    candidates = [
        flow_state.get("pending_confirmation_solution"),
        flow_state.get("last_response_solution"),
        flow_state.get("prev_response_solution_raw"),
        case_record.get("prev_response_solution_raw"),
    ]
    for key in ["prev_response_solution_components", "last_response_solution_components"]:
        comps = flow_state.get(key) or []
        if comps:
            candidates.append(";".join(comps))
    pending_strong = _first(candidates, STRONG_CONFIRMATION)
    pending_user_request = _first(candidates, USER_REQUEST_ENOUGH)
    raw = current_turn_intent.get("raw", "") or ""
    blocked = any(x in raw for x in BLOCK_CONFIRM)
    if pending_strong:
        debug.append(f"pending_strong:{pending_strong}")
    if blocked:
        debug.append("blocked_by_question_or_reject")
    confirm_signal = current_turn_intent.get("is_pure_confirm") is True or current_turn_intent.get("maybe_accept_pending") is True
    close_block = current_turn_intent.get("is_close_or_thanks") is True and current_turn_intent.get("maybe_accept_pending") is not True
    can_confirm = bool(pending_strong) and confirm_signal and not close_block and not blocked
    if can_confirm:
        debug.append("v22_confirmed_pending_strong")
    elif current_turn_intent.get("is_confirm_like"):
        debug.append("confirm_like_not_enough")
    return {
        "pending_strong_solution": pending_strong,
        "pending_user_request_solution": pending_user_request,
        "can_confirm_strong_solution": can_confirm,
        "confirmed_solution": pending_strong if can_confirm else "",
        "debug_reason": debug,
    }


def build_report() -> None:
    ensure_dirs()
    flows = {r["sample_id"]: r for r in read_jsonl(get_flow_states_path())}
    v21_confirm = 0
    v22_block = 0
    maybe = 0
    agree_non_empty = 0
    agree_covered = 0
    examples = []
    for case in read_jsonl(get_case_records_path()):
        sid = case.get("sample_id")
        flow = flows.get(sid, {})
        cur = classify_current_turn(case.get("last_user_query", ""))
        res = resolve_pending_confirmation(case, flow, cur)
        if cur.get("maybe_accept_pending"):
            maybe += 1
        # Approximate v21 trigger: confirm_like + pending strong + not close.
        pending = res.get("pending_strong_solution")
        old_can = bool(pending) and cur.get("is_confirm_like") and not cur.get("is_close_or_thanks")
        if old_can:
            v21_confirm += 1
            if not res.get("can_confirm_strong_solution"):
                v22_block += 1
                if len(examples) < 30:
                    examples.append((case.get("sample_id"), case.get("last_user_query"), pending, cur.get("debug_reason")))
        if case.get("dialogue_agree_solution_raw") not in ("", "无", None):
            agree_non_empty += 1
            if res.get("can_confirm_strong_solution") or case.get("dialogue_agree_solution_raw") == flow.get("dialogue_agree_solution_raw"):
                agree_covered += 1
    lines = [
        "# Confirmation Resolver v22 Report",
        "",
        f"- v21_confirm_like_with_pending: `{v21_confirm}`",
        f"- v21_trigger_but_v22_blocked: `{v22_block}`",
        f"- v22_maybe_accept_pending: `{maybe}`",
        f"- dialogue_agree_non_empty_cases: `{agree_non_empty}`",
        f"- dialogue_agree_covered_or_preserved: `{agree_covered}`",
        "",
        "## Blocked Examples",
    ]
    for sid, q, pending, reason in examples:
        lines.append(f"- `{sid}` `{q}` pending=`{pending}` debug=`{reason}`")
    (V22_REPORTS / "confirmation_resolver_v22_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_report()
