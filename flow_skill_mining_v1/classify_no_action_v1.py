#!/usr/bin/env python3
"""Calibrate no_action_reason v1."""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_mining_v1.common_v1 import V0_OUT, V1_OUT, V1_REPORTS, ensure_dirs, get_v0_flow_states_path, load_jsonl, read_jsonl, top_counter, write_jsonl


OUTPUT = V1_OUT / "no_action_labeled_v1.jsonl"
REPORT = V1_REPORTS / "no_action_v1_report.md"


REFUND_WORDS = re.compile(r"退款|退钱|到账|退回|退款进度|审核|驳回|银行退款")
CLOSE_WORDS = re.compile(r"没有了|不用了|谢谢|没事|再见|好的|好")


def _has_available(state: Dict[str, Any], *names: str) -> bool:
    available = " ".join(state.get("available_solution_names", []))
    return any(name in available for name in names)


def _refund_stateful(state: Dict[str, Any]) -> bool:
    scene = state.get("scene", "")
    intent = state.get("user_intent", "")
    signals = state.get("signals", {}) or {}
    selected = state.get("selected_item_info", {}) or {}
    text = " ".join(
        [
            scene,
            intent,
            state.get("refund_state", ""),
            state.get("can_refund_state", ""),
            str(signals.get("订单退款状态", "")),
            str(signals.get("订单是否有退款记录", "")),
            str(selected.get("商品退款状态", "")),
            state.get("last_user_query", ""),
        ]
    )
    return bool(
        "退款" in scene
        or "催退款" in scene
        or intent in {"refund_progress", "cannot_refund", "refund_request"}
        or REFUND_WORDS.search(text)
    )


def _selected(state: Dict[str, Any]) -> bool:
    info = state.get("selected_item_info", {}) or {}
    if any(v for k, v in info.items() if "商品" in k and str(v).strip() not in {"", "无", "不涉及"}):
        return True
    if state.get("selected_sku_state") == "selected":
        return True
    return False


def classify_v1(state: Dict[str, Any], v0_reason: str) -> str:
    if state.get("response_solution_components"):
        return ""
    scene = state.get("scene", "")
    intent = state.get("user_intent", "")
    q = state.get("last_user_query", "") or ""
    response = state.get("response", "") or ""

    if CLOSE_WORDS.search(q) and len(q) <= 20:
        return "close_conversation"
    if scene == "履约场景-配送问题":
        if intent == "eta_question" and not any(w in q for w in ["催", "快", "超时", "投诉"]):
            return "eta_answer_only"
        if intent in {"delivery_urge", "no_rider"} and _has_available(state, "系统催单", "加急调度", "智能跟单"):
            return "unknown"
        if "状态" in response or "预计" in response or "送达" in response:
            return "explain_status"
    if scene == "收货场景-品质问题":
        if not _selected(state):
            return "ask_select_product"
        if state.get("image_state") in {"missing_image", "unknown"}:
            return "ask_upload_image"
        info = state.get("selected_item_info", {}) or {}
        if info.get("是否已收集退款原因") == "否":
            return "ask_refund_reason"
        if info.get("建议退款比例") in {"", "无", None}:
            return "ask_refund_ratio"
        if _refund_stateful(state):
            return "explain_refund_status"
    if v0_reason == "explain_refund_status" and not _refund_stateful(state):
        if any(word in scene for word in ["发票", "会员", "活动", "金融"]):
            return "policy_explain" if "规则" in response or "无法" in response else "explain_status"
        return "explain_status" if response else "unknown"
    if _refund_stateful(state):
        return "explain_refund_status" if v0_reason in {"explain_refund_status", "explain_status", "unknown"} else v0_reason
    return v0_reason or "unknown"


def possible_missing_action(state: Dict[str, Any], reason: str) -> bool:
    if state.get("response_solution_components"):
        return False
    scene = state.get("scene", "")
    intent = state.get("user_intent", "")
    if scene == "履约场景-配送问题":
        if reason == "eta_answer_only" and (
            intent in {"delivery_urge", "no_rider"}
            or state.get("has_timeout_risk") is True
            or _has_available(state, "系统催单", "加急调度", "智能跟单")
        ):
            return True
        if reason == "unknown" and intent in {"delivery_urge", "no_rider", "contact_rider", "cancel_request"}:
            return True
    if scene == "收货场景-品质问题":
        if reason == "unknown" and _selected(state) and state.get("image_state") == "has_image":
            if "可退款" in state.get("can_refund_state", "") or _has_available(state, "小象单商品退款", "操作赔付"):
                return True
    if any(key in scene for key in ["少送", "错送"]) and _selected(state) and reason in {"unknown", "eta_answer_only"}:
        return True
    return False


def main() -> None:
    ensure_dirs()
    states = load_jsonl(get_v0_flow_states_path())
    v0_rows = {r.get("sample_id"): r for r in load_jsonl(V0_OUT / "no_action_labeled.jsonl")}
    rows = []
    v0_ctr = collections.Counter()
    v1_ctr = collections.Counter()
    scene_unknown = collections.defaultdict(lambda: [0, 0])
    missing_samples = []
    for state in states:
        v0 = v0_rows.get(state.get("sample_id"), {})
        v0_reason = v0.get("no_action_reason", "")
        if not state.get("response_solution_components"):
            v0_ctr[v0_reason] += 1
        v1_reason = classify_v1(state, v0_reason)
        possible = possible_missing_action(state, v1_reason)
        if v1_reason:
            v1_ctr[v1_reason] += 1
            scene_unknown[state.get("scene", "")][1] += 1
            if v1_reason == "unknown":
                scene_unknown[state.get("scene", "")][0] += 1
        row = {
            "sample_id": state.get("sample_id"),
            "scene": state.get("scene"),
            "last_user_query": state.get("last_user_query", ""),
            "available_solutions": state.get("available_solution_names", []),
            "signals": state.get("signals", {}),
            "response_solution_raw": state.get("response_solution_raw", ""),
            "no_action_reason_v0": v0_reason,
            "no_action_reason": v1_reason,
            "possible_missing_action": possible,
        }
        if possible and len(missing_samples) < 200:
            missing_samples.append(row)
        rows.append(row)
    write_jsonl(OUTPUT, rows)

    md = []
    md.append("# no_action_reason v1 报告")
    md.append("")
    md.append("## v0 vs v1 分布")
    md.append("### v0")
    md.append(top_counter(v0_ctr, 40))
    md.append("### v1")
    md.append(top_counter(v1_ctr, 40))
    md.append("")
    md.append(f"- explain_refund_status v0: `{v0_ctr.get('explain_refund_status', 0)}`")
    md.append(f"- explain_refund_status v1: `{v1_ctr.get('explain_refund_status', 0)}`")
    md.append(f"- 减少: `{v0_ctr.get('explain_refund_status', 0) - v1_ctr.get('explain_refund_status', 0)}`")
    md.append(f"- possible_missing_action 候选数: `{sum(1 for r in rows if r['possible_missing_action'])}`")
    md.append("")
    md.append("## 按 scene 的 unknown 比例")
    for scene, (unknown, total) in sorted(scene_unknown.items(), key=lambda kv: -(kv[1][0] / kv[1][1] if kv[1][1] else 0))[:50]:
        md.append(f"- `{scene}`: `{unknown}/{total}` ({unknown / total:.2%})")
    md.append("")
    md.append("## possible_missing_action 抽样 50")
    for row in missing_samples[:50]:
        md.append(
            f"- `{row['sample_id']}` scene=`{row['scene']}` query=`{row['last_user_query']}` "
            f"available={row['available_solutions'][:8]} response_solution=`{row['response_solution_raw']}`"
        )
    REPORT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "missing_candidates": sum(1 for r in rows if r["possible_missing_action"]), "report": str(REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

