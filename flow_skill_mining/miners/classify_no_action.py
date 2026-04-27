#!/usr/bin/env python3
"""Classify ResponseSolution=无 into explicit no-action reasons."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import OUT_DIR, REPORT_DIR, compact_counter, ensure_dirs, load_jsonl_list, write_jsonl


INPUT_PATH = OUT_DIR / "flow_states.jsonl"
OUTPUT_PATH = OUT_DIR / "no_action_labeled.jsonl"
REPORT_PATH = REPORT_DIR / "no_action_report.md"


BADCASE_FREQUENT_SCENE_HINTS = ["履约场景-配送", "收货场景-品质", "履约场景-履约中订单缺货", "收货场景-退款", "收货场景-少送"]


def classify_reason(state: Dict[str, Any]) -> str:
    if state.get("response_solution_components"):
        return ""
    q = state.get("last_user_query", "") or ""
    scene = state.get("scene", "") or ""
    response = state.get("response", "") or ""
    selected = state.get("selected_sku_state", "")
    image = state.get("image_state", "")
    refund_state = state.get("refund_state", "")
    already_comp = state.get("already_compensated")
    intent = state.get("user_intent", "")

    if q.strip() in {"人工", "转人工", "客服", "人工客服", "转人工客服"}:
        return "ask_user_problem"
    if intent == "transfer_request":
        return "clarify_intent"
    if intent == "close_conversation" or any(word in q for word in ["没有了", "不用了", "谢谢", "再见"]):
        return "close_conversation"
    if any(key in scene for key in ["品质", "少送", "错送", "退款"]) and selected in {"", "not_selected", "unknown"}:
        return "ask_select_product"
    if any(key in scene for key in ["品质", "日期", "实描", "口感"]) and image in {"missing_image", "unknown"}:
        return "ask_upload_image"
    if "是否已收集退款原因" in str(state.get("selected_item_info", {})) and "否" in str(
        state.get("selected_item_info", {}).get("是否已收集退款原因", "")
    ):
        return "ask_refund_reason"
    if "建议退款比例" in state.get("selected_item_info", {}) and state.get("selected_item_info", {}).get("建议退款比例") in {"", "无"}:
        return "ask_refund_ratio"
    if "数量" in q and "退款" in scene:
        return "ask_refund_quantity"
    if "取消" in refund_state or "已取消" in response:
        return "explain_order_cancelled"
    if "退款" in refund_state or "退款" in response:
        return "explain_refund_status"
    if "无法" in response or "不能" in response or "不可" in response:
        if "退款" in response:
            return "explain_cannot_refund"
        return "unavailable_capability"
    if state.get("order_status") or state.get("rider_status") or state.get("store_status"):
        if intent in {"eta_question", "delivery_urge", "no_rider"}:
            return "eta_answer_only"
        if "查询" in response or "查看" in response or "状态" in response:
            return "explain_status"
    if already_comp is True:
        return "already_compensated"
    if "外呼" in state.get("last_response_solution", "") or "稍后" in response or "等待" in response:
        return "wait_for_tool_result"
    if "还有其他问题" in response or "请问还有" in response:
        return "after_action_followup"
    if "规则" in response or "政策" in response:
        return "policy_explain"
    return "unknown"


def is_leak_candidate(state: Dict[str, Any], reason: str) -> bool:
    if state.get("response_solution_components"):
        return False
    if reason not in {"unknown", "eta_answer_only"}:
        return False
    if state.get("user_intent") in {"other", "close_conversation", "transfer_request"}:
        return False
    if not state.get("available_solution_names"):
        return False
    return any(hint in state.get("scene", "") for hint in BADCASE_FREQUENT_SCENE_HINTS)


def main() -> None:
    ensure_dirs()
    states = load_jsonl_list(INPUT_PATH)
    rows = []
    reason_ctr = collections.Counter()
    scene_reason = collections.defaultdict(collections.Counter)
    leak_candidates = []
    no_action_total = 0
    for state in states:
        reason = classify_reason(state)
        row = {
            "sample_id": state.get("sample_id", ""),
            "scene": state.get("scene", ""),
            "user_intent": state.get("user_intent", ""),
            "response_solution_raw": state.get("response_solution_raw", ""),
            "no_action_reason": reason,
            "possible_missing_action": is_leak_candidate(state, reason),
        }
        if not state.get("response_solution_components"):
            no_action_total += 1
            reason_ctr[reason] += 1
            scene_reason[state.get("scene", "")][reason] += 1
            if row["possible_missing_action"] and len(leak_candidates) < 200:
                leak_candidates.append(row)
        rows.append(row)
    write_jsonl(OUTPUT_PATH, rows)

    unknown = reason_ctr.get("unknown", 0)
    md = []
    md.append("# ResponseSolution=无 分类报告")
    md.append("")
    md.append(f"- ResponseSolution=无 总数: `{no_action_total}`")
    md.append(f"- unknown 数: `{unknown}` ({unknown / no_action_total:.2%} if nonzero)")
    md.append(f"- 漏操作候选样本数: `{sum(1 for r in rows if r.get('possible_missing_action'))}`")
    md.append("")
    md.append("## no_action_reason 分布")
    md.append(compact_counter(reason_ctr, 50))
    md.append("")
    md.append("## 按 scene 的 no_action_reason 分布")
    for scene, ctr in sorted(scene_reason.items(), key=lambda kv: -sum(kv[1].values()))[:40]:
        md.append(f"### {scene}")
        md.append(compact_counter(ctr, 20))
    md.append("")
    md.append("## 可能是漏操作的无动作样本候选 TOP")
    if leak_candidates:
        for row in leak_candidates[:50]:
            md.append(
                f"- `{row['sample_id']}` scene=`{row['scene']}` intent=`{row['user_intent']}` reason=`{row['no_action_reason']}`"
            )
    else:
        md.append("- 暂无。")
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"no_action_total": no_action_total, "report": str(REPORT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
