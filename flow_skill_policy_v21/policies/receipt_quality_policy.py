#!/usr/bin/env python3
"""Policy v21 for 收货场景-品质问题 with current-turn gating."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v21.common import contains_any, parse_amount_range
from flow_skill_policy_v21.policies.confirmation_resolver import resolve_pending_confirmation
from flow_skill_policy_v21.policies.current_turn_intent import classify_current_turn
from flow_skill_policy_v21.policies.signal_normalizer import normalize_signals
from flow_skill_policy_v21.policies.solution_eligibility import get_eligible_solutions


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


def _first_coupon(range_text: str) -> str:
    lo, hi = parse_amount_range(range_text)
    if lo is not None:
        return f"操作赔付-优惠券-{lo}元"
    if hi is not None:
        return f"操作赔付-优惠券-{hi}元"
    return "操作赔付-优惠券-xx元"


def _item_qty(case_record: Dict[str, Any], normalized: Dict[str, Any]) -> int:
    selected_name = normalized.get("selected_item_name", "")
    if not selected_name:
        return 1
    for item in case_record.get("items") or []:
        name = str(item.get("商品名称", ""))
        if selected_name in name or name in selected_name:
            try:
                return int(float(str(item.get("商品数量", item.get("数量", 1))).replace("件", "")))
            except Exception:
                return 1
    return 1


def _refund_active(status: str) -> bool:
    return any(x in (status or "") for x in ["退款中", "审核中", "客服审核", "银行退款中", "银行处理中", "处理中", "待审核"])


def _refunded(status: str) -> bool:
    return any(x in (status or "") for x in ["已退款", "已全部退款", "退款完成", "退款成功"])


def _refund_solution(case_record: Dict[str, Any]) -> str:
    raw = case_record.get("response_solution_raw", "")
    if raw.startswith("小象单商品退款-"):
        return raw
    return "小象单商品退款-100%" if contains_any(case_record.get("last_user_query", ""), "全退", "全部", "全额") else "小象单商品退款-xx%"


def decide_receipt_quality(
    case_record: Dict[str, Any],
    flow_state: Dict[str, Any] | None = None,
    registry: Any = None,
    eligibility: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    flow_state = flow_state or {}
    last_query = _last_query(case_record, flow_state)
    current = classify_current_turn(last_query)
    resolver = resolve_pending_confirmation(case_record, flow_state, current, registry)
    normalized = normalize_signals(case_record, flow_state)
    eligible = eligibility or get_eligible_solutions(case_record, flow_state, registry)
    intents = set(current.get("current_intents") or [])
    status = normalized.get("refund_status", "") + normalized.get("selected_item_refund_status", "")
    result = _empty()
    forbidden: List[str] = []
    if normalized.get("selected_item_state") != "selected" or normalized.get("selected_item_can_refund") is False or normalized.get("order_over_after_sales") is True:
        forbidden.append("小象单商品退款-xx%")
    if normalized.get("can_compensate") is False or normalized.get("already_compensated") is True:
        forbidden.append("操作赔付-优惠券-xx元")
    result["forbidden_solutions"] = forbidden

    # Current-turn gates first.
    if current.get("is_close_or_thanks"):
        result.update({"priority_rule_id": "RQ-CLOSE", "no_action_reason": "close_conversation", "rationale": ["当前最后一条用户消息是感谢/结束语，不从历史或状态触发新退款/赔付/催审。"]})
        return result
    if current.get("is_transfer_only"):
        result.update({"priority_rule_id": "RQ-CLARIFY_OR_TRANSFER", "no_action_reason": "clarify_intent", "rationale": ["当前只请求人工/客服且无具体诉求，ResponseSolution=无。"]})
        return result
    if current.get("is_ack_only") and not resolver.get("can_confirm_strong_solution"):
        result.update({"priority_rule_id": "RQ-ACK", "no_action_reason": "after_action_followup", "rationale": ["当前只是弱确认/应答，且没有 pending strong solution，不触发动作。"]})
        return result
    if resolver.get("can_confirm_strong_solution"):
        confirmed = resolver["confirmed_solution"]
        if confirmed == "小象单商品退款-xx%" and (normalized.get("selected_item_can_refund") is False or normalized.get("order_over_after_sales") is True):
            result.update({"priority_rule_id": "RQ-01", "decision_type": "guard", "no_action_reason": "explain_cannot_refund", "rationale": ["用户确认退款但商品不可退/订单超售后，禁止退款。"]})
            return result
        if confirmed.startswith("操作赔付") and (normalized.get("can_compensate") is False or normalized.get("already_compensated") is True):
            result.update({"priority_rule_id": "RQ-12", "decision_type": "guard", "no_action_reason": "already_compensated" if normalized.get("already_compensated") else "unavailable_capability", "rationale": ["用户确认赔付但不可赔/已赔，禁止赔付。"]})
            return result
        if confirmed in {"小象单商品退款-xx%", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元"}:
            result.update({"recommended_response_solution": confirmed, "recommended_dialogue_agree_solution": confirmed, "decision_type": "confirm", "priority_rule_id": "RQ-CONFIRM", "rationale": ["当前弱确认结合 pending strong solution，允许 DialogueAgreeSolution 非空。"]})
            return result

    # RQ-01 only when order-level after-sales or selected item is explicitly unavailable.
    if normalized.get("order_over_after_sales") is True:
        result.update({"priority_rule_id": "RQ-01", "decision_type": "guard", "no_action_reason": "policy_explain", "rationale": ["订单明确超售后，禁止单商品退款。"]})
        return result
    if normalized.get("selected_item_state") == "selected" and normalized.get("selected_item_can_refund") is False:
        result.update({"priority_rule_id": "RQ-01", "decision_type": "guard", "no_action_reason": "explain_cannot_refund", "rationale": ["已选商品且明确不可退款，禁止单商品退款。"]})
        return result

    # RQ-10 / RQ-09 only on refund progress current intent.
    if "refund_progress" in intents and _refunded(status):
        result.update({"priority_rule_id": "RQ-10", "no_action_reason": "explain_refund_status", "rationale": ["当前询问退款状态且退款已完成。"]})
        return result
    if "refund_progress" in intents and _refund_active(status):
        sol = "加急催促退款审核" if contains_any(last_query, "还没", "怎么还", "再催", "加急") else "催促退款审核;退审跟单"
        result.update({"recommended_response_solution": sol, "decision_type": "action", "priority_rule_id": "RQ-09", "rationale": ["当前明确咨询/催促退款进度，且退款状态为进行中/审核中。"]})
        return result

    # RQ-12 compensation guard.
    if "compensation_request" in intents and (normalized.get("can_compensate") is False or normalized.get("already_compensated") is True):
        result.update({"priority_rule_id": "RQ-12", "decision_type": "guard", "no_action_reason": "already_compensated" if normalized.get("already_compensated") else "unavailable_capability", "rationale": ["当前要求赔付，但不可赔或已赔。"]})
        return result

    # Front guards only when current turn is still quality/refund flow.
    refund_flow_intent = bool({"quality_issue", "refund_request", "confirm_refund"} & intents or resolver.get("pending_strong_solution") == "小象单商品退款-xx%")
    if normalized.get("selected_item_state") != "selected" and {"quality_issue", "refund_request"} & intents and _has(eligible, "选择商品"):
        result.update({"recommended_response_solution": "选择商品", "decision_type": "action", "priority_rule_id": "RQ-02", "rationale": ["当前品质/退款诉求仍在推进且未选商品，先选择商品。"]})
        return result
    if refund_flow_intent and normalized.get("selected_item_state") == "selected" and normalized.get("has_image_evidence") is not True:
        result.update({"priority_rule_id": "RQ-03", "no_action_reason": "ask_upload_image", "rationale": ["当前仍在推进品质退款，已选商品但缺图片凭证。"]})
        return result
    if refund_flow_intent and normalized.get("selected_item_state") == "selected" and normalized.get("has_image_evidence") is True and normalized.get("has_refund_reason") is False:
        result.update({"priority_rule_id": "RQ-04", "no_action_reason": "ask_refund_reason", "rationale": ["当前仍在推进品质退款，缺退款原因。"]})
        return result
    if refund_flow_intent and normalized.get("selected_item_state") == "selected" and normalized.get("has_image_evidence") is True and normalized.get("has_refund_reason") is True and normalized.get("has_refund_ratio") is False:
        result.update({"priority_rule_id": "RQ-05", "no_action_reason": "ask_refund_ratio", "rationale": ["当前仍在推进品质退款，缺退款比例。"]})
        return result
    if refund_flow_intent and _item_qty(case_record, normalized) > 1 and normalized.get("has_refund_quantity") is False:
        result.update({"priority_rule_id": "RQ-06", "no_action_reason": "ask_refund_quantity", "rationale": ["多数量商品缺退款数量，不默认处理。"]})
        return result

    # RQ-11 compensation proposal.
    if "compensation_request" in intents and any(s.startswith("操作赔付-优惠券") for s in eligible.get("eligible_solutions", [])):
        sol = _first_coupon(normalized.get("compensation_amount_range", ""))
        result.update({"recommended_response_solution": sol, "decision_type": "action", "priority_rule_id": "RQ-11", "rationale": ["当前要求赔付/强烈不满且可赔未赔；first_offer 取赔付区间下限。"]})
        return result

    # RQ-07 / RQ-08 refund proposal.
    if ({"refund_request", "quality_issue", "confirm_refund"} & intents) and _has(eligible, "小象单商品退款-xx%"):
        sol = _refund_solution(case_record)
        result.update({"recommended_response_solution": sol, "decision_type": "action", "priority_rule_id": "RQ-08", "rationale": ["当前仍有退款/品质诉求且前置满足；提出退款，未确认前 DialogueAgreeSolution=无。"]})
        return result

    result.update({"priority_rule_id": "RQ-OTHER", "no_action_reason": "unknown", "rationale": ["未命中 v21 品质动作规则；current-turn gating 阻止状态或历史误触发。"]})
    return result


OPEN_QUESTIONS_FOR_TRAINER = [
    "未选商品但部分商品状态不可退时，是否必须先选择商品再判断不可退？",
    "品质问题缺图片/原因/比例时，是否允许客服主动提出退款比例？",
    "退款进度只有订单部分退款但用户未问进度时，是否绝不催审？",
    "赔付 first_offer 取区间下限是否符合训练师口径？",
]
