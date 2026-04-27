#!/usr/bin/env python3
"""Explicit v2 policy for 收货场景-品质问题."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v2.common import contains_any, explicit_confirm, parse_amount_range
from flow_skill_policy_v2.policies.signal_normalizer import normalize_signals
from flow_skill_policy_v2.policies.solution_eligibility import get_eligible_solutions


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


def _text(case_record: Dict[str, Any], flow_state: Dict[str, Any]) -> str:
    return "".join(
        str(x or "")
        for x in [
            case_record.get("last_user_query"),
            flow_state.get("last_user_query"),
            (case_record.get("dialogue_history") or "")[-800:],
        ]
    )


def _has(eligible: Dict[str, Any], solution: str) -> bool:
    return solution in set(eligible.get("eligible_solutions") or [])


def _coupon(range_text: str) -> str:
    lo, hi = parse_amount_range(range_text)
    levels = [3, 5, 8, 10, 15, 20]
    if hi is None:
        return "操作赔付-优惠券-xx元"
    candidates = [x for x in levels if x <= hi and (lo is None or x >= lo)]
    if not candidates:
        candidates = [x for x in levels if x <= hi]
    return f"操作赔付-优惠券-{max(candidates) if candidates else hi}元"


def _item_qty(case_record: Dict[str, Any], normalized: Dict[str, Any]) -> int:
    selected_name = normalized.get("selected_item_name", "")
    for item in case_record.get("items") or []:
        if not selected_name or selected_name in str(item.get("商品名称", "")) or str(item.get("商品名称", "")) in selected_name:
            try:
                return int(float(str(item.get("商品数量", item.get("数量", 1))).replace("件", "")))
            except Exception:
                return 1
    return 1


def _refund_progress(normalized: Dict[str, Any], flow_state: Dict[str, Any], text: str) -> bool:
    status = normalized.get("refund_status", "") + normalized.get("selected_item_refund_status", "")
    return any(x in status for x in ["退款中", "审核", "银行", "处理中", "待审核"]) or flow_state.get("user_intent") in {
        "refund_progress",
        "cannot_refund",
    } or contains_any(text, "退款进度", "多久到账", "还没退", "退款状态", "审核")


def _refunded(normalized: Dict[str, Any]) -> bool:
    status = normalized.get("refund_status", "") + normalized.get("selected_item_refund_status", "")
    return any(x in status for x in ["已退款", "已全部退款", "退款完成", "退款成功"])


def _wants_compensation(flow_state: Dict[str, Any], text: str) -> bool:
    return flow_state.get("user_intent") in {"compensation_request", "confirm_compensation"} or contains_any(
        text, "赔", "补偿", "优惠券", "券", "投诉", "太差", "生虫", "异物", "发霉", "变质"
    )


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
    normalized = normalize_signals(case_record, flow_state)
    eligible = eligibility or get_eligible_solutions(case_record, flow_state, registry)
    text = _text(case_record, flow_state)
    result = _empty()
    forbidden: List[str] = []
    if normalized.get("selected_item_state") != "selected" or normalized.get("selected_item_can_refund") is False or normalized.get("order_over_after_sales") is True:
        forbidden.append("小象单商品退款-xx%")
    if normalized.get("can_compensate") is False or normalized.get("already_compensated") is True:
        forbidden.append("操作赔付-优惠券-xx元")
    result["forbidden_solutions"] = forbidden

    # RQ-01 hard refund guard.
    if normalized.get("order_over_after_sales") is True or normalized.get("selected_item_can_refund") is False:
        result.update(
            {
                "priority_rule_id": "RQ-01",
                "decision_type": "guard",
                "no_action_reason": "explain_cannot_refund" if "不可退" in normalized.get("selected_item_refund_status", "") else "policy_explain",
                "rationale": ["超售后或商品不可退款时，不得选择单商品退款，也不要错误引导选择商品。"],
            }
        )
        return result

    # RQ-10 / RQ-09 refund progress before new refund.
    if _refunded(normalized):
        result.update(
            {
                "priority_rule_id": "RQ-10",
                "decision_type": "no_action",
                "no_action_reason": "explain_refund_status",
                "rationale": ["退款已完成，只解释退款状态，不再触发新退款。"],
            }
        )
        return result
    if _refund_progress(normalized, flow_state, text):
        sol = "加急催促退款审核" if contains_any(text, "还没", "怎么还", "再催", "加急") else "催促退款审核;退审跟单"
        result.update(
            {
                "recommended_response_solution": sol,
                "priority_rule_id": "RQ-09",
                "decision_type": "action",
                "rationale": ["退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。"],
            }
        )
        return result

    # RQ-12 compensation guard.
    if (normalized.get("can_compensate") is False or normalized.get("already_compensated") is True) and _wants_compensation(flow_state, text):
        result.update(
            {
                "priority_rule_id": "RQ-12",
                "decision_type": "guard",
                "no_action_reason": "already_compensated" if normalized.get("already_compensated") else "unavailable_capability",
                "rationale": ["已赔或不可赔时禁止赔付。"],
            }
        )
        return result

    # RQ-02 to RQ-06 front guards.
    if normalized.get("selected_item_state") != "selected" and _has(eligible, "选择商品"):
        result.update(
            {
                "recommended_response_solution": "选择商品",
                "priority_rule_id": "RQ-02",
                "decision_type": "action",
                "rationale": ["品质/日期/口感等质量问题缺具体商品，先选择商品。"],
            }
        )
        return result
    if normalized.get("selected_item_state") == "selected" and normalized.get("has_image_evidence") is not True:
        result.update(
            {
                "priority_rule_id": "RQ-03",
                "decision_type": "no_action",
                "no_action_reason": "ask_upload_image",
                "rationale": ["已选商品但缺图片凭证，不能直接退款/赔付。"],
            }
        )
        return result
    if normalized.get("selected_item_state") == "selected" and normalized.get("has_image_evidence") is True and normalized.get("has_refund_reason") is False:
        result.update(
            {
                "priority_rule_id": "RQ-04",
                "decision_type": "no_action",
                "no_action_reason": "ask_refund_reason",
                "rationale": ["已选商品且有图片，但缺退款原因。"],
            }
        )
        return result
    if normalized.get("selected_item_state") == "selected" and normalized.get("has_image_evidence") is True and normalized.get("has_refund_reason") is True and normalized.get("has_refund_ratio") is False:
        result.update(
            {
                "priority_rule_id": "RQ-05",
                "decision_type": "no_action",
                "no_action_reason": "ask_refund_ratio",
                "rationale": ["退款比例未明确，不能直接执行单商品退款。"],
            }
        )
        return result
    if _item_qty(case_record, normalized) > 1 and normalized.get("has_refund_quantity") is False:
        result.update(
            {
                "priority_rule_id": "RQ-06",
                "decision_type": "no_action",
                "no_action_reason": "ask_refund_quantity",
                "rationale": ["多数量商品缺退款数量，不得默认按任意数量处理。"],
            }
        )
        return result

    # RQ-11 compensation after prerequisites.
    if _wants_compensation(flow_state, text) and any(s.startswith("操作赔付-优惠券") for s in eligible.get("eligible_solutions", [])):
        sol = _coupon(normalized.get("compensation_amount_range", ""))
        result.update(
            {
                "recommended_response_solution": sol,
                "recommended_dialogue_agree_solution": sol if explicit_confirm(text) else "无",
                "priority_rule_id": "RQ-11",
                "decision_type": "confirm" if explicit_confirm(text) else "action",
                "rationale": ["用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。"],
            }
        )
        return result

    # RQ-07 / RQ-08 refund.
    if _has(eligible, "小象单商品退款-xx%"):
        sol = _refund_solution(case_record)
        result.update(
            {
                "recommended_response_solution": sol,
                "recommended_dialogue_agree_solution": sol if explicit_confirm(text) else "无",
                "priority_rule_id": "RQ-07" if explicit_confirm(text) else "RQ-08",
                "decision_type": "confirm" if explicit_confirm(text) else "action",
                "rationale": ["商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。"],
            }
        )
        return result

    result.update(
        {
            "priority_rule_id": "RQ-OTHER",
            "decision_type": "no_action",
            "no_action_reason": "close_conversation" if contains_any(text, "谢谢", "没有了", "不用了") else "unknown",
            "rationale": ["未命中 v2 品质动作规则，保持无动作并进入训练师校准候选。"],
        }
    )
    return result


OPEN_QUESTIONS_FOR_TRAINER = [
    "哪些品质子类必须图片前置，哪些可以仅凭文字描述进入退款？",
    "建议退款比例缺失时，是否允许客服先提出经验比例，还是必须追问？",
    "赔付与退款可以同轮复合输出的边界是什么？",
    "多数量商品用户只说“这个坏了”时，是否默认 1 件还是必须询问数量？",
]

