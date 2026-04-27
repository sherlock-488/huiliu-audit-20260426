#!/usr/bin/env python3
"""Build abstract FlowState records."""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import (
    OUT_DIR,
    REPORT_DIR,
    compact_counter,
    ensure_dirs,
    load_jsonl_list,
    split_components,
    write_jsonl,
    yes_no_to_bool,
)


INPUT_PATH = OUT_DIR / "session_trajectories.jsonl"
OUTPUT_PATH = OUT_DIR / "flow_states.jsonl"
REPORT_PATH = REPORT_DIR / "flow_state_report.md"


CORE_SIGNAL_KEYS = [
    "订单状态",
    "是否为配送单",
    "是否为自提单",
    "订单类型",
    "订单骑手状态",
    "订单门店状态",
    "订单是否超时",
    "履约中未超时订单是否有超时风险",
    "是否可取消订单",
    "订单退款状态",
    "订单是否有退款记录",
    "订单是否超售后",
    "是否赔付过",
    "订单是否可赔付",
    "用户分层标签",
    "是否有骑手真实手机号",
    "骑手是否有送达图片",
    "是否会员",
]


def _contains(text: str, *words: str) -> bool:
    return any(word in text for word in words)


def classify_user_intent(last_user_query: str, scene: str, dialogue_history: str = "") -> str:
    q = (last_user_query or "").strip()
    text = q + "\n" + (dialogue_history or "")[-300:]
    if re.fullmatch(r"(人工|转人工|客服|人工客服|转客服|转人工客服|真人|转真人).*", q):
        return "transfer_request"
    if _contains(q, "什么时候送", "多久送", "几点送", "送到", "到哪", "配送进度"):
        return "eta_question"
    if _contains(q, "催", "快点", "赶紧", "尽快", "太慢"):
        return "delivery_urge"
    if _contains(q, "没有骑手", "无骑手", "没人接单"):
        return "no_rider"
    if _contains(q, "联系骑手", "骑手电话", "打骑手", "找骑手"):
        return "contact_rider"
    if _contains(q, "修改", "改地址", "改时间", "改备注", "换地址", "改电话"):
        return "modify_order"
    if _contains(q, "取消", "不要了", "不想要"):
        return "cancel_request"
    if _contains(q, "退款进度", "退款什么时候", "多久到账", "没到账", "审核"):
        return "refund_progress"
    if _contains(q, "退款", "退钱", "退给我", "申请退款"):
        return "refund_request"
    if _contains(q, "不能退", "不可退", "退不了"):
        return "cannot_refund"
    if _contains(q, "赔", "补偿", "优惠券", "运费券"):
        if _contains(q, "可以", "同意", "接受", "行", "好"):
            return "compensation_accept"
        if _contains(q, "不要", "不同意", "不接受"):
            return "compensation_reject"
        return "compensation_request"
    if _contains(q, "可以", "同意", "行", "好", "确认"):
        if _contains(scene, "退款"):
            return "confirm_refund"
        if _contains(scene, "赔", "品质", "少送", "错送"):
            return "confirm_compensation"
        if _contains(scene, "取消"):
            return "confirm_cancel"
    if _contains(q, "质量", "坏", "烂", "变质", "异味", "不新鲜", "发霉"):
        return "quality_issue"
    if _contains(q, "日期", "过期", "临期", "生产日期"):
        return "date_issue"
    if _contains(q, "少送", "少了", "漏发", "没给", "缺少"):
        return "short_delivery"
    if _contains(q, "错送", "送错", "不是我买的"):
        return "wrong_delivery"
    if _contains(q, "没收到", "未收到", "没拿到", "找不到", "没有收到"):
        return "not_received_after_delivered"
    if _contains(q, "发票", "开票"):
        return "invoice_request"
    if _contains(q, "自动续费", "续费", "关闭会员"):
        return "member_auto_renew"
    if _contains(q, "会员退款", "退会员", "会员卡退款"):
        return "member_refund"
    if _contains(q, "会员权益", "权益", "会员"):
        return "member_benefit"
    if _contains(q, "券", "优惠", "活动", "省钱卡"):
        return "activity_coupon"
    if _contains(q, "支付", "付款", "扣款", "钱"):
        return "payment_issue"
    if _contains(q, "有没有", "怎么下单", "配送范围", "商品"):
        return "presale_consult"
    if _contains(q, "没有了", "不用了", "谢谢", "没事", "再见"):
        return "close_conversation"
    return "other"


def selected_sku_state(record: Dict[str, Any]) -> str:
    info = record.get("selected_item_info") or {}
    if info.get("已选择退款商品") or info.get("已选择商品"):
        return "selected"
    if record.get("items"):
        return "not_selected"
    return "unknown"


def image_state(record: Dict[str, Any]) -> str:
    info = record.get("selected_item_info") or {}
    value = str(info.get("是否已收集图片凭证", "")).strip()
    if value == "是":
        return "has_image"
    if value == "否":
        return "missing_image"
    text = (record.get("dialogue_history", "") or "") + "\n" + (record.get("last_user_query", "") or "")
    if "【图片】" in text or "系统识别图片" in text:
        return "has_image"
    return "unknown"


def can_refund_state(record: Dict[str, Any]) -> str:
    info = record.get("selected_item_info") or {}
    if info.get("商品退款状态"):
        return str(info.get("商品退款状态"))
    statuses = collections.Counter(
        str(item.get("商品退款状态", "")) for item in record.get("items", []) if item.get("商品退款状态")
    )
    if statuses:
        return ";".join(f"{k}:{v}" for k, v in statuses.most_common())
    return ""


def build_state(record: Dict[str, Any]) -> Dict[str, Any]:
    signals = record.get("signals", {}) or {}
    last_user_query = record.get("last_user_query", "")
    scene = record.get("scene", "")
    refund_record_text = str(signals.get("订单是否有退款记录", "")).strip()
    refund_record_head = refund_record_text.split()[0] if refund_record_text.split() else ""
    return {
        "sample_id": record.get("sample_id", ""),
        "session_id": record.get("session_id", ""),
        "turn_index": record.get("turn_index", 0),
        "scene": scene,
        "scene_l1": record.get("scene_l1", ""),
        "scene_l2": record.get("scene_l2", ""),
        "user_intent": classify_user_intent(last_user_query, scene, record.get("dialogue_history", "")),
        "order_status": signals.get("订单状态", ""),
        "is_delivery_order": yes_no_to_bool(signals.get("是否为配送单")),
        "is_pickup_order": yes_no_to_bool(signals.get("是否为自提单")),
        "order_type": signals.get("订单类型", ""),
        "rider_status": signals.get("订单骑手状态", ""),
        "store_status": signals.get("订单门店状态", ""),
        "timeout_state": signals.get("订单是否超时", "") or signals.get("履约中订单超时时长", ""),
        "has_timeout_risk": yes_no_to_bool(signals.get("履约中未超时订单是否有超时风险")),
        "can_cancel": yes_no_to_bool(signals.get("是否可取消订单")),
        "refund_state": signals.get("订单退款状态", ""),
        "has_refund_record": yes_no_to_bool(refund_record_head),
        "selected_sku_state": selected_sku_state(record),
        "image_state": image_state(record),
        "can_refund_state": can_refund_state(record),
        "can_compensate": yes_no_to_bool(signals.get("订单是否可赔付")),
        "already_compensated": yes_no_to_bool(signals.get("是否赔付过")),
        "compensation_range": signals.get("赔付金额", "") or signals.get("可赔付金额", ""),
        "user_value_tier": signals.get("用户分层标签", ""),
        "has_rider_phone": yes_no_to_bool(signals.get("是否有骑手真实手机号")),
        "has_delivery_photo": yes_no_to_bool(signals.get("骑手是否有送达图片")),
        "last_response_solution": record.get("prev_response_solution_raw", ""),
        "pending_confirmation_solution": record.get("pending_confirmation_solution", ""),
        "response_solution_raw": record.get("response_solution_raw", ""),
        "response_solution_components": record.get("response_solution_components", []),
        "dialogue_agree_solution_raw": record.get("dialogue_agree_solution_raw", ""),
        "dialogue_agree_solution_components": record.get("dialogue_agree_solution_components", []),
        # Extra fields for downstream mining/checking.
        "available_solution_names": [
            sol.get("name", "") for sol in record.get("available_solutions", []) if sol.get("name")
        ],
        "signals": signals,
        "items": record.get("items", []),
        "selected_item_info": record.get("selected_item_info", {}),
        "last_user_query": last_user_query,
        "dialogue_history": record.get("dialogue_history", ""),
        "response": record.get("response", ""),
    }


def main() -> None:
    ensure_dirs()
    records = load_jsonl_list(INPUT_PATH)
    states = [build_state(record) for record in records]
    write_jsonl(OUTPUT_PATH, states)

    scene_intent = collections.defaultdict(collections.Counter)
    scene_resp = collections.defaultdict(collections.Counter)
    scene_agree = collections.defaultdict(collections.Counter)
    signal_coverage = collections.Counter()
    missing_by_scene = collections.defaultdict(int)
    for state in states:
        scene = state["scene"]
        scene_intent[scene][state["user_intent"]] += 1
        scene_resp[scene][state["response_solution_raw"]] += 1
        scene_agree[scene][state["dialogue_agree_solution_raw"]] += 1
        signals = state.get("signals", {})
        missing_core = 0
        for key in CORE_SIGNAL_KEYS:
            if signals.get(key) not in (None, ""):
                signal_coverage[key] += 1
            else:
                missing_core += 1
        missing_by_scene[scene] += missing_core

    total = len(states)
    md = []
    md.append("# FlowState 报告")
    md.append("")
    md.append(f"- FlowState 数: `{total}`")
    md.append("- user_intent 是弱规则标签，只用于聚合分析，不能替代训练师 `问题场景`。")
    md.append("")
    md.append("## 核心信号覆盖率")
    for key in CORE_SIGNAL_KEYS:
        md.append(f"- `{key}`: `{signal_coverage[key]}` ({signal_coverage[key] / total:.2%})")
    md.append("")
    md.append("## 各 scene 的 user_intent 分布 TOP")
    for scene, ctr in sorted(scene_intent.items(), key=lambda kv: -sum(kv[1].values()))[:30]:
        md.append(f"### {scene}")
        md.append(compact_counter(ctr, 12))
    md.append("")
    md.append("## 各 scene 的 ResponseSolution 分布 TOP")
    for scene, ctr in sorted(scene_resp.items(), key=lambda kv: -sum(kv[1].values()))[:20]:
        md.append(f"### {scene}")
        md.append(compact_counter(ctr, 12))
    md.append("")
    md.append("## 各 scene 的 DialogueAgreeSolution 分布 TOP")
    for scene, ctr in sorted(scene_agree.items(), key=lambda kv: -sum(kv[1].values()))[:20]:
        md.append(f"### {scene}")
        md.append(compact_counter(ctr, 12))
    md.append("")
    md.append("## 缺关键信号最多的场景")
    for scene, missing in sorted(missing_by_scene.items(), key=lambda kv: -kv[1])[:30]:
        md.append(f"- `{scene}`: `{missing}`")
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"flow_states": len(states), "report": str(REPORT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
