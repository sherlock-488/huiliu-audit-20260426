#!/usr/bin/env python3
"""Shared helpers for flow skill mining scripts."""

from __future__ import annotations

import collections
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl"
OUT_DIR = ROOT / "flow_skill_mining" / "outputs"
REPORT_DIR = OUT_DIR / "reports"

NO_SOLUTION = "无"


def ensure_dirs() -> None:
    for path in [
        ROOT / "flow_skill_mining",
        ROOT / "flow_skill_mining" / "parsers",
        ROOT / "flow_skill_mining" / "miners",
        ROOT / "flow_skill_mining" / "checkers",
        ROOT / "flow_skill_mining" / "skills",
        OUT_DIR,
        REPORT_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def load_jsonl_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return list(read_jsonl(path))


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def split_components(raw_value: Any) -> List[str]:
    if raw_value is None:
        return []
    raw = str(raw_value).strip()
    if not raw or raw == NO_SOLUTION:
        return []
    parts = re.split(r"[;；]", raw)
    return [p.strip() for p in parts if p.strip() and p.strip() != NO_SOLUTION]


def normalize_solution_name(name: Any) -> Tuple[str, str]:
    """Return (normalized_name, pattern_type)."""
    if name is None:
        return "", "other"
    s = str(name).strip()
    s = s.replace("％", "%")
    s = re.sub(r"\s+", "", s)
    if not s:
        return "", "other"
    if s == NO_SOLUTION:
        return NO_SOLUTION, "exact"
    if re.fullmatch(r"小象-?单商品退款-\d+%", s):
        return "小象单商品退款-xx%", "refund_percent"
    if re.fullmatch(r"操作赔付-优惠券-\d+元", s):
        return "操作赔付-优惠券-xx元", "compensation_coupon"
    if re.fullmatch(r"操作赔付-运费券-\d+元", s):
        return "操作赔付-运费券-3元", "compensation_shipping_coupon"
    if re.fullmatch(r"引导自助查看-.+", s):
        return "引导自助查看-xx", "self_service_view"
    if re.fullmatch(r"再次外呼骑手-.+", s):
        return "再次外呼骑手-xx", "call_rider"
    if re.fullmatch(r"外呼骑手-.+", s):
        return "外呼骑手-xx", "call_rider"
    if re.fullmatch(r"再次外呼门店-.+", s):
        return "再次外呼门店-xx", "call_store"
    if re.fullmatch(r"外呼门店-.+", s):
        return "外呼门店-xx", "call_store"
    return s, "exact"


CONFIRM_REQUIRED_INITIAL = {
    "取消订单",
    "小象单商品退款-xx%",
    "小象整单申请退款",
    "会员卡退款",
    "操作赔付-优惠券-xx元",
    "操作赔付-运费券-3元",
}

CONFIRM_NOT_REQUIRED_INITIAL = {
    "系统催单",
    "加急调度",
    "智能跟单",
    "退审跟单",
    "催促退款审核",
    "加急催促退款审核",
    "选择商品",
    "发送送达图片",
    "开发票",
    "管理会员自动续费",
    "引导自助查看-xx",
    "引导自助修改订单",
    "引导自助联系骑手",
    "引导自助管理地址",
    "引导自助开通会员",
    "外呼骑手-xx",
    "再次外呼骑手-xx",
    "外呼门店-xx",
    "再次外呼门店-xx",
}


def initial_requires_agreement(solution_name: Any) -> Optional[bool]:
    norm, _ = normalize_solution_name(solution_name)
    if norm in CONFIRM_REQUIRED_INITIAL:
        return True
    if norm in CONFIRM_NOT_REQUIRED_INITIAL:
        return False
    return None


def same_solution_or_type(a: Any, b: Any) -> bool:
    an, at = normalize_solution_name(a)
    bn, bt = normalize_solution_name(b)
    if not an or not bn:
        return False
    if an == bn:
        return True
    type_matchable = {
        "refund_percent",
        "compensation_coupon",
        "compensation_shipping_coupon",
        "self_service_view",
        "call_rider",
        "call_store",
    }
    return at == bt and at in type_matchable


def yes_no_to_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    s = str(value).strip()
    if s in {"是", "有", "可", "可以", "true", "True", "1"}:
        return True
    if s in {"否", "无", "不可", "不可以", "false", "False", "0"}:
        return False
    return None


def top_counter(counter: collections.Counter, limit: int = 30) -> List[Dict[str, Any]]:
    return [{"value": k, "count": v} for k, v in counter.most_common(limit)]


def pct(num: int, den: int) -> str:
    return f"{(num / den * 100):.2f}%" if den else "0.00%"


def parse_target_json(target_raw: Any) -> Tuple[Dict[str, Any], str]:
    if target_raw is None:
        return {}, "missing target"
    s = str(target_raw).strip()
    if s.startswith("```json"):
        s = s[7:].strip()
    elif s.startswith("```"):
        s = s[3:].strip()
    if s.endswith("```"):
        s = s[:-3].strip()
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj, ""
        return {}, f"target json is {type(obj).__name__}, not dict"
    except Exception as exc:
        return {}, str(exc)


def scene_parts(scene_raw: Any) -> Tuple[str, str, str, str]:
    if scene_raw in (None, ""):
        scene_raw_s = ""
        scene = "<MISSING>"
    else:
        scene_raw_s = str(scene_raw)
        scene = scene_raw_s.strip() or "<MISSING>"
    if "-" in scene and scene != "<MISSING>":
        l1, l2 = scene.split("-", 1)
    else:
        l1, l2 = scene, ""
    return scene_raw_s, scene, l1, l2


def has_confirm_expression(text: str) -> bool:
    if not text:
        return False
    return bool(
        re.search(
            r"可以|同意|行|好|确认|退吧|赔吧|取消吧|就这样|接受|要得|嗯嗯|是的|对的|没问题|可以的|好的",
            text,
        )
    )


def safe_div(num: int, den: int) -> float:
    return num / den if den else 0.0


def compact_counter(counter: collections.Counter, limit: int = 20) -> str:
    return "\n".join(f"- `{k}`: `{v}`" for k, v in counter.most_common(limit))

