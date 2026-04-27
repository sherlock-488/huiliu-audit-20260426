#!/usr/bin/env python3
"""Policy v22 for 履约场景-配送问题 with current-turn gating."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v22.common import contains_any, parse_amount_range
from flow_skill_policy_v22.policies.confirmation_resolver import resolve_pending_confirmation
from flow_skill_policy_v22.policies.current_turn_intent import classify_current_turn
from flow_skill_policy_v22.policies.safe_context_bridge import enrich_current_intent
from flow_skill_policy_v22.policies.signal_normalizer import normalize_signals
from flow_skill_policy_v22.policies.solution_eligibility import get_eligible_solutions


def _empty(rule_id: str = "") -> Dict[str, Any]:
    return {
        "recommended_response_solution": "无",
        "recommended_dialogue_agree_solution": "无",
        "decision_type": "no_action",
        "no_action_reason": "",
        "priority_rule_id": rule_id,
        "forbidden_solutions": [],
        "rationale": [],
    }


def _last_query(case_record: Dict[str, Any], flow_state: Dict[str, Any]) -> str:
    return str(case_record.get("last_user_query") or flow_state.get("last_user_query") or "")


def _has(eligible: Dict[str, Any], solution: str) -> bool:
    return solution in set(eligible.get("eligible_solutions") or [])


def _no_rider(status: str) -> bool:
    return any(x in status for x in ["无骑手", "创建履约单", "已推配送", "待接单"])


def _rider_active(status: str) -> bool:
    return any(x in status for x in ["已接单", "配送中", "取货", "到店", "送货"])


def _first_coupon(range_text: str) -> str:
    lo, hi = parse_amount_range(range_text)
    if lo is not None:
        return f"操作赔付-优惠券-{lo}元"
    if hi is not None:
        return f"操作赔付-优惠券-{hi}元"
    return "操作赔付-优惠券-xx元"


def decide_fulfillment_delivery(
    case_record: Dict[str, Any],
    flow_state: Dict[str, Any] | None = None,
    registry: Any = None,
    eligibility: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    flow_state = flow_state or {}
    last_query = _last_query(case_record, flow_state)
    current = classify_current_turn(last_query)
    bridge = enrich_current_intent(case_record, flow_state, current)
    if bridge.get("bridge_used"):
        current = dict(current)
        current["current_intents"] = bridge["enriched_intents"]
        current["bridge_used"] = True
        current["bridge_reason"] = bridge["bridge_reason"]
    resolver = resolve_pending_confirmation(case_record, flow_state, current, registry)
    normalized = normalize_signals(case_record, flow_state)
    eligible = eligibility or get_eligible_solutions(case_record, flow_state, registry)
    intents = set(current.get("current_intents") or [])
    rider = normalized.get("rider_status", "")
    order = normalized.get("order_status", "")
    result = _empty()
    forbidden: List[str] = []
    if normalized.get("can_cancel") is False:
        forbidden.append("取消订单")
    if normalized.get("can_compensate") is False or normalized.get("already_compensated") is True:
        forbidden.extend(["操作赔付-优惠券-xx元", "操作赔付-运费券-3元"])
    result["forbidden_solutions"] = forbidden

    # Current-turn gates first.
    if current.get("is_close_or_thanks"):
        result.update({"priority_rule_id": "FD-CLOSE", "no_action_reason": "close_conversation", "rationale": ["当前最后一条用户消息是感谢/结束语，不从历史触发新动作。"]})
        return result
    if current.get("is_transfer_only"):
        result.update({"priority_rule_id": "FD-CLARIFY_OR_TRANSFER", "no_action_reason": "clarify_intent", "rationale": ["当前只请求人工/客服且无具体诉求，ResponseSolution=无。"]})
        return result
    if current.get("is_ack_only") and not resolver.get("can_confirm_strong_solution"):
        result.update({"priority_rule_id": "FD-ACK", "no_action_reason": "after_action_followup", "rationale": ["当前只是弱确认/应答，且没有 pending strong solution，不触发动作。"]})
        return result
    if resolver.get("can_confirm_strong_solution"):
        confirmed = resolver["confirmed_solution"]
        if confirmed == "取消订单" and normalized.get("can_cancel") is False:
            result.update({"priority_rule_id": "FD-09", "decision_type": "guard", "no_action_reason": "unavailable_capability", "rationale": ["用户确认取消但订单不可取消，禁止填取消订单。"]})
            return result
        if confirmed.startswith("操作赔付") and (normalized.get("can_compensate") is False or normalized.get("already_compensated") is True):
            result.update({"priority_rule_id": "FD-11", "decision_type": "guard", "no_action_reason": "already_compensated" if normalized.get("already_compensated") else "unavailable_capability", "rationale": ["用户确认赔付但订单不可赔/已赔，禁止填赔付。"]})
            return result
        if confirmed in {"取消订单", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元"}:
            result.update({"recommended_response_solution": confirmed, "recommended_dialogue_agree_solution": confirmed, "decision_type": "confirm", "priority_rule_id": "FD-CONFIRM", "rationale": ["当前弱确认结合 pending strong solution，允许 DialogueAgreeSolution 非空。"]})
            return result

    # FD-09 / FD-11 guards based on current intent only.
    if "cancel_request" in intents and normalized.get("can_cancel") is False:
        result.update({"priority_rule_id": "FD-09", "decision_type": "guard", "no_action_reason": "unavailable_capability", "rationale": ["当前用户要求取消，但 can_cancel=false。"]})
        return result
    if "compensation_request" in intents and (normalized.get("can_compensate") is False or normalized.get("already_compensated") is True):
        result.update({"priority_rule_id": "FD-11", "decision_type": "guard", "no_action_reason": "already_compensated" if normalized.get("already_compensated") else "unavailable_capability", "rationale": ["当前用户要求赔付，但不可赔或已赔。"]})
        return result

    # FD-08 cancel proposal.
    if "cancel_request" in intents and _has(eligible, "取消订单"):
        result.update({"recommended_response_solution": "取消订单", "decision_type": "action", "priority_rule_id": "FD-08", "rationale": ["当前用户有取消诉求且可取消；未确认前 DialogueAgreeSolution=无。"]})
        return result

    # FD-10 compensation proposal. Do not auto-trigger on timeout alone.
    if "compensation_request" in intents and any(s.startswith("操作赔付-优惠券") for s in eligible.get("eligible_solutions", [])):
        sol = _first_coupon(normalized.get("compensation_amount_range", ""))
        result.update({"recommended_response_solution": sol, "decision_type": "action", "priority_rule_id": "FD-10", "rationale": ["当前用户要求赔付/强烈不满且可赔未赔；first_offer 取赔付区间下限。"]})
        return result

    # FD-06 repeated call.
    if _has(eligible, "再次外呼骑手-xx"):
        result.update({"recommended_response_solution": "再次外呼骑手-催促配送", "decision_type": "action", "priority_rule_id": "FD-06", "rationale": ["当前仍要求联系骑手，且最近一次外呼未接通。"]})
        return result

    # FD-12 smart follow-up after previous delivery push/call.
    if _has(eligible, "智能跟单") and contains_any(last_query, "别忘", "继续", "还没到", "盯", "跟进", "问骑手了吗", "5分钟"):
        result.update({"recommended_response_solution": "智能跟单", "decision_type": "action", "priority_rule_id": "FD-12", "rationale": ["上一轮已推进且当前仍要求继续关注/询问结果。"]})
        return result

    # FD-05 contact rider.
    if "contact_rider" in intents and _rider_active(rider):
        if _has(eligible, "外呼骑手-xx") and contains_any(last_query, "帮我", "你问", "客服问", "打电话", "帮忙联系"):
            result.update({"recommended_response_solution": "外呼骑手-催促配送", "decision_type": "action", "priority_rule_id": "FD-05B", "rationale": ["当前明确要求客服帮忙联系骑手，外呼类不要求 DialogueAgreeSolution。"]})
            return result
        if _has(eligible, "引导自助联系骑手"):
            result.update({"recommended_response_solution": "引导自助联系骑手", "decision_type": "action", "priority_rule_id": "FD-05A", "rationale": ["当前想联系骑手但未明确要求客服外呼，优先自助联系。"]})
            return result

    # FD-02 / FD-04 no rider dispatch.
    if _no_rider(rider) and _has(eligible, "加急调度") and ({"eta_question", "delivery_urge", "no_rider"} & intents):
        result.update({"recommended_response_solution": "加急调度", "decision_type": "action", "priority_rule_id": "FD-04" if "delivery_urge" in intents or "no_rider" in intents else "FD-02", "rationale": ["当前询问 ETA/催接单/催配送且骑手无接单，优先加急调度。"]})
        return result

    # FD-03 system urge.
    if (("delivery_urge" in intents) or (("eta_question" in intents) and (normalized.get("has_timeout_risk") is True or normalized.get("order_timeout") is True))) and _has(eligible, "系统催单"):
        result.update({"recommended_response_solution": "系统催单", "decision_type": "action", "priority_rule_id": "FD-03", "rationale": ["当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。"]})
        return result

    # FD-07 delivered/status close.
    if any(x in rider + order for x in ["已送达", "已完成"]) and contains_any(last_query, "到了吗", "送到了", "找到了", "我看看"):
        result.update({"priority_rule_id": "FD-07", "no_action_reason": "explain_status", "rationale": ["已送达/已完成的状态咨询，不触发催单/加急。"]})
        return result

    # FD-01 ETA only.
    if "eta_question" in intents and "履约中" in order and normalized.get("order_timeout") is not True and normalized.get("has_timeout_risk") is not True and not _no_rider(rider):
        result.update({"priority_rule_id": "FD-01", "no_action_reason": "eta_answer_only", "rationale": ["普通 ETA 咨询可告知预计送达时间，不承诺一定准时。"]})
        return result

    result.update({"priority_rule_id": "FD-OTHER", "no_action_reason": "unknown", "rationale": ["未命中 v22 配送动作规则；当前轮 gating 阻止历史关键词误触发。"]})
    return result


OPEN_QUESTIONS_FOR_TRAINER = [
    "普通 ETA + 无骑手接单时是否总应加急调度，还是部分样本只解释预计时间？",
    "配送超时但用户未要求赔付时是否永远不主动赔付？",
    "系统催单与智能跟单是否允许同轮复合输出？",
    "用户要求联系骑手时，自助联系与客服外呼的优先级边界是什么？",
]
