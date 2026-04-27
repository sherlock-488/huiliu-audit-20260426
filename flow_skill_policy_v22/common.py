#!/usr/bin/env python3
"""Shared helpers for policy v22."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
V0_OUT = ROOT / "flow_skill_mining" / "outputs"
V1_OUT = ROOT / "flow_skill_mining_v1" / "outputs"
V2_ROOT = ROOT / "flow_skill_policy_v2"
V2_OUT = V2_ROOT / "outputs"
V2_REPORTS = V2_OUT / "reports"
V21_ROOT = ROOT / "flow_skill_policy_v21"
V21_OUT = V21_ROOT / "outputs"
V21_REPORTS = V21_OUT / "reports"
V22_ROOT = ROOT / "flow_skill_policy_v22"
V22_OUT = V22_ROOT / "outputs"
V22_REPORTS = V22_OUT / "reports"


def ensure_dirs() -> None:
    for path in [
        V22_ROOT,
        V22_ROOT / "policies",
        V22_ROOT / "replay",
        V22_ROOT / "skills",
        V22_OUT,
        V22_REPORTS,
        V22_OUT / "trainer_review_pack",
        V22_OUT / "run_logs",
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


def get_case_records_path() -> Path:
    plain = V0_OUT / "case_records.jsonl"
    return plain if plain.exists() else V0_OUT / "release_assets" / "case_records.jsonl.gz"


def get_flow_states_path() -> Path:
    plain = V0_OUT / "flow_states.jsonl"
    return plain if plain.exists() else V0_OUT / "release_assets" / "flow_states.jsonl.gz"


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()


def yes_no(value: Any) -> Optional[bool]:
    if value is None:
        return None
    s = str(value).strip()
    if s in {"是", "有", "可", "可以", "true", "True", "1"}:
        return True
    if s in {"否", "无", "不可", "不可以", "false", "False", "0"}:
        return False
    return None


ALIASES = {
    "引导自助查看会员权益": "引导自助查看-会员权益",
    "引导自助查看配送范围": "引导自助查看-配送范围",
    "引导自助查看小象开通城市": "引导自助查看-小象开通城市",
    "引导自助查看优惠券": "引导自助查看-优惠券",
}


def normalize_text(value: Any) -> str:
    s = "" if value is None else str(value).strip()
    return re.sub(r"\s+", "", s.replace("％", "%").replace("；", ";").replace("：", ":"))


def canonicalize_solution(name: Any) -> Tuple[str, str, List[str]]:
    raw = normalize_text(name)
    notes: List[str] = []
    if not raw:
        return "", "other", notes
    if raw == "无":
        return "无", "none", notes
    if raw in ALIASES:
        notes.append("alias")
        return ALIASES[raw], "self_service_view", notes
    if "红包" in raw:
        raw = raw.replace("红包", "优惠券")
        notes.append("historical_red_packet")
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


def split_solution_raw(raw_value: Any) -> List[str]:
    raw = normalize_text(raw_value)
    if not raw or raw == "无":
        return []
    out: List[str] = []
    for piece in re.split(r"[;；]", raw):
        if ":" in piece:
            left, right = piece.split(":", 1)
            if left and right and ("-" in left or "赔付" in left or "退款" in left):
                out.extend([left, right])
                continue
        out.append(piece)
    return [x for x in out if x and x != "无"]


def canonical_components(raw_value: Any) -> List[str]:
    comps = []
    for piece in split_solution_raw(raw_value):
        canonical, _, _ = canonicalize_solution(piece)
        if canonical and canonical != "无":
            comps.append(canonical)
    return comps


def explicit_confirm(text: str) -> bool:
    return bool(
        re.search(
            r"可以|同意|行|好|确认|退吧|赔吧|取消吧|就这样|接受|嗯|可以的|行吧|那就|帮我弄|帮我处理|给我退|给我赔|退这个|赔这个|要得|好的|对",
            text or "",
        )
    )


def contains_any(text: str, *words: str) -> bool:
    return any(word in (text or "") for word in words)


def extract_amount(solution: str) -> Optional[int]:
    match = re.search(r"(\d+)元", solution or "")
    return int(match.group(1)) if match else None


def parse_amount_range(text: str) -> Tuple[Optional[int], Optional[int]]:
    nums = [int(x) for x in re.findall(r"\d+", text or "")]
    if not nums:
        return None, None
    return min(nums), max(nums)


def mask_text(text: Any) -> str:
    s = "" if text is None else str(text)
    s = re.sub(r"1[3-9]\d{9}", lambda m: m.group(0)[:3] + "****" + m.group(0)[-4:], s)
    s = re.sub(r"(地址|收货地址|详细地址)[:：]?\s*[^,，。\n\t ]+", r"\1:<MASKED_ADDRESS>", s)
    s = re.sub(r"(姓名|联系人|收货人)[:：]?\s*[^,，。\n\t ]+", r"\1:<MASKED_NAME>", s)
    return s


def top_counter(counter, limit: int = 30) -> str:
    return "\n".join(f"- `{k}`: `{v}`" for k, v in counter.most_common(limit))


def relation(gold: str, oracle: str) -> str:
    if gold == oracle:
        return "same"
    gold_c = canonical_components(gold)
    oracle_c = canonical_components(oracle)
    if gold_c and oracle_c and gold_c == oracle_c:
        return "canonical_same"
    if gold == "无" and oracle != "无":
        return "oracle_no_gold_action"
    if gold != "无" and oracle == "无":
        return "gold_no_oracle_action"
    return "different"
