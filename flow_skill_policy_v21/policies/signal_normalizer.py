#!/usr/bin/env python3
"""Normalize Chinese business signals into policy v21 fields."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v21.common import yes_no


def _first(*values: Any) -> str:
    for value in values:
        if value not in (None, ""):
            return str(value).strip()
    return ""


EMPTY_VALUES = {"", "无", "未知", "不涉及", "None", "null", "NULL"}


def _yes_no_loose(value: Any) -> Optional[bool]:
    parsed = yes_no(value)
    if parsed is not None:
        return parsed
    s = "" if value is None else str(value).strip()
    if s.startswith(("是", "有", "可", "可以")):
        return True
    if s.startswith(("否", "无", "不可", "不可以")):
        return False
    return None


def _compensation_range(signals: Dict[str, Any], flow_state: Dict[str, Any]) -> str:
    direct = _first(signals.get("赔付金额"), signals.get("可赔付金额"), flow_state.get("compensation_range"))
    if direct:
        return direct
    text = _first(signals.get("订单是否可赔付"), signals.get("是否可赔付"))
    match = re.search(r"赔付金额[:：]?\s*([^,，;；\s]+)", text)
    return match.group(1) if match else ""


def _minutes(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None


def _selected_item_name(selected_info: Dict[str, Any]) -> str:
    for key in ["已选择退款商品", "已选择商品", "商品名称", "已选择商品信息"]:
        value = selected_info.get(key)
        if value not in (None, "", "无", "不涉及"):
            return str(value).strip()
    return ""


def _selected_item_refund_status(selected_name: str, selected_info: Dict[str, Any], items: list, warnings: list) -> str:
    direct = _first(selected_info.get("商品退款状态"), selected_info.get("退款状态"), selected_info.get("是否可退款"))
    if direct:
        return direct
    if selected_name:
        for item in items or []:
            name = str(item.get("商品名称", ""))
            if selected_name in name or name in selected_name:
                return _first(item.get("商品退款状态"), item.get("退款状态"), item.get("是否可退款"))
        warnings.append("selected_item_unmatched")
        return ""
    statuses = [_first(item.get("商品退款状态"), item.get("退款状态"), item.get("是否可退款")) for item in items or []]
    statuses = [s for s in statuses if s]
    if len(set(statuses)) > 1:
        warnings.append("mixed_item_refund_status_without_selection")
    # v21: when no item is selected, do not collapse item statuses into a selected
    # item refund status. The policy should choose item first.
    return ""


def _has_value(value: Any) -> Optional[bool]:
    if value is None:
        return None
    s = str(value).strip()
    if s in EMPTY_VALUES:
        return False
    yn = _yes_no_loose(s)
    if yn is not None:
        return yn
    return True


def _selected_state(selected_name: str, items: list, flow_state: Dict[str, Any], warnings: list) -> str:
    flow_selected = flow_state.get("selected_sku_state")
    if selected_name or flow_selected == "selected":
        return "selected"
    if len(items or []) > 1:
        warnings.append("multiple_items_no_selected_item")
    if items or flow_selected == "not_selected":
        return "not_selected"
    return "unknown"


def _can_refund(status: str) -> Optional[bool]:
    if not status:
        return None
    if "不可退款" in status or "不可退" in status or "超售后" in status:
        return False
    if "可退款" in status or status in {"是", "可", "可以"}:
        return True
    return None


def normalize_signals(record: Dict[str, Any], flow_state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    flow_state = flow_state or {}
    signals = record.get("signals") or flow_state.get("signals") or {}
    items = record.get("items") or flow_state.get("items") or []
    selected = record.get("selected_item_info") or flow_state.get("selected_item_info") or {}
    history = record.get("dialogue_history") or flow_state.get("dialogue_history") or ""
    errors = []
    warnings = []

    selected_name = _selected_item_name(selected)
    selected_state = _selected_state(selected_name, items, flow_state, warnings)
    image_value = _first(selected.get("是否已收集图片凭证"), signals.get("是否已收集图片凭证"))
    has_image = _yes_no_loose(image_value)
    if has_image is None and flow_state.get("image_state") == "has_image":
        has_image = True
    if has_image is None and ("【图片】" in history or "系统识别图片" in history or "图片识别" in history):
        has_image = True

    refund_reason = None if selected_state != "selected" else _has_value(_first(selected.get("是否已收集退款原因"), signals.get("是否已收集退款原因")))
    refund_ratio = selected.get("建议退款比例")
    has_ratio = None if selected_state != "selected" else _has_value(refund_ratio)
    refund_qty = selected.get("实际退款数量") or selected.get("退款数量")
    has_qty = None if selected_state != "selected" else _has_value(refund_qty)
    refund_status = _first(signals.get("订单退款状态"), signals.get("退款状态"), flow_state.get("refund_state"))
    selected_refund_status = _selected_item_refund_status(selected_name, selected, items, warnings)
    timeout_text = _first(signals.get("履约中订单超时时长"), signals.get("已完成订单超时时长"))

    over_after_sales = _yes_no_loose(_first(signals.get("订单是否超售后"), flow_state.get("order_over_after_sales")))
    if over_after_sales is None and "超售后" in str(signals.get("订单是否超售后", "")):
        over_after_sales = True
    if over_after_sales is None and "超售后" in _first(flow_state.get("can_refund_state")) and selected_state == "selected":
        warnings.append("ambiguous_after_sales_status")

    normalized = {
        "order_status": _first(signals.get("订单状态"), flow_state.get("order_status")),
        "is_delivery_order": _yes_no_loose(_first(signals.get("是否为配送单"), flow_state.get("is_delivery_order"))),
        "is_pickup_order": _yes_no_loose(_first(signals.get("是否为自提单"), flow_state.get("is_pickup_order"))),
        "rider_status": _first(signals.get("订单骑手状态"), flow_state.get("rider_status")),
        "store_status": _first(signals.get("订单门店状态"), flow_state.get("store_status")),
        "estimated_arrival_time": _first(signals.get("预计送达时间")),
        "latest_promised_arrival_time": _first(signals.get("承诺最晚送达时间")),
        "order_timeout": _yes_no_loose(signals.get("订单是否超时") or flow_state.get("timeout_state")),
        "timeout_minutes": _minutes(timeout_text),
        "has_timeout_risk": _yes_no_loose(_first(signals.get("履约中未超时订单是否有超时风险"), flow_state.get("has_timeout_risk"))),
        "can_cancel": _yes_no_loose(_first(signals.get("是否可取消订单"), signals.get("能否取消订单"), flow_state.get("can_cancel"))),
        "can_compensate": _yes_no_loose(_first(signals.get("订单是否可赔付"), signals.get("是否可赔付"), flow_state.get("can_compensate"))),
        "already_compensated": _yes_no_loose(_first(signals.get("是否赔付过"), flow_state.get("already_compensated"))),
        "compensation_amount_range": _compensation_range(signals, flow_state),
        "has_rider_phone": _yes_no_loose(_first(signals.get("是否有骑手真实手机号"), flow_state.get("has_rider_phone"))),
        "has_delivery_photo": _yes_no_loose(_first(signals.get("骑手是否有送达图片"), flow_state.get("has_delivery_photo"))),
        "refund_status": refund_status,
        "has_refund_record": _yes_no_loose(str(_first(signals.get("订单是否有退款记录"), flow_state.get("has_refund_record"))).split()[0] if _first(signals.get("订单是否有退款记录"), flow_state.get("has_refund_record")) else ""),
        "order_over_after_sales": over_after_sales,
        "selected_item_name": selected_name,
        "selected_item_state": selected_state,
        "has_image_evidence": has_image,
        "has_refund_reason": refund_reason,
        "has_refund_ratio": has_ratio,
        "has_refund_quantity": has_qty,
        "selected_item_refund_status": selected_refund_status,
        "selected_item_can_refund": _can_refund(selected_refund_status) if selected_state == "selected" else None,
        "refund_apply_result": _first(selected.get("退款申请结果"), signals.get("退款申请结果")),
        "normalization_errors": errors,
        "normalization_warnings": warnings,
    }
    return normalized


if __name__ == "__main__":
    import json

    print(json.dumps(normalize_signals(json.loads(sys.stdin.read())), ensure_ascii=False, indent=2))
