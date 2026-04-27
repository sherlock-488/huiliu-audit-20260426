#!/usr/bin/env python3
"""Decide which prompt-listed solutions are actually executable now."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v2.common import (
    V1_OUT,
    V2_OUT,
    V2_REPORTS,
    canonical_components,
    canonicalize_solution,
    contains_any,
    ensure_dirs,
    extract_amount,
    get_case_records_path,
    get_flow_states_path,
    load_jsonl,
    parse_amount_range,
    read_jsonl,
    top_counter,
    write_jsonl,
)
from flow_skill_policy_v2.policies.signal_normalizer import normalize_signals


NO_RIDER = ("无骑手", "创建履约单", "已推配送", "待接单")
RIDER_ACTIVE = ("已接单", "配送中", "取货", "到店", "送货")
DELIVERED = ("已送达", "送达")
ORDER_ACTIVE = ("履约中", "付款成功", "待配送", "待发货")


def _text(record: Dict[str, Any], flow_state: Dict[str, Any]) -> str:
    return "".join(
        str(x or "")
        for x in [
            record.get("last_user_query"),
            flow_state.get("last_user_query"),
            record.get("dialogue_history", "")[-500:],
        ]
    )


def _available_names(case_record: Dict[str, Any], flow_state: Dict[str, Any]) -> List[str]:
    names: List[str] = []
    for item in case_record.get("available_solutions") or []:
        if isinstance(item, dict):
            names.append(str(item.get("name", "")).strip())
        elif item:
            names.append(str(item).strip())
    if not names:
        names = [str(x).strip() for x in flow_state.get("available_solution_names") or []]
    seen = set()
    out = []
    for name in names:
        canonical, _, _ = canonicalize_solution(name)
        if canonical and canonical not in seen:
            out.append(canonical)
            seen.add(canonical)
    return out


def _scene_needs_item(scene: str) -> bool:
    return any(x in scene for x in ["品质", "少送", "错送", "退款", "日期", "口感", "实描"])


def _needs_image(scene: str, text: str) -> bool:
    return any(x in scene + text for x in ["品质", "日期", "口感", "实描", "异物", "坏", "变质", "发霉", "破损"])


def _is_refund_progress(normalized: Dict[str, Any], flow_state: Dict[str, Any], text: str) -> bool:
    status = normalized.get("refund_status", "")
    return (
        any(x in status for x in ["退款中", "审核", "银行", "处理中", "待审核"])
        or flow_state.get("user_intent") in {"refund_progress", "cannot_refund", "refund_request"}
        or contains_any(text, "退款进度", "什么时候退款", "多久到账", "还没退", "退款怎么")
    )


def _is_delivery_urge(flow_state: Dict[str, Any], text: str, normalized: Dict[str, Any]) -> bool:
    return (
        flow_state.get("user_intent") in {"delivery_urge", "no_rider", "contact_rider"}
        or contains_any(text, "催", "快点", "太慢", "超时", "还没送", "怎么还没到", "没人接单", "没有骑手", "联系骑手", "问骑手")
        or normalized.get("order_timeout") is True
        or normalized.get("has_timeout_risk") is True
    )


def _is_eta_only(flow_state: Dict[str, Any], text: str, normalized: Dict[str, Any]) -> bool:
    return (
        flow_state.get("user_intent") == "eta_question"
        or contains_any(text, "什么时候送", "几点到", "预计", "多久到")
    ) and not _is_delivery_urge(flow_state, text, normalized)


def _wants_compensation(flow_state: Dict[str, Any], text: str) -> bool:
    return flow_state.get("user_intent") in {"compensation_request", "confirm_compensation"} or contains_any(
        text, "赔", "补偿", "优惠券", "券", "投诉", "太差", "不满意"
    )


def _wants_cancel(flow_state: Dict[str, Any], text: str) -> bool:
    return flow_state.get("user_intent") in {"cancel_request", "confirm_cancel"} or contains_any(text, "取消", "不要了", "退单")


def _wants_contact_rider(flow_state: Dict[str, Any], text: str) -> bool:
    return flow_state.get("user_intent") == "contact_rider" or contains_any(text, "联系骑手", "骑手电话", "问下骑手", "帮我问骑手", "打电话给骑手")


def _amount_ok(solution: str, normalized: Dict[str, Any]) -> Tuple[bool, str]:
    amount = extract_amount(solution)
    lo, hi = parse_amount_range(normalized.get("compensation_amount_range", ""))
    if amount is None or hi is None:
        return True, ""
    if amount > hi:
        return False, f"赔付金额{amount}元超过信号上限{hi}元"
    if lo is not None and amount < lo:
        return True, f"赔付金额{amount}元低于信号下限{lo}元，需训练师确认"
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
    """Return eligible prompt solutions and guarded-out candidates."""

    flow_state = flow_state or {}
    normalized = normalize_signals(case_record, flow_state)
    scene = case_record.get("scene") or flow_state.get("scene") or ""
    text = _text(case_record, flow_state)
    available = _available_names(case_record, flow_state)
    result: Dict[str, Any] = {
        "sample_id": case_record.get("sample_id") or flow_state.get("sample_id"),
        "scene": scene,
        "available_solutions": available,
        "eligible_solutions": [],
        "ineligible_solutions": [],
        "guards": [],
        "warnings": [],
        "normalized_signals": normalized,
    }

    rider = normalized.get("rider_status", "")
    order = normalized.get("order_status", "")
    delivery_order = normalized.get("is_delivery_order")
    delivery_urge = _is_delivery_urge(flow_state, text, normalized)
    eta_only = _is_eta_only(flow_state, text, normalized)
    wants_contact = _wants_contact_rider(flow_state, text)
    wants_cancel = _wants_cancel(flow_state, text)
    wants_comp = _wants_compensation(flow_state, text)

    for solution in available:
        ok = False
        reason = ""
        warning = ""
        if solution == "无":
            continue
        if solution.startswith("操作赔付-优惠券") or solution.startswith("操作赔付-运费券"):
            amount_ok, amount_warning = _amount_ok(solution, normalized)
            if normalized.get("can_compensate") is False:
                reason = "订单不可赔付"
            elif normalized.get("already_compensated") is True:
                reason = "订单已赔付过"
            elif not amount_ok:
                reason = amount_warning
            elif wants_comp or normalized.get("order_timeout") is True or "品质" in scene:
                ok = True
                warning = amount_warning
            else:
                reason = "候选方案存在，但当前用户诉求/流程未显示需要赔付"
        elif solution == "取消订单":
            if normalized.get("can_cancel") is False:
                reason = "订单不可取消"
            elif wants_cancel or contains_any(text, "改不了", "送太慢不想要"):
                ok = True
            else:
                reason = "用户当前未表达取消诉求"
        elif solution == "系统催单":
            if eta_only:
                reason = "普通 ETA 咨询不一定需要催单"
            elif delivery_order is False:
                reason = "非配送单"
            elif not any(x in order for x in ORDER_ACTIVE):
                reason = "订单状态不适合催单"
            elif any(x in rider for x in DELIVERED):
                reason = "骑手/订单已送达"
            elif delivery_urge:
                ok = True
            else:
                reason = "未识别到催配送意图"
        elif solution == "加急调度":
            if not any(x in rider for x in NO_RIDER):
                reason = "骑手状态不是无骑手接单/待接单"
            elif delivery_order is False:
                reason = "非配送单"
            elif not any(x in order for x in ORDER_ACTIVE):
                reason = "订单状态不适合加急调度"
            elif delivery_urge or _is_eta_only(flow_state, text, normalized):
                ok = True
            else:
                reason = "无骑手信号存在，但当前轮未识别到送达/接单诉求"
        elif solution == "智能跟单":
            prev = flow_state.get("last_response_solution", "")
            if any(x in prev for x in ["系统催单", "加急调度", "外呼骑手", "催促退款审核"]):
                ok = True
            elif delivery_urge and not eta_only:
                ok = True
                warning = "未看到已执行前置动作，作为跟进动作需训练师确认"
            else:
                reason = "没有已执行推进类方案或持续跟进需求"
        elif solution == "无骑手接单跟单":
            if any(x in rider for x in NO_RIDER) and contains_any(text, "修改地址", "改地址", "改时间", "改备注", "联系骑手"):
                ok = True
            else:
                reason = "未同时满足无骑手接单和需等待骑手协商的问题"
        elif solution == "引导自助联系骑手":
            if wants_contact and any(x in rider for x in RIDER_ACTIVE):
                ok = True
            else:
                reason = "用户未要求联系骑手或骑手状态不支持"
        elif solution == "外呼骑手-xx":
            if wants_contact and any(x in rider for x in RIDER_ACTIVE) and normalized.get("has_rider_phone") is not False:
                ok = True
            else:
                reason = "未满足客服外呼骑手条件"
        elif solution == "再次外呼骑手-xx":
            recent = (case_record.get("dialogue_history") or "")[-800:]
            if wants_contact and "未接通" in recent and any(x in rider for x in RIDER_ACTIVE):
                ok = True
            else:
                reason = "缺少最近外呼未接通且用户持续追问的证据"
        elif solution == "选择商品":
            if _scene_needs_item(scene) and normalized.get("selected_item_state") != "selected":
                ok = True
            else:
                reason = "当前不缺商品选择前置"
        elif solution == "小象单商品退款-xx%":
            if normalized.get("selected_item_state") != "selected":
                reason = "未选择具体商品"
            elif normalized.get("selected_item_can_refund") is False or normalized.get("order_over_after_sales") is True:
                reason = "商品不可退款或订单超售后"
            elif _needs_image(scene, text) and normalized.get("has_image_evidence") is not True:
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
            if contains_any(text, "整单", "全部退款", "整个订单") and "商品" not in text:
                ok = True
            else:
                reason = "未识别到整单退款诉求"
        elif solution in {"催促退款审核", "加急催促退款审核", "退审跟单"}:
            if _is_refund_progress(normalized, flow_state, text):
                ok = True
            else:
                reason = "退款状态/用户诉求不满足催审"
        elif solution == "发送送达图片":
            if normalized.get("has_delivery_photo") is True and contains_any(text, "没收到", "找不到", "送哪", "放哪", "没看见"):
                ok = True
            else:
                reason = "缺送达图片或用户未反馈未找到包裹"
        elif solution in {"开发票", "管理会员自动续费", "引导自助修改订单", "引导自助联系骑手", "引导自助管理地址", "引导自助开通会员"} or solution.startswith("引导自助查看"):
            ok = contains_any(scene + text, "发票", "会员", "续费", "权益", "配送范围", "优惠券", "修改", "地址", "联系骑手", "开通")
            if not ok:
                reason = "候选自助/业务工具与当前场景或诉求不匹配"
        elif solution.startswith("外呼门店") or solution.startswith("再次外呼门店"):
            ok = contains_any(text, "门店", "商家", "店里", "分拣", "缺货", "修改订单")
            if not ok:
                reason = "未识别到需联系门店的问题"
        else:
            # Unknown tools stay conservative: they are candidates but not executable without a rule.
            reason = "未配置 v2 eligibility 规则"
        _add(result, solution, ok, reason, warning)
    return result


def _load_maps() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    cases = {row["sample_id"]: row for row in read_jsonl(get_case_records_path())}
    flows = {row["sample_id"]: row for row in read_jsonl(get_flow_states_path())}
    no_action = {row["sample_id"]: row for row in read_jsonl(V1_OUT / "no_action_labeled_v1.jsonl")}
    return cases, flows, no_action


def _r12_sample_ids() -> set[str]:
    path = V1_OUT / "global_checker_result_v1.jsonl"
    ids = set()
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
    cases, flows, no_action = _load_maps()
    rows = []
    eligible_counts = Counter()
    ineligible_reasons: Dict[str, Counter] = defaultdict(Counter)
    available_ineligible = Counter()
    r12_ids = _r12_sample_ids()
    r12_eligible = 0
    r12_ineligible_only = 0
    possible_missing_eligible = 0
    for sid, case in cases.items():
        flow = flows.get(sid, {})
        result = get_eligible_solutions(case, flow, registry)
        rows.append(result)
        for sol in result["eligible_solutions"]:
            eligible_counts[sol] += 1
        for item in result["ineligible_solutions"]:
            ineligible_reasons[item["solution"]][item["reason"]] += 1
            available_ineligible[item["solution"]] += 1
        has_action = bool([s for s in result["eligible_solutions"] if s not in {"无"}])
        if sid in r12_ids:
            if has_action:
                r12_eligible += 1
            else:
                r12_ineligible_only += 1
        if (no_action.get(sid) or {}).get("possible_missing_action") and has_action:
            possible_missing_eligible += 1

    out_path = V2_OUT / "eligibility_results.jsonl"
    write_jsonl(out_path, rows)

    report = [
        "# Eligibility Engine Report",
        "",
        f"- total_cases: `{len(rows)}`",
        f"- v1_R12_cases: `{len(r12_ids)}`",
        f"- v1_R12_with_eligible_action: `{r12_eligible}`",
        f"- v1_R12_available_but_ineligible_only: `{r12_ineligible_only}`",
        f"- no_action_v1_possible_missing_with_eligible_action: `{possible_missing_eligible}`",
        "",
        "## Eligible Counts",
        top_counter(eligible_counts, 80) or "- none",
        "",
        "## Available But Ineligible Top",
        top_counter(available_ineligible, 80) or "- none",
        "",
        "## Ineligible Top Reasons",
    ]
    for sol, counter in sorted(ineligible_reasons.items(), key=lambda kv: sum(kv[1].values()), reverse=True)[:80]:
        report.append(f"### {sol}")
        report.append(top_counter(counter, 10) or "- none")
    (V2_REPORTS / "eligibility_engine_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
