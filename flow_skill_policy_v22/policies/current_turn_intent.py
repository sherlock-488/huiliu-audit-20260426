#!/usr/bin/env python3
"""Classify current last_user_query for policy v22."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_policy_v22.common import V21_ROOT, V22_REPORTS, ensure_dirs, read_jsonl


CLOSE_PATTERNS = ["没有了", "没了", "不用了", "没事了", "谢谢", "感谢", "好的谢谢", "没有其他问题", "不需要了"]
ACK_ONLY = {"嗯", "嗯嗯", "好", "好的", "行", "OK", "ok", "知道了", "好吧", "可以"}
TRANSFER_ONLY = {"人工", "转人工", "人工客服", "客服"}

QUESTION_OR_REJECT = [
    "？", "?", "什么时候", "多久", "到账", "还没", "怎么", "为什么", "能不能", "太少", "少吗", "不行", "不接受", "不能接受", "再", "多退", "投诉",
]
PURE_CONFIRM_PATTERNS = ["可以", "同意", "行", "好的", "确认", "确认取消", "退吧", "给我退", "赔吧", "给我赔", "取消吧", "就这样", "接受", "行吧", "可以吧"]
MAYBE_ACCEPT_PATTERNS = ["就这样吧", "行吧", "可以吧", "算了那就这样吧", "那就这样吧"]

INTENT_PATTERNS = {
    "eta_question": [
        "什么时候送到", "几点到", "多久到", "到哪了", "预计", "啥时候到", "什么时候到", "啥时候送", "何时送", "什么时间到",
        "还得等多久", "还得等到啥时候", "还要多久", "5分钟", "几分钟", "多少分钟", "到哪儿了", "配送到哪了", "怎么还没配送",
        "怎么还没送", "还没配送", "还没送到",
    ],
    "delivery_urge": [
        "催", "快点", "快一点", "快点啊", "太慢", "配送慢", "还没送", "怎么还没到", "赶紧", "超时", "急", "很急", "加急",
        "要求加急", "没有加急", "帮我加急", "催一下", "给我催催", "赶紧送", "赶紧的", "太久", "等太久", "超时了", "都超时",
        "着急用", "别忘了赶紧送",
    ],
    "no_rider": ["没有骑手", "没人接单", "无骑手", "还没骑手", "没骑手", "还没人接", "一直没人接", "没人配送", "没骑手配送", "骑手没接", "还没分配骑手"],
    "contact_rider": [
        "联系骑手", "骑手电话", "问骑手", "打给骑手", "帮我问骑手", "帮我联系骑手", "问一下骑手", "问问骑手", "帮我问下",
        "帮我联系下", "联系一下配送员", "骑手呢", "骑手在哪", "问骑手了吗", "打电话给骑手", "怎么联系骑手",
    ],
    "cancel_request": ["取消", "不要了", "退单", "不想要"],
    "compensation_request": [
        "赔", "补偿", "优惠券", "券", "太差", "不满意", "不能接受", "就给这么少", "太少了", "不接受", "这不合理", "怎么补偿", "怎么赔", "给个说法", "心意", "赔我",
    ],
    "rider_complaint": ["投诉骑手", "骑手态度", "投诉配送员"],
    "refund_progress": ["退款进度", "多久到账", "什么时候退", "还没退", "退款状态", "审核", "退款呢", "还没到账", "到账了吗", "什么时候到账", "退完了吗", "什么时候退完", "审核要多久", "要这么久吗"],
    "refund_request": ["退款", "退钱", "全退", "退这个", "申请退款", "要退", "我要退", "退了吧", "退一下", "退一部分", "至少退", "退50", "退一半", "给我退", "申请退"],
    "quality_issue": [
        "坏了", "破了", "漏了", "发霉", "变质", "生虫", "异物", "质量问题", "不新鲜", "软了", "烂了", "碎了", "漏的", "漏液",
        "漏出来", "空心", "碎的", "坏的", "坏得", "干瘪", "臭", "发臭", "不能吃", "没法吃", "烂掉", "压坏", "不甜", "酸",
        "变味", "有泥", "泥太多", "有虫", "死了", "无活力", "临期", "过期", "包装破", "袋子破", "发黑", "发软", "软烂", "质量差",
    ],
    "select_product": ["选好了", "这个", "这个商品", "就这个"],
    "upload_image": ["【图片】", "系统识别图片结果", "系统识别图片", "图片中显示", "图中显示", "图片识别"],
}


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").strip())


def _contains(text: str, words: List[str]) -> bool:
    return any(w in text for w in words)


def classify_current_turn(last_user_query: str) -> Dict[str, Any]:
    raw = last_user_query or ""
    text = _norm(raw)
    lower = text.lower()
    debug: List[str] = []
    intents: List[str] = []

    maybe_accept = _contains(text, MAYBE_ACCEPT_PATTERNS)
    is_close = _contains(text, CLOSE_PATTERNS)
    if "算了" in text and maybe_accept:
        is_close = False
        debug.append("maybe_accept_not_close")
    elif is_close:
        debug.append("close_or_thanks")

    has_question_or_reject = _contains(text, QUESTION_OR_REJECT)
    is_ack_only = text in ACK_ONLY or lower in ACK_ONLY
    if is_ack_only:
        debug.append("ack_only")
    is_transfer_only = text in TRANSFER_ONLY
    if is_transfer_only:
        debug.append("transfer_only")

    for intent, patterns in INTENT_PATTERNS.items():
        if _contains(text, patterns):
            intents.append(intent)
            debug.append(f"intent:{intent}")

    # "投诉骑手" is a complaint intent. It should not become compensation_request
    # unless the user separately asks for compensation/coupon/refund.
    if "rider_complaint" in intents and not _contains(text, ["赔", "补偿", "优惠券", "券", "怎么赔", "赔我"]):
        intents = [x for x in intents if x != "compensation_request"]
        debug.append("rider_complaint_not_compensation")

    is_confirm_like = _contains(text, PURE_CONFIRM_PATTERNS) or is_ack_only
    if is_confirm_like:
        debug.append("confirm_like")
    is_pure_confirm = False
    if is_confirm_like and not has_question_or_reject and not is_close:
        stripped = re.sub(r"(吧|啊|呀|哦|呢|哈|啦|，|,|。|！|!)", "", text)
        confirm_core = any(stripped == p.replace("吧", "") or stripped == p for p in PURE_CONFIRM_PATTERNS + list(ACK_ONLY))
        explicit_action_confirm = _contains(text, ["退吧", "给我退", "赔吧", "给我赔", "取消吧", "确认取消"])
        if confirm_core or explicit_action_confirm or maybe_accept:
            is_pure_confirm = True
            debug.append("pure_confirm")

    if is_confirm_like and has_question_or_reject:
        debug.append("confirm_blocked_by_question_or_reject")

    if _contains(text, ["取消吧", "确认取消"]):
        intents.append("confirm_cancel")
    if _contains(text, ["退吧", "给我退", "可以退", "同意退"]):
        intents.append("confirm_refund")
    if _contains(text, ["赔吧", "给我赔", "可以赔", "同意赔"]):
        intents.append("confirm_compensation")

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
        "is_pure_confirm": is_pure_confirm,
        "maybe_accept_pending": maybe_accept,
        "has_new_action_intent": has_new_action,
        "debug_reason": debug,
    }


def _dry_run_rows() -> List[Dict[str, Any]]:
    phrases = [
        "怎么还没配送", "急", "还得等到啥时候啊", "我要求加急并没有加急啊，我很着急啊", "5分钟？", "好，快点",
        "洗衣液今天打开看都是漏的", "芹菜空心的", "这个蛋送来打开后是碎的", "坏得有一半了", "都不能吃了就给这么少吗", "臭的", "干瘪",
        "嗯，什么时候退完给我啊", "行吧，那就这样吧", "好谢谢", "可以，那退吧",
    ]
    return [{"phrase": p, "intent": classify_current_turn(p)} for p in phrases]


def build_report() -> None:
    ensure_dirs()
    lines = ["# Current Turn Intent v22 Report", "", "## Dry Run"]
    for row in _dry_run_rows():
        lines.append(f"- `{row['phrase']}` -> `{row['intent']['current_intents']}` pure_confirm=`{row['intent']['is_pure_confirm']}` maybe_accept=`{row['intent']['maybe_accept_pending']}` debug=`{row['intent']['debug_reason']}`")
    # Compare v21/v22 on remaining v21 challenge samples.
    v21_paths = [V21_ROOT / "replay" / "fulfillment_delivery_challenge_replay.jsonl", V21_ROOT / "replay" / "receipt_quality_challenge_replay.jsonl"]
    changed = Counter()
    examples = []
    for path in v21_paths:
        if not path.exists():
            continue
        for row in read_jsonl(path):
            q = row.get("last_user_query", "")
            v22 = classify_current_turn(q)
            old = row.get("current_turn_intent") or {}
            if set(v22["current_intents"]) != set(old.get("current_intents") or []):
                changed[path.stem] += 1
                if len(examples) < 40:
                    examples.append((q, old.get("current_intents"), v22["current_intents"], v22["debug_reason"]))
    lines.extend(["", "## v21/v22 Intent Changed On v21 Challenge", *[f"- `{k}`: `{v}`" for k, v in changed.items()], "", "## Examples"])
    for q, old, new, reason in examples:
        lines.append(f"- `{q}`: `{old}` -> `{new}` debug=`{reason}`")
    (V22_REPORTS / "current_turn_intent_v22_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        build_report()
    else:
        print(json.dumps(classify_current_turn(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))
