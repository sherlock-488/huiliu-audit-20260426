#!/usr/bin/env python3
"""Global flow checker v0 for CaseRecords."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import (
    OUT_DIR,
    compact_counter,
    has_confirm_expression,
    initial_requires_agreement,
    load_jsonl_list,
    normalize_solution_name,
    same_solution_or_type,
    split_components,
    write_jsonl,
)


NO_CONFIRM_TYPES = {"系统催单", "加急调度", "智能跟单", "选择商品", "引导自助查看-xx", "外呼骑手-xx", "再次外呼骑手-xx", "外呼门店-xx", "再次外呼门店-xx"}


def _add(issues: List[Dict[str, Any]], rule: str, level: str, message: str) -> None:
    issues.append({"rule": rule, "level": level, "message": message})


def _available_norms(record: Dict[str, Any]) -> set:
    return {normalize_solution_name(sol.get("name", ""))[0] for sol in record.get("available_solutions", [])}


def _money_amount(solution: str) -> int:
    match = re.search(r"(\d+)元", solution or "")
    return int(match.group(1)) if match else -1


def check_record(record: Dict[str, Any], prev_by_sample: Dict[str, Dict[str, Any]], no_action: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    response_components = record.get("response_solution_components", [])
    agree_components = record.get("dialogue_agree_solution_components", [])
    available = _available_norms(record)
    signals = record.get("signals", {}) or {}
    scene = record.get("scene", "")

    for comp in response_components:
        norm, _ = normalize_solution_name(comp)
        if norm and norm not in available:
            _add(issues, "R1", "warning", f"ResponseSolution `{comp}` not found in available_solutions")

    for comp in agree_components:
        norm, _ = normalize_solution_name(comp)
        req = initial_requires_agreement(comp)
        if req is False or norm in NO_CONFIRM_TYPES:
            _add(issues, "R2", "warning", f"DialogueAgreeSolution `{comp}` is usually no-confirmation action")
        elif req is None:
            _add(issues, "R2", "warning", f"DialogueAgreeSolution `{comp}` confirmation requirement unclear")

    if agree_components:
        prev = prev_by_sample.get(record.get("sample_id"), {})
        prev_resp = prev.get("response_solution_components", [])
        current_resp = record.get("response_solution_components", [])
        matched = any(same_solution_or_type(a, b) for a in agree_components for b in prev_resp + current_resp)
        if not matched:
            _add(issues, "R3", "warning", "DialogueAgreeSolution does not match previous/current ResponseSolution")
        if not has_confirm_expression(record.get("last_user_query", "")):
            _add(issues, "R4", "warning", "DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression")

    if signals.get("订单是否可赔付") == "否":
        for comp in response_components + agree_components:
            if "操作赔付" in comp:
                _add(issues, "R5", "fail", "订单是否可赔付=否 but compensation solution is used")

    if signals.get("是否赔付过") == "是":
        for comp in response_components:
            if "操作赔付" in comp:
                _add(issues, "R6", "warning", "already compensated but compensation is proposed again")

    range_text = signals.get("赔付金额", "") or signals.get("可赔付金额", "")
    if range_text:
        nums = [int(x) for x in re.findall(r"\d+", range_text)]
        if nums:
            low, high = min(nums), max(nums)
            for comp in response_components + agree_components:
                if "操作赔付" in comp:
                    amount = _money_amount(comp)
                    if amount > high >= 0:
                        _add(issues, "R7", "fail", f"compensation amount {amount} exceeds range upper {high}")
                    elif 0 <= amount < low:
                        _add(issues, "R7", "warning", f"compensation amount {amount} below range lower {low}")

    if signals.get("是否可取消订单") == "否":
        for comp in response_components + agree_components:
            if comp == "取消订单":
                _add(issues, "R8", "fail", "是否可取消订单=否 but 取消订单 is used")

    # R9 is semantic note; no issue when response confirm action but agree is empty.

    selected = record.get("selected_item_info") or {}
    if any(key in scene for key in ["品质", "少送", "错送", "退款"]):
        for comp in response_components:
            norm, ptype = normalize_solution_name(comp)
            if ptype == "refund_percent" and not selected:
                _add(issues, "R10", "fail", "single-item refund used before selected_item_info is available")

    history = record.get("dialogue_history", "")
    has_image = "【图片】" in history or "系统识别图片" in history or selected.get("是否已收集图片凭证") == "是"
    if any(key in scene for key in ["品质", "日期", "实描", "口感"]) and not has_image:
        for comp in response_components:
            if "退款" in comp or "赔付" in comp:
                _add(issues, "R11", "warning", "refund/compensation in quality-like scene before image evidence")

    no = no_action.get(record.get("sample_id"), {})
    if no.get("possible_missing_action"):
        _add(issues, "R12", "warning", f"ResponseSolution=无 possible missing action, reason={no.get('no_action_reason')}")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    records = load_jsonl_list(Path(args.input))
    trajectories = load_jsonl_list(OUT_DIR / "session_trajectories.jsonl")
    by_session = collections.defaultdict(list)
    prev_by_sample = {}
    for row in trajectories:
        by_session[row.get("session_id", "")].append(row)
    for rows in by_session.values():
        rows.sort(key=lambda r: r.get("source_line", 0))
        for idx, row in enumerate(rows):
            if idx > 0:
                prev_by_sample[row.get("sample_id")] = rows[idx - 1]
    no_action = {r.get("sample_id"): r for r in load_jsonl_list(OUT_DIR / "no_action_labeled.jsonl")}

    out_rows = []
    rule_ctr = collections.Counter()
    scene_issue_ctr = collections.defaultdict(collections.Counter)
    fail_count = 0
    warn_count = 0
    top_problem_rows = []
    for record in records:
        issues = check_record(record, prev_by_sample, no_action)
        for issue in issues:
            rule_ctr[(issue["rule"], issue["level"])] += 1
            scene_issue_ctr[record.get("scene", "")][issue["level"]] += 1
        fails = sum(1 for i in issues if i["level"] == "fail")
        warns = sum(1 for i in issues if i["level"] == "warning")
        fail_count += fails
        warn_count += warns
        row = {
            "sample_id": record.get("sample_id"),
            "scene": record.get("scene"),
            "fail_count": fails,
            "warning_count": warns,
            "issues": issues,
        }
        if issues and len(top_problem_rows) < 100:
            top_problem_rows.append(row)
        out_rows.append(row)
    write_jsonl(Path(args.output), out_rows)

    md = []
    md.append("# Global Flow Checker v0 报告")
    md.append("")
    md.append(f"- 总样本数: `{len(records)}`")
    md.append(f"- fail 数: `{fail_count}`")
    md.append(f"- warning 数: `{warn_count}`")
    md.append("")
    md.append("注意：这批数据是训练师 goodcase；大量 fail/warning 不应直接判定数据错，可能是 checker 规则过严、工具名兼容或 DialogueAgreeSolution 语义需确认。")
    md.append("")
    md.append("## 各规则命中数")
    for (rule, level), count in sorted(rule_ctr.items()):
        md.append(f"- `{rule}` `{level}`: `{count}`")
    md.append("")
    md.append("## 各 scene fail/warning 分布")
    for scene, ctr in sorted(scene_issue_ctr.items(), key=lambda kv: -(kv[1]["fail"] + kv[1]["warning"]))[:50]:
        md.append(f"- `{scene}`: fail=`{ctr['fail']}`, warning=`{ctr['warning']}`")
    md.append("")
    md.append("## TOP 问题样本")
    for row in sorted(top_problem_rows, key=lambda r: -(r["fail_count"] * 10 + r["warning_count"]))[:50]:
        md.append(
            f"- `{row['sample_id']}` scene=`{row['scene']}` fail={row['fail_count']} warning={row['warning_count']} issues={row['issues'][:3]}"
        )
    md.append("")
    md.append("## 可能过严、需训练师确认")
    md.append("- R1 工具名兼容问题可能导致 available_solutions 未命中。")
    md.append("- R4 用户确认表达非常口语化，不能作为 fail。")
    md.append("- R11 图片前置是否强制，需要按品质/日期/实描等子流程确认。")
    Path(args.report).write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"fail": fail_count, "warning": warn_count, "report": args.report}, ensure_ascii=False))


if __name__ == "__main__":
    main()
