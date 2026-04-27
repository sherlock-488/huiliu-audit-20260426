#!/usr/bin/env python3
"""Shared helpers for flow skill mining v1."""

from __future__ import annotations

import collections
import gzip
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
V0_OUT = ROOT / "flow_skill_mining" / "outputs"
V1_ROOT = ROOT / "flow_skill_mining_v1"
V1_OUT = V1_ROOT / "outputs"
V1_REPORTS = V1_OUT / "reports"


def ensure_dirs() -> None:
    for path in [
        V1_ROOT,
        V1_ROOT / "checkers",
        V1_ROOT / "replay",
        V1_ROOT / "skills",
        V1_OUT,
        V1_REPORTS,
        V1_OUT / "run_logs",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return list(read_jsonl(path))


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


ALIASES = {
    "引导自助查看会员权益": ("引导自助查看-会员权益", "missing_dash_alias"),
    "引导自助查看配送范围": ("引导自助查看-配送范围", "missing_dash_alias"),
    "引导自助查看小象开通城市": ("引导自助查看-小象开通城市", "missing_dash_alias"),
    "引导自助查看优惠券": ("引导自助查看-优惠券", "missing_dash_alias"),
}


def _normalize_text(name: Any) -> str:
    s = "" if name is None else str(name).strip()
    return re.sub(r"\s+", "", s.replace("％", "%").replace("；", ";").replace("：", ":"))


def canonicalize_solution(name: Any) -> Tuple[str, str, List[str]]:
    """Return canonical_name, pattern_type, notes."""
    notes: List[str] = []
    raw = _normalize_text(name)
    if not raw:
        return "", "other", notes
    if raw == "无":
        return "无", "none", notes
    if raw in ALIASES:
        canonical, note = ALIASES[raw]
        notes.append(note)
        return canonical, "self_service_view", notes
    if "红包" in raw:
        raw = raw.replace("红包", "优惠券")
        notes.append("historical_red_packet_mapped_to_coupon")
    if re.fullmatch(r"小象-?单商品退款-\d+%", raw):
        return "小象单商品退款-xx%", "refund_percent", notes
    if re.fullmatch(r"操作赔付-优惠券-\d+元", raw):
        return "操作赔付-优惠券-xx元", "compensation_coupon", notes
    if re.fullmatch(r"操作赔付-运费券-\d+元", raw):
        return "操作赔付-运费券-3元", "compensation_shipping_coupon", notes
    if re.fullmatch(r"引导自助查看-.+", raw):
        return raw, "self_service_view", notes
    if re.fullmatch(r"再次外呼骑手-.+", raw):
        return "再次外呼骑手-xx", "call_rider", notes
    if re.fullmatch(r"外呼骑手-.+", raw):
        return "外呼骑手-xx", "call_rider", notes
    if re.fullmatch(r"再次外呼门店-.+", raw):
        return "再次外呼门店-xx", "call_store", notes
    if re.fullmatch(r"外呼门店-.+", raw):
        return "外呼门店-xx", "call_store", notes
    return raw, "exact", notes


def split_solution_raw(raw_value: Any) -> Tuple[List[str], List[str]]:
    raw = _normalize_text(raw_value)
    dirty_notes: List[str] = []
    if not raw or raw == "无":
        return [], dirty_notes
    pieces = re.split(r"[;；]", raw)
    out: List[str] = []
    for piece in pieces:
        if ":" in piece:
            left, right = piece.split(":", 1)
            if left and right and ("-" in left or "赔付" in left or "退款" in left):
                dirty_notes.append(f"colon_composite:{piece}")
                out.extend([left, right])
                continue
        out.append(piece)
    return [x for x in out if x and x != "无"], dirty_notes


def canonical_components(raw_value: Any) -> Tuple[List[str], List[str]]:
    comps, notes = split_solution_raw(raw_value)
    canonical = []
    for comp in comps:
        name, _, cnotes = canonicalize_solution(comp)
        if name and name != "无":
            canonical.append(name)
        notes.extend(cnotes)
    return canonical, notes


STRONG_CONFIRMATION = {
    "取消订单",
    "小象单商品退款-xx%",
    "小象整单申请退款",
    "会员卡退款",
    "操作赔付-优惠券-xx元",
    "操作赔付-运费券-3元",
}

USER_REQUEST_ENOUGH = {
    "外呼骑手-xx",
    "再次外呼骑手-xx",
    "外呼门店-xx",
    "再次外呼门店-xx",
    "催促退款审核",
    "加急催促退款审核",
}

NO_CONFIRMATION = {
    "系统催单",
    "加急调度",
    "智能跟单",
    "退审跟单",
    "无骑手接单跟单",
    "选择商品",
    "发送送达图片",
    "开发票",
    "管理会员自动续费",
    "引导自助修改订单",
    "引导自助联系骑手",
    "引导自助管理地址",
    "引导自助开通会员",
    "引导自助查看-xx",
}


def confirmation_level(canonical_name: str) -> str:
    if canonical_name in STRONG_CONFIRMATION:
        return "strong_confirmation_required"
    if canonical_name in USER_REQUEST_ENOUGH:
        return "user_request_is_enough"
    if canonical_name in NO_CONFIRMATION or canonical_name.startswith("引导自助查看-"):
        return "no_confirmation_required"
    return "unclear"


def same_canonical(a: Any, b: Any) -> bool:
    ac, _, _ = canonicalize_solution(a)
    bc, _, _ = canonicalize_solution(b)
    return bool(ac and bc and ac == bc)


CONFIRM_RE = re.compile(
    r"可以|同意|行|好|确认|退吧|赔吧|取消吧|就这样|接受|嗯|可以的|行吧|那就|帮我弄|帮我处理|给我退|给我赔|退这个|赔这个|要得|好的|对"
)


def has_confirm_expression(text: str) -> bool:
    return bool(CONFIRM_RE.search(text or ""))


def user_request_matches_action(text: str, canonical_name: str) -> bool:
    text = text or ""
    if canonical_name in {"外呼骑手-xx", "再次外呼骑手-xx"}:
        return bool(re.search(r"联系骑手|打.*骑手|问.*骑手|催.*骑手|找骑手|骑手电话", text))
    if canonical_name in {"外呼门店-xx", "再次外呼门店-xx"}:
        return bool(re.search(r"联系门店|问.*门店|打.*门店|找门店", text))
    if canonical_name in {"催促退款审核", "加急催促退款审核"}:
        return bool(re.search(r"催.*退款|退款.*催|退款.*审核|什么时候退款|退款进度|到账", text))
    return False


def yes_no_bool(value: Any) -> Optional[bool]:
    s = "" if value is None else str(value).strip()
    if s in {"是", "有", "可以", "可", "true", "True", "1"}:
        return True
    if s in {"否", "无", "不可", "不可以", "false", "False", "0"}:
        return False
    return None


def top_counter(counter: collections.Counter, limit: int = 30) -> str:
    return "\n".join(f"- `{k}`: `{v}`" for k, v in counter.most_common(limit))


def pct(num: int, den: int) -> str:
    return f"{num / den:.2%}" if den else "0.00%"


def get_v0_case_records_path() -> Path:
    plain = V0_OUT / "case_records.jsonl"
    if plain.exists():
        return plain
    gz = V0_OUT / "release_assets" / "case_records.jsonl.gz"
    return gz


def get_v0_flow_states_path() -> Path:
    plain = V0_OUT / "flow_states.jsonl"
    if plain.exists():
        return plain
    return V0_OUT / "release_assets" / "flow_states.jsonl.gz"


def get_v0_session_trajectories_path() -> Path:
    plain = V0_OUT / "session_trajectories.jsonl"
    if plain.exists():
        return plain
    return V0_OUT / "release_assets" / "session_trajectories.jsonl.gz"

