#!/usr/bin/env python3
"""Explicit v2 policy for 履约场景-配送问题."""

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


def _no_rider(status: str) -> bool:
    return any(x in status for x in ["无骑手", "创建履约单", "已推配送", "待接单"])


def _rider_active(status: str) -> bool:
    return any(x in status for x in ["已接单", "配送中", "取货", "到店", "送货"])


def _coupon(range_text: str) -> str:
    lo, hi = parse_amount_range(range_text)
    levels = [3, 5, 8, 10, 15, 20]
    if hi is None:
        return "操作赔付-优惠券-xx元"
    candidates = [x for x in levels if x <= hi and (lo is None or x >= lo)]
    if not candidates:
        candidates = [x for x in levels if x <= hi]
    return f"操作赔付-优惠券-{max(candidates) if candidates else hi}元"


def _eta_question(flow_state: Dict[str, Any], text: str) -> bool:
    return flow_state.get("user_intent") == "eta_question" or contains_any(text, "什么时候送", "几点到", "预计", "多久到", "到哪了")


def _delivery_urge(flow_state: Dict[str, Any], text: str, normalized: Dict[str, Any]) -> bool:
    return flow_state.get("user_intent") in {"delivery_urge", "no_rider"} or contains_any(
        text, "催", "快点", "配送慢", "太慢", "超时", "还没送", "怎么还没到", "没人接单", "没有骑手"
    ) or normalized.get("order_timeout") is True or normalized.get("has_timeout_risk") is True


def _contact_rider(flow_state: Dict[str, Any], text: str) -> bool:
    return flow_state.get("user_intent") == "contact_rider" or contains_any(text, "联系骑手", "骑手电话", "问骑手", "打给骑手")


def decide_fulfillment_delivery(
    case_record: Dict[str, Any],
    flow_state: Dict[str, Any] | None = None,
    registry: Any = None,
    eligibility: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    flow_state = flow_state or {}
    normalized = normalize_signals(case_record, flow_state)
    eligible = eligibility or get_eligible_solutions(case_record, flow_state, registry)
    text = _text(case_record, flow_state)
    rider = normalized.get("rider_status", "")
    order = normalized.get("order_status", "")
    result = _empty()
    forbidden: List[str] = []
    if normalized.get("can_cancel") is False:
        forbidden.append("取消订单")
    if normalized.get("can_compensate") is False or normalized.get("already_compensated") is True:
        forbidden.extend(["操作赔付-优惠券-xx元", "操作赔付-运费券-3元"])
    result["forbidden_solutions"] = forbidden

    # FD-09 / FD-11 hard guards first.
    if normalized.get("can_cancel") is False and contains_any(text, "取消", "不要了"):
        result.update(
            {
                "decision_type": "guard",
                "priority_rule_id": "FD-09",
                "no_action_reason": "unavailable_capability",
                "rationale": ["订单不可取消，禁止 ResponseSolution/DialogueAgreeSolution=取消订单。"],
            }
        )
        return result
    if (normalized.get("can_compensate") is False or normalized.get("already_compensated") is True) and contains_any(text, "赔", "补偿", "优惠券"):
        result.update(
            {
                "decision_type": "guard",
                "priority_rule_id": "FD-11",
                "no_action_reason": "already_compensated" if normalized.get("already_compensated") else "unavailable_capability",
                "rationale": ["不可赔或已赔时禁止再次主动赔付，可改为催单、加急或解释。"],
            }
        )
        return result

    # FD-08 cancel.
    if contains_any(text, "取消", "不要了", "退单") and _has(eligible, "取消订单"):
        result.update(
            {
                "recommended_response_solution": "取消订单",
                "recommended_dialogue_agree_solution": "取消订单" if explicit_confirm(text) else "无",
                "decision_type": "confirm" if explicit_confirm(text) else "action",
                "priority_rule_id": "FD-08",
                "rationale": ["用户有取消诉求且订单可取消；只有明确确认取消时 DialogueAgreeSolution 才能非空。"],
            }
        )
        return result

    # FD-10 compensation.
    if contains_any(text, "赔", "补偿", "优惠券", "投诉", "太慢") and any(s.startswith("操作赔付-优惠券") for s in eligible.get("eligible_solutions", [])):
        sol = _coupon(normalized.get("compensation_amount_range", ""))
        result.update(
            {
                "recommended_response_solution": sol,
                "recommended_dialogue_agree_solution": sol if explicit_confirm(text) else "无",
                "decision_type": "confirm" if explicit_confirm(text) else "action",
                "priority_rule_id": "FD-10",
                "rationale": ["用户因超时/配送慢要求赔付或强烈不满，且赔付信号允许；赔付执行需用户确认。"],
            }
        )
        return result

    # FD-06 repeated call.
    if _has(eligible, "再次外呼骑手-xx"):
        result.update(
            {
                "recommended_response_solution": "再次外呼骑手-催促配送",
                "decision_type": "action",
                "priority_rule_id": "FD-06",
                "rationale": ["最近外呼骑手未接通且用户持续追问，可再次外呼。"],
            }
        )
        return result

    # FD-05 contact rider.
    if _contact_rider(flow_state, text) and _rider_active(rider):
        if _has(eligible, "外呼骑手-xx") and contains_any(text, "帮我", "你问", "客服问", "打电话"):
            result.update(
                {
                    "recommended_response_solution": "外呼骑手-催促配送",
                    "decision_type": "action",
                    "priority_rule_id": "FD-05B",
                    "rationale": ["用户明确要求客服帮忙联系骑手，外呼类方案不要求 DialogueAgreeSolution。"],
                }
            )
            return result
        if _has(eligible, "引导自助联系骑手"):
            result.update(
                {
                    "recommended_response_solution": "引导自助联系骑手",
                    "decision_type": "action",
                    "priority_rule_id": "FD-05A",
                    "rationale": ["用户想联系骑手且骑手已接单/配送中，优先引导自助联系。"],
                }
            )
            return result

    # FD-04 / FD-02 no rider should dispatch before generic urge.
    if _no_rider(rider) and _has(eligible, "加急调度") and (_delivery_urge(flow_state, text, normalized) or _eta_question(flow_state, text)):
        result.update(
            {
                "recommended_response_solution": "加急调度",
                "decision_type": "action",
                "priority_rule_id": "FD-04" if _delivery_urge(flow_state, text, normalized) else "FD-02",
                "rationale": ["骑手状态为无骑手接单/待接单，用户问送达或催促时优先加急调度。"],
            }
        )
        return result

    # FD-03 generic urge.
    if _delivery_urge(flow_state, text, normalized) and _has(eligible, "系统催单"):
        result.update(
            {
                "recommended_response_solution": "系统催单",
                "decision_type": "action",
                "priority_rule_id": "FD-03",
                "rationale": ["用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。"],
            }
        )
        return result

    # FD-12 follow-up.
    if _has(eligible, "智能跟单") and any(x in flow_state.get("last_response_solution", "") for x in ["系统催单", "加急调度", "外呼骑手"]):
        result.update(
            {
                "recommended_response_solution": "智能跟单",
                "decision_type": "action",
                "priority_rule_id": "FD-12",
                "rationale": ["上一轮已执行推进类动作，本轮可持续跟进。"],
            }
        )
        return result

    # FD-07 delivered/status close.
    if any(x in rider + order for x in ["已送达", "已完成"]) and contains_any(text, "到了吗", "送到了", "找到了", "谢谢", "没有了", "我看看"):
        result.update(
            {
                "decision_type": "no_action",
                "priority_rule_id": "FD-07",
                "no_action_reason": "close_conversation" if contains_any(text, "谢谢", "没有了", "找到了") else "explain_status",
                "rationale": ["已送达/已完成的状态咨询或结束语，不触发催单/加急。"],
            }
        )
        return result

    # FD-01 ETA only.
    if _eta_question(flow_state, text) and "履约中" in order and normalized.get("order_timeout") is not True and normalized.get("has_timeout_risk") is not True and not _no_rider(rider):
        result.update(
            {
                "decision_type": "no_action",
                "priority_rule_id": "FD-01",
                "no_action_reason": "eta_answer_only",
                "rationale": ["普通 ETA 咨询可只告知预计送达时间，不承诺一定准时。"],
            }
        )
        return result

    result.update(
        {
            "decision_type": "no_action",
            "priority_rule_id": "FD-OTHER",
            "no_action_reason": "explain_status" if contains_any(text, "状态", "到了", "送达") else "unknown",
            "rationale": ["未命中 v2 配送动作规则，保持无动作并进入训练师校准候选。"],
        }
    )
    return result


OPEN_QUESTIONS_FOR_TRAINER = [
    "普通 ETA 咨询但 rider_status=无骑手接单时，是否总应加急调度，还是先解释预计时间？",
    "系统催单与智能跟单是否允许同轮复合输出，还是主 ResponseSolution 只保留系统催单？",
    "配送超时赔付的优惠券档位应取信号区间上限、下限，还是由训练师根据用户分层决定？",
    "用户要求客服联系骑手时，优先外呼还是先引导自助联系的边界需确认。",
]

