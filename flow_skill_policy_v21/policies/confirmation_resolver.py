#!/usr/bin/env python3
"""Resolve whether the current turn confirms a pending strong solution."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v21.common import canonical_components, canonicalize_solution, split_solution_raw


STRONG_CONFIRMATION = {
    "取消订单",
    "小象单商品退款-xx%",
    "小象整单申请退款",
    "操作赔付-优惠券-xx元",
    "操作赔付-运费券-3元",
    "会员卡退款",
}
USER_REQUEST_ENOUGH = {"外呼骑手-xx", "再次外呼骑手-xx", "外呼门店-xx", "再次外呼门店-xx", "催促退款审核", "加急催促退款审核"}


def _first_strong(raw_values: List[Any]) -> str:
    for value in raw_values:
        for comp in split_solution_raw(value):
            canonical, _, _ = canonicalize_solution(comp)
            if canonical in STRONG_CONFIRMATION:
                return canonical
    return ""


def _first_user_request(raw_values: List[Any]) -> str:
    for value in raw_values:
        for comp in split_solution_raw(value):
            canonical, _, _ = canonicalize_solution(comp)
            if canonical in USER_REQUEST_ENOUGH:
                return canonical
    return ""


def resolve_pending_confirmation(
    case_record: Dict[str, Any],
    flow_state: Dict[str, Any] | None,
    current_turn_intent: Dict[str, Any],
    solution_registry: Any = None,
) -> Dict[str, Any]:
    flow_state = flow_state or {}
    debug: List[str] = []
    candidates = [
        flow_state.get("pending_confirmation_solution"),
        flow_state.get("last_response_solution"),
        flow_state.get("prev_response_solution_raw"),
        case_record.get("prev_response_solution_raw"),
    ]
    # Some trajectory builds keep recent components rather than raw strings.
    for key in ["prev_response_solution_components", "last_response_solution_components"]:
        comps = flow_state.get(key) or []
        if comps:
            candidates.append(";".join(comps))

    pending_strong = _first_strong(candidates)
    pending_user_request = _first_user_request(candidates)
    if pending_strong:
        debug.append(f"pending_strong:{pending_strong}")
    if pending_user_request:
        debug.append(f"pending_user_request:{pending_user_request}")

    can_confirm = (
        bool(pending_strong)
        and current_turn_intent.get("is_confirm_like") is True
        and current_turn_intent.get("is_close_or_thanks") is not True
    )
    if can_confirm:
        debug.append("current_confirm_like_with_pending_strong")
    elif current_turn_intent.get("is_confirm_like"):
        debug.append("confirm_like_without_pending_strong")

    return {
        "pending_strong_solution": pending_strong,
        "pending_user_request_solution": pending_user_request,
        "can_confirm_strong_solution": can_confirm,
        "confirmed_solution": pending_strong if can_confirm else "",
        "debug_reason": debug,
    }

