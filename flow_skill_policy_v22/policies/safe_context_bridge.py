#!/usr/bin/env python3
"""Conservative bridge for short current-turn messages."""

from __future__ import annotations

from typing import Any, Dict, List


SHORT_ETA = {"5分钟？", "5分钟?", "多久？", "多久?", "还要多久？", "还要多久?", "啥时候？", "啥时候?"}
SHORT_URGE = {"急", "快点", "催一下", "加急"}


def _tail(case_record: Dict[str, Any], flow_state: Dict[str, Any]) -> str:
    return "".join(
        str(x or "")
        for x in [
            flow_state.get("last_response_solution"),
            flow_state.get("prev_response_solution_raw"),
            case_record.get("last_assistant_response"),
            (case_record.get("dialogue_history") or "")[-600:],
        ]
    )


def enrich_current_intent(case_record: Dict[str, Any], flow_state: Dict[str, Any] | None, current_intent: Dict[str, Any]) -> Dict[str, Any]:
    flow_state = flow_state or {}
    raw = (current_intent.get("raw") or "").strip()
    compact = "".join(raw.split())
    intents: List[str] = list(current_intent.get("current_intents") or [])
    reasons: List[str] = []
    if current_intent.get("is_close_or_thanks") or current_intent.get("is_transfer_only"):
        return {"enriched_intents": intents, "bridge_used": False, "bridge_reason": ["blocked_close_or_transfer"]}
    if len(compact) > 8 and compact not in SHORT_ETA:
        return {"enriched_intents": intents, "bridge_used": False, "bridge_reason": ["not_short_query"]}
    context = _tail(case_record, flow_state)
    context_delivery = any(x in context for x in ["预计送达", "送达时间", "系统催单", "加急调度", "外呼骑手", "智能跟单", "配送"])
    context_confirm = any(x in context for x in ["退款", "赔付", "取消订单", "优惠券", "退"])
    if compact in SHORT_ETA and context_delivery and "eta_question" not in intents:
        intents.append("eta_question")
        reasons.append("short_eta_with_delivery_context")
    if compact in SHORT_URGE and (context_delivery or "履约场景-配送问题" in (case_record.get("scene") or flow_state.get("scene") or "")) and "delivery_urge" not in intents:
        intents.append("delivery_urge")
        reasons.append("short_urge_with_delivery_context")
    if compact in {"行", "好", "可以", "嗯"} and context_confirm and "confirm_like_context" not in intents:
        reasons.append("short_ack_with_confirmation_context")
    return {"enriched_intents": list(dict.fromkeys(intents)), "bridge_used": bool(reasons), "bridge_reason": reasons}

