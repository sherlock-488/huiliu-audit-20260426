#!/usr/bin/env python3
"""Classify only the current last user query, never dialogue history."""

from __future__ import annotations

import re
from typing import Any, Dict, List


CLOSE_PATTERNS = [
    "没有了",
    "没了",
    "不用了",
    "没事了",
    "谢谢",
    "感谢",
    "好的谢谢",
    "就这样吧",
    "没有其他问题",
    "不需要了",
]
ACK_ONLY = {"嗯", "嗯嗯", "好", "好的", "行", "OK", "ok", "知道了", "好吧", "可以"}
TRANSFER_ONLY = {"人工", "转人工", "人工客服", "客服"}

INTENT_PATTERNS = {
    "eta_question": ["什么时候送到", "几点到", "多久到", "到哪了", "预计", "啥时候到", "什么时候到"],
    "delivery_urge": ["催", "快点", "太慢", "配送慢", "还没送", "怎么还没到", "赶紧", "超时"],
    "no_rider": ["没有骑手", "没人接单", "无骑手", "还没骑手", "没骑手"],
    "contact_rider": ["联系骑手", "骑手电话", "问骑手", "打给骑手", "帮我问骑手", "帮我联系骑手"],
    "cancel_request": ["取消", "不要了", "退单", "不想要"],
    "compensation_request": ["赔", "补偿", "优惠券", "券", "投诉", "太差", "不满意", "不能接受"],
    "refund_progress": ["退款进度", "多久到账", "什么时候退", "还没退", "退款状态", "审核"],
    "refund_request": ["退款", "退钱", "全退", "退这个", "申请退款"],
    "quality_issue": ["坏了", "破了", "漏了", "发霉", "变质", "生虫", "异物", "质量问题", "不新鲜", "软了", "烂了", "碎了"],
    "select_product": ["选好了", "这个", "这个商品", "就这个"],
    "upload_image": ["【图片】", "系统识别图片", "图片识别"],
}

CONFIRM_WORDS = [
    "确认取消",
    "取消吧",
    "退吧",
    "给我退",
    "赔吧",
    "给我赔",
    "可以",
    "同意",
    "行",
    "好的",
    "好",
    "嗯",
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").strip())


def _contains(text: str, words: List[str]) -> bool:
    return any(word in text for word in words)


def classify_current_turn(last_user_query: str) -> Dict[str, Any]:
    raw = last_user_query or ""
    text = _norm(raw)
    intents: List[str] = []
    debug: List[str] = []

    is_close = _contains(text, CLOSE_PATTERNS)
    if is_close:
        debug.append("close_or_thanks")

    is_ack_only = text in ACK_ONLY or text.lower() in ACK_ONLY
    if is_ack_only:
        debug.append("ack_only")

    is_transfer_only = text in TRANSFER_ONLY
    if is_transfer_only:
        debug.append("transfer_only")

    for intent, patterns in INTENT_PATTERNS.items():
        if _contains(text, patterns):
            intents.append(intent)
            debug.append(f"intent:{intent}")

    # "可以/好的/嗯" alone is weak confirmation only. Strong execution requires
    # a pending strong-confirmation solution in confirmation_resolver.
    is_confirm_like = _contains(text, CONFIRM_WORDS)
    if is_confirm_like:
        debug.append("confirm_like")
        if _contains(text, ["取消", "不要了"]):
            intents.append("confirm_cancel")
        if _contains(text, ["退", "退款"]):
            intents.append("confirm_refund")
        if _contains(text, ["赔", "补偿", "优惠券"]):
            intents.append("confirm_compensation")

    # Remove generic select_product if a close/ack-only message happens to contain "这个"
    # in an unrelated short acknowledgement; this keeps it conservative.
    intents = list(dict.fromkeys(intents))
    if is_close or is_ack_only or is_transfer_only:
        action_intents = [x for x in intents if x not in {"select_product"}]
        has_new_action = bool(action_intents) and not (is_ack_only and set(action_intents).issubset({"confirm_cancel", "confirm_refund", "confirm_compensation"}))
    else:
        has_new_action = bool(intents)

    return {
        "raw": raw,
        "current_intents": intents,
        "is_close_or_thanks": is_close,
        "is_ack_only": is_ack_only,
        "is_transfer_only": is_transfer_only,
        "is_confirm_like": is_confirm_like,
        "has_new_action_intent": has_new_action,
        "debug_reason": debug,
    }


if __name__ == "__main__":
    import json
    import sys

    print(json.dumps(classify_current_turn(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))
