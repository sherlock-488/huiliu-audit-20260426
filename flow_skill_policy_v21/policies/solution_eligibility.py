#!/usr/bin/env python3
"""Policy v21 eligibility engine with current-turn gating."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v21.common import (
    V1_OUT,
    V2_REPORTS,
    V21_OUT,
    V21_REPORTS,
    canonicalize_solution,
    contains_any,
    ensure_dirs,
    extract_amount,
    get_case_records_path,
    get_flow_states_path,
    parse_amount_range,
    read_jsonl,
    top_counter,
    write_jsonl,
)
from flow_skill_policy_v21.policies.confirmation_resolver import resolve_pending_confirmation
from flow_skill_policy_v21.policies.current_turn_intent import classify_current_turn
from flow_skill_policy_v21.policies.signal_normalizer import normalize_signals


ACTIVE_ORDER = ("履约中", "付款成功")
NO_RIDER = ("无骑手", "创建履约单", "已推配送", "待接单")
RIDER_ACTIVE = ("已接单", "配送中", "取货", "到店", "送货")


def _last_query(case_record: Dict[str, Any], flow_state: Dict[str, Any]) -> str:
    return str(case_record.get("last_user_query") or flow_state.get("last_user_query") or "")


def _available(case_record: Dict[str, Any], flow_state: Dict[str, Any]) -> List[str]:
    names = []
    for item in case_record.get("available_solutions") or []:
        names.append(item.get("name", "") if isinstance(item, dict) else str(item))
    if not names:
        names = [str(x) for x in flow_state.get("available_solution_names") or []]
    out, seen = [], set()
    for name in names:
        canonical, _, _ = canonicalize_solution(name)
        if canonical and canonical not in seen:
            out.append(canonical)
            seen.add(canonical)
    return out


def _intents(intent: Dict[str, Any]) -> set[str]:
    return set(intent.get("current_intents") or [])


def _refund_active(status: str) -> bool:
    # v21 intentionally excludes generic "订单部分退款" / "订单无退款".
    return any(x in (status or "") for x in ["退款中", "审核中", "客服审核", "银行退款中", "银行处理中", "处理中", "待审核"])


def _amount_ok(solution: str, normalized: Dict[str, Any]) -> Tuple[bool, str]:
    amount = extract_amount(solution)
    lo, hi = parse_amount_range(normalized.get("compensation_amount_range", ""))
    if amount is None or hi is None:
        return True, ""
    if amount > hi:
        return False, f"赔付金额{amount}元超过信号上限{hi}元"
    if lo is not None and amount < lo:
        return True, f"赔付金额{amount}元低于信号下限{lo}元"
    return True, ""


def _add(result: Dict[str, Any], solution: str, ok: bool, reason: str = "", warning: str = "") -> None:
    if ok:
        if solution not in result["eligible_solutions"]:
            result["eligible_solutions"].append(solution)
    else:
        result["ineligible_solutions"].append({"solution": solution, "reason": reason})
    if reason:
        result["guards"].append(f"{solution}: {reason}")
    if warning:
        result["warnings"].append(f"{solution}: {warning}")


def get_eligible_solutions(case_record: Dict[str, Any], flow_state: Dict[str, Any] | None, registry: Any = None) -> Dict[str, Any]:
    flow_state = flow_state or {}
    normalized = normalize_signals(case_record, flow_state)
    current = classify_current_turn(_last_query(case_record, flow_state))
    resolver = resolve_pending_confirmation(case_record, flow_state, current, registry)
    intents = _intents(current)
    available = _available(case_record, flow_state)
    scene = case_record.get("scene") or flow_state.get("scene") or ""
    rider = normalized.get("rider_status", "")
    order = normalized.get("order_status", "")
    history_tail = (case_record.get("dialogue_history") or "")[-800:]
    result: Dict[str, Any] = {
        "sample_id": case_record.get("sample_id") or flow_state.get("sample_id"),
        "scene": scene,
        "available_solutions": available,
        "eligible_solutions": [],
        "ineligible_solutions": [],
        "guards": [],
        "warnings": [],
        "normalized_signals": normalized,
        "current_turn_intent": current,
        "confirmation": resolver,
    }

    for solution in available:
        ok = False
        reason = ""
        warning = ""
        if solution.startswith("操作赔付-优惠券") or solution.startswith("操作赔付-运费券"):
            amount_ok, amount_warning = _amount_ok(solution, normalized)
            if normalized.get("can_compensate") is False:
                reason = "订单不可赔付"
            elif normalized.get("already_compensated") is True:
                reason = "订单已赔付过"
            elif not amount_ok:
                reason = amount_warning
            elif "compensation_request" in intents or resolver.get("confirmed_solution") in {"操作赔付-优惠券-xx元", "操作赔付-运费券-3元"}:
                ok = True
                warning = amount_warning
            else:
                reason = "当前轮没有赔付诉求或 pending compensation confirmation"
        elif solution == "取消订单":
            if normalized.get("can_cancel") is False:
                reason = "订单不可取消"
            elif "cancel_request" in intents or resolver.get("confirmed_solution") == "取消订单":
                ok = True
            else:
                reason = "当前轮没有取消诉求或 pending cancel confirmation"
        elif solution == "系统催单":
            if not ({"delivery_urge"} & intents or (("eta_question" in intents) and (normalized.get("has_timeout_risk") is True or normalized.get("order_timeout") is True))):
                reason = "当前轮不是催配送，也不是超时/风险 ETA 咨询"
            elif normalized.get("is_delivery_order") is False:
                reason = "非配送单"
            elif not any(x in order for x in ACTIVE_ORDER):
                reason = "订单状态不适合催单"
            elif any(x in rider for x in ["已送达"]):
                reason = "骑手已送达"
            else:
                ok = True
        elif solution == "加急调度":
            if not any(x in rider for x in NO_RIDER):
                reason = "骑手状态不是无骑手/待接单"
            elif not ({"eta_question", "delivery_urge", "no_rider"} & intents):
                reason = "当前轮没有 ETA/催接单/无骑手诉求"
            elif normalized.get("is_delivery_order") is False:
                reason = "非配送单"
            elif not any(x in order for x in ACTIVE_ORDER):
                reason = "订单状态不适合加急调度"
            else:
                ok = True
        elif solution == "智能跟单":
            if any(x in flow_state.get("last_response_solution", "") for x in ["系统催单", "加急调度", "外呼骑手"]) and contains_any(_last_query(case_record, flow_state), "别忘", "继续", "还没到", "盯", "跟进"):
                ok = True
            else:
                reason = "当前轮没有持续跟进诉求或缺少上一轮推进动作"
        elif solution == "无骑手接单跟单":
            if any(x in rider for x in NO_RIDER) and {"delivery_urge", "no_rider"} & intents and contains_any(_last_query(case_record, flow_state), "修改", "地址", "时间", "备注"):
                ok = True
            else:
                reason = "未满足当前轮无骑手接单跟单条件"
        elif solution == "引导自助联系骑手":
            if "contact_rider" in intents and any(x in rider for x in RIDER_ACTIVE):
                ok = True
            else:
                reason = "当前轮没有联系骑手诉求或骑手状态不支持"
        elif solution == "外呼骑手-xx":
            if "contact_rider" in intents and any(x in rider for x in RIDER_ACTIVE) and normalized.get("has_rider_phone") is not False:
                ok = True
            else:
                reason = "当前轮未满足外呼骑手条件"
        elif solution == "再次外呼骑手-xx":
            if "contact_rider" in intents and "未接通" in history_tail and any(x in rider for x in RIDER_ACTIVE):
                ok = True
            else:
                reason = "缺少当前联系骑手诉求或最近外呼未接通证据"
        elif solution == "选择商品":
            if current.get("is_close_or_thanks") or current.get("is_ack_only") or current.get("is_transfer_only"):
                reason = "当前轮是结束/弱确认/转人工，不触发选择商品"
            elif ({"quality_issue", "refund_request"} & intents) and normalized.get("selected_item_state") != "selected":
                ok = True
            else:
                reason = "当前轮没有品质/退款诉求或已选商品"
        elif solution == "小象单商品退款-xx%":
            if current.get("is_close_or_thanks"):
                reason = "当前轮结束语不触发退款"
            elif not ({"refund_request", "quality_issue", "confirm_refund"} & intents or resolver.get("confirmed_solution") == "小象单商品退款-xx%"):
                reason = "当前轮没有退款/品质诉求或 pending refund confirmation"
            elif normalized.get("selected_item_state") != "selected":
                reason = "未选择具体商品"
            elif normalized.get("selected_item_can_refund") is False or normalized.get("order_over_after_sales") is True:
                reason = "商品不可退款或订单超售后"
            elif normalized.get("has_image_evidence") is not True and "quality_issue" in intents:
                reason = "缺图片凭证"
            elif normalized.get("has_refund_reason") is False:
                reason = "缺退款原因"
            elif normalized.get("has_refund_ratio") is False:
                reason = "缺退款比例"
            elif normalized.get("has_refund_quantity") is False:
                reason = "缺退款数量"
            else:
                ok = True
        elif solution == "小象整单申请退款":
            if "refund_request" in intents and contains_any(_last_query(case_record, flow_state), "整单", "全部退款", "整个订单"):
                ok = True
            else:
                reason = "当前轮未识别到整单退款诉求"
        elif solution in {"催促退款审核", "加急催促退款审核", "退审跟单"}:
            status = normalized.get("refund_status", "") + normalized.get("selected_item_refund_status", "")
            if "refund_progress" in intents and _refund_active(status):
                ok = True
            else:
                reason = "当前轮不是退款进度诉求或退款状态不是进行中/审核中"
        elif solution == "发送送达图片":
            if normalized.get("has_delivery_photo") is True and contains_any(_last_query(case_record, flow_state), "没收到", "找不到", "送哪", "放哪", "没看见"):
                ok = True
            else:
                reason = "缺送达图片或当前轮未反馈未找到包裹"
        elif solution in {"开发票", "管理会员自动续费", "引导自助修改订单", "引导自助联系骑手", "引导自助管理地址", "引导自助开通会员"} or solution.startswith("引导自助查看"):
            if current.get("has_new_action_intent") and contains_any(scene + _last_query(case_record, flow_state), "发票", "会员", "续费", "权益", "配送范围", "优惠券", "修改", "地址", "联系骑手", "开通"):
                ok = True
            else:
                reason = "当前轮诉求不匹配该自助/业务工具"
        elif solution.startswith("外呼门店") or solution.startswith("再次外呼门店"):
            if current.get("has_new_action_intent") and contains_any(_last_query(case_record, flow_state), "门店", "商家", "店里", "分拣", "缺货", "修改订单"):
                ok = True
            else:
                reason = "当前轮未识别到联系门店诉求"
        else:
            reason = "未配置 v21 eligibility 规则"
        _add(result, solution, ok, reason, warning)
    return result


def _r12_ids() -> set[str]:
    ids = set()
    path = V1_OUT / "global_checker_result_v1.jsonl"
    if not path.exists():
        return ids
    for row in read_jsonl(path):
        if any(issue.get("rule") == "R12" for issue in row.get("issues", [])):
            ids.add(row.get("sample_id"))
    return ids


def main() -> None:
    ensure_dirs()
    registry_path = V1_OUT / "solution_registry_v1.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else []
    flows = {row["sample_id"]: row for row in read_jsonl(get_flow_states_path())}
    r12_ids = _r12_ids()
    rows = []
    eligible_counts = Counter()
    ineligible = defaultdict(Counter)
    r12_eligible = 0
    close_ack_with_action = 0
    for case in read_jsonl(get_case_records_path()):
        flow = flows.get(case.get("sample_id"), {})
        result = get_eligible_solutions(case, flow, registry)
        rows.append(result)
        for sol in result["eligible_solutions"]:
            eligible_counts[sol] += 1
        for item in result["ineligible_solutions"]:
            ineligible[item["solution"]][item["reason"]] += 1
        if case.get("sample_id") in r12_ids and result["eligible_solutions"]:
            r12_eligible += 1
        current = result["current_turn_intent"]
        if (current.get("is_close_or_thanks") or current.get("is_ack_only") or current.get("is_transfer_only")) and result["eligible_solutions"]:
            close_ack_with_action += 1
    write_jsonl(V21_OUT / "eligibility_results_v21.jsonl", rows)
    v2_r12 = "unknown"
    v2_report = V2_REPORTS / "eligibility_engine_report.md"
    if v2_report.exists():
        text = v2_report.read_text(encoding="utf-8")
        import re

        m = re.search(r"v1_R12_with_eligible_action: `(\d+)`", text)
        if m:
            v2_r12 = m.group(1)
    report = [
        "# Eligibility Engine v21 Report",
        "",
        f"- total_cases: `{len(rows)}`",
        f"- v2_R12_with_eligible_action: `{v2_r12}`",
        f"- v21_R12_with_eligible_action: `{r12_eligible}`",
        f"- close_ack_transfer_samples_with_any_eligible_action: `{close_ack_with_action}`",
        "",
        "## Eligible Counts",
        top_counter(eligible_counts, 80) or "- none",
        "",
        "## Ineligible Top Reasons",
    ]
    for sol, counter in sorted(ineligible.items(), key=lambda kv: sum(kv[1].values()), reverse=True)[:80]:
        report.append(f"### {sol}")
        report.append(top_counter(counter, 8) or "- none")
    (V21_REPORTS / "eligibility_engine_v21_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
