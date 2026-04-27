#!/usr/bin/env python3
"""Global flow checker v1 with calibrated registry/no-action semantics."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flow_skill_mining_v1.common_v1 import (
    V0_OUT,
    V1_OUT,
    V1_REPORTS,
    canonical_components,
    canonicalize_solution,
    confirmation_level,
    ensure_dirs,
    get_v0_case_records_path,
    get_v0_flow_states_path,
    has_confirm_expression,
    load_jsonl,
    pct,
    read_jsonl,
    top_counter,
    user_request_matches_action,
    write_jsonl,
)


REPORT = V1_REPORTS / "global_checker_v1_report.md"
R10_AUDIT = V1_REPORTS / "r10_fail_audit.md"


def add_issue(issues: List[Dict[str, str]], rule: str, level: str, message: str) -> None:
    issues.append({"rule": rule, "level": level, "message": message})


def item_names(record: Dict[str, Any]) -> List[str]:
    names = []
    for item in record.get("items", []):
        name = str(item.get("商品名称", "")).strip()
        if name:
            names.append(name)
    return names


def selected_item_effective(record: Dict[str, Any]) -> bool:
    info = record.get("selected_item_info", {}) or {}
    for key, value in info.items():
        if "商品" in key and str(value).strip() not in {"", "无", "不涉及", "None"}:
            return True
    history = record.get("dialogue_history", "") or ""
    recent = "\n".join(history.splitlines()[-12:]) + "\n" + (record.get("last_user_query", "") or "")
    for name in item_names(record):
        if name and (name in recent or recent in name):
            return True
    return False


def has_image_evidence(record: Dict[str, Any]) -> bool:
    info = record.get("selected_item_info", {}) or {}
    if str(info.get("是否已收集图片凭证", "")).strip() == "是":
        return True
    history = record.get("dialogue_history", "") or ""
    return "【图片】" in history or "系统识别图片" in history


def suspected_dialogue_item(record: Dict[str, Any]) -> str:
    history = record.get("dialogue_history", "") or ""
    recent = "\n".join(history.splitlines()[-12:])
    for name in item_names(record):
        if name and name in recent:
            return name
    user_lines = [line[3:].strip() for line in recent.splitlines() if line.startswith("用户:")]
    return user_lines[-1] if user_lines else ""


def compensation_amount(solution: str) -> int:
    m = re.search(r"(\d+)元", solution)
    return int(m.group(1)) if m else -1


def build_prev_recent(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    by_session = collections.defaultdict(list)
    for record in records:
        by_session[record.get("session_id", "")].append(record)
    recent_by_sample = {}
    for rows in by_session.values():
        rows.sort(key=lambda r: r.get("source_line", 0))
        for idx, row in enumerate(rows):
            recent_by_sample[row["sample_id"]] = rows[max(0, idx - 3) : idx + 1]
    return recent_by_sample


def check_record(record: Dict[str, Any], state: Dict[str, Any], recent: List[Dict[str, Any]], no_action: Dict[str, Any], registry: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    resp_components, resp_notes = canonical_components(record.get("response_solution_raw", "无"))
    agree_components, agree_notes = canonical_components(record.get("dialogue_agree_solution_raw", "无"))
    available = {canonicalize_solution(sol.get("name", ""))[0] for sol in record.get("available_solutions", [])}
    signals = record.get("signals", {}) or {}

    # R1
    for comp in resp_components:
        if comp and comp not in available:
            reg = registry.get(comp, {})
            if any("historical" in n for n in reg.get("notes", [])):
                add_issue(issues, "R1", "warning", f"historical tool name maps to `{comp}`")
            elif comp.startswith("引导自助查看-") and "引导自助查看-xx" in available:
                pass
            else:
                add_issue(issues, "R1", "warning", f"canonical ResponseSolution `{comp}` not in available_solutions")

    # R2, R3, R4
    recent_resp = []
    for r in recent:
        comps, _ = canonical_components(r.get("response_solution_raw", "无"))
        recent_resp.extend(comps)
    for comp in agree_components:
        level = registry.get(comp, {}).get("requires_confirmation_level", confirmation_level(comp))
        if level == "no_confirmation_required":
            add_issue(issues, "R2", "warning", f"no-confirm solution `{comp}` appears in DialogueAgreeSolution")
        elif level == "unclear":
            add_issue(issues, "R2", "warning", f"unclear confirmation level for `{comp}`")

        if level == "strong_confirmation_required":
            if comp not in recent_resp:
                add_issue(issues, "R3", "warning", f"strong confirmation `{comp}` does not match recent ResponseSolution")
            if not has_confirm_expression(record.get("last_user_query", "")):
                add_issue(issues, "R4", "warning", f"strong confirmation `{comp}` lacks explicit confirm expression")
        elif level == "user_request_is_enough":
            if comp not in recent_resp and not user_request_matches_action(record.get("last_user_query", ""), comp):
                add_issue(issues, "R3", "warning", f"user-request action `{comp}` has no recent offer or matching user request")

    # R5/R6/R7/R8
    if signals.get("订单是否可赔付") == "否":
        for comp in resp_components + agree_components:
            if "操作赔付" in comp:
                add_issue(issues, "R5", "fail", "订单是否可赔付=否 but compensation used")
    if signals.get("是否赔付过") == "是" and not re.search(r"再赔|继续赔|还要赔|赔偿", record.get("last_user_query", "")):
        for comp in resp_components:
            if "操作赔付" in comp:
                add_issue(issues, "R6", "warning", "already compensated but active compensation proposed")
    range_text = signals.get("赔付金额", "") or signals.get("可赔付金额", "")
    nums = [int(x) for x in re.findall(r"\d+", range_text or "")]
    if nums:
        low, high = min(nums), max(nums)
        for comp in resp_components + agree_components:
            if "操作赔付" in comp:
                amount = compensation_amount(comp)
                if amount > high >= 0:
                    add_issue(issues, "R7", "fail", f"compensation amount {amount} exceeds upper {high}")
                elif 0 <= amount < low:
                    add_issue(issues, "R7", "warning", f"compensation amount {amount} below lower {low}")
    if signals.get("是否可取消订单") == "否":
        for comp in resp_components + agree_components:
            if comp == "取消订单":
                add_issue(issues, "R8", "fail", "是否可取消订单=否 but 取消订单 used")

    # R10
    if any(comp == "小象单商品退款-xx%" for comp in resp_components):
        if not selected_item_effective(record):
            add_issue(issues, "R10", "fail", "single-item refund before selected product")

    # R11
    if any(key in record.get("scene", "") for key in ["品质", "日期", "实描", "口感"]):
        if any(comp in {"小象单商品退款-xx%", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元"} for comp in resp_components):
            if not has_image_evidence(record):
                add_issue(issues, "R11", "warning", "quality-like refund/compensation before image evidence")

    # R12
    if no_action.get("possible_missing_action"):
        add_issue(issues, "R12", "warning", f"possible missing action; no_action_reason={no_action.get('no_action_reason')}")
    return issues


def main() -> None:
    ensure_dirs()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(get_v0_case_records_path()))
    parser.add_argument("--output", default=str(V1_OUT / "global_checker_result_v1.jsonl"))
    parser.add_argument("--report", default=str(REPORT))
    args = parser.parse_args()

    records = load_jsonl(Path(args.input))
    states = {r.get("sample_id"): r for r in load_jsonl(get_v0_flow_states_path())}
    registry = {r["canonical_name"]: r for r in json.loads((V1_OUT / "solution_registry_v1.json").read_text(encoding="utf-8"))}
    no_actions = {r.get("sample_id"): r for r in load_jsonl(V1_OUT / "no_action_labeled_v1.jsonl")}
    recent_by_sample = build_prev_recent(records)
    v0_checker = load_jsonl(V0_OUT / "global_checker_result.jsonl")
    v0_fail = sum(r.get("fail_count", 0) for r in v0_checker)
    v0_warn = sum(r.get("warning_count", 0) for r in v0_checker)

    out_rows = []
    rule_ctr = collections.Counter()
    scene_ctr = collections.defaultdict(collections.Counter)
    r10_audit = []
    delivery_r12 = []
    quality_r10_r11 = []
    for record in records:
        sample_id = record.get("sample_id")
        issues = check_record(
            record,
            states.get(sample_id, {}),
            recent_by_sample.get(sample_id, []),
            no_actions.get(sample_id, {}),
            registry,
        )
        fail_count = sum(1 for i in issues if i["level"] == "fail")
        warning_count = sum(1 for i in issues if i["level"] == "warning")
        for issue in issues:
            rule_ctr[(issue["rule"], issue["level"])] += 1
            scene_ctr[record.get("scene", "")][issue["level"]] += 1
        if any(i["rule"] == "R10" for i in issues):
            r10_audit.append(
                {
                    "sample_id": sample_id,
                    "scene": record.get("scene", ""),
                    "last_user_query": record.get("last_user_query", ""),
                    "selected_item_info": record.get("selected_item_info", {}),
                    "items": item_names(record),
                    "dialogue_suspected_selection": suspected_dialogue_item(record),
                    "response_solution": record.get("response_solution_raw", ""),
                }
            )
        if record.get("scene") == "履约场景-配送问题" and any(i["rule"] == "R12" for i in issues):
            delivery_r12.append(sample_id)
        if record.get("scene") == "收货场景-品质问题" and any(i["rule"] in {"R10", "R11"} for i in issues):
            quality_r10_r11.append(sample_id)
        out_rows.append(
            {
                "sample_id": sample_id,
                "scene": record.get("scene"),
                "fail_count": fail_count,
                "warning_count": warning_count,
                "issues": issues,
            }
        )
    write_jsonl(Path(args.output), out_rows)

    fail = sum(r["fail_count"] for r in out_rows)
    warn = sum(r["warning_count"] for r in out_rows)
    r10_count = rule_ctr.get(("R10", "fail"), 0)
    md = []
    md.append("# Global Flow Checker v1 报告")
    md.append("")
    md.append(f"- 总样本数: `{len(records)}`")
    md.append(f"- v0 fail/warning: `{v0_fail}` / `{v0_warn}`")
    md.append(f"- v1 fail/warning: `{fail}` / `{warn}`")
    md.append(f"- R10 fail: `{r10_count}`")
    md.append(f"- 履约配送 R12 候选: `{len(delivery_r12)}`")
    md.append(f"- 收货品质 R10/R11 候选: `{len(quality_r10_r11)}`")
    md.append("")
    md.append("## 各规则命中")
    for (rule, level), count in sorted(rule_ctr.items()):
        md.append(f"- `{rule}` `{level}`: `{count}`")
    md.append("")
    md.append("## 各 scene fail/warning 分布")
    for scene, ctr in sorted(scene_ctr.items(), key=lambda kv: -(kv[1]["fail"] + kv[1]["warning"]))[:50]:
        md.append(f"- `{scene}`: fail=`{ctr['fail']}`, warning=`{ctr['warning']}`")
    md.append("")
    md.append("## 仍需训练师确认")
    md.append("- R11 图片前置目前只 warning，是否升级为 fail 需确认。")
    md.append("- user_request_is_enough 类外呼/催促方案是否允许 DialogueAgreeSolution 非空，需确认标注口径。")
    md.append("- R12 漏操作候选应由训练师抽样区分好 case 中合理无动作与真正漏动作。")
    Path(args.report).write_text("\n".join(md) + "\n", encoding="utf-8")

    audit_md = ["# R10 fail 专项审计", "", f"- R10 fail 数: `{len(r10_audit)}`", ""]
    for row in r10_audit:
        audit_md.append(f"## {row['sample_id']}")
        audit_md.append(f"- scene: `{row['scene']}`")
        audit_md.append(f"- last_user_query: `{row['last_user_query']}`")
        audit_md.append(f"- selected_item_info: `{json.dumps(row['selected_item_info'], ensure_ascii=False)}`")
        audit_md.append(f"- items 商品名: `{row['items']}`")
        audit_md.append(f"- dialogue 疑似商品选择: `{row['dialogue_suspected_selection']}`")
        audit_md.append(f"- ResponseSolution: `{row['response_solution']}`")
        audit_md.append("")
    R10_AUDIT.write_text("\n".join(audit_md), encoding="utf-8")
    print(json.dumps({"fail": fail, "warning": warn, "r10_fail": r10_count, "report": str(args.report)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

