#!/usr/bin/env python3
"""Calibrate solution registry with aliases and v1 confirmation levels."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_mining_v1.common_v1 import (
    V0_OUT,
    V1_OUT,
    V1_REPORTS,
    canonical_components,
    canonicalize_solution,
    confirmation_level,
    dump_json,
    ensure_dirs,
    get_v0_case_records_path,
    load_jsonl,
    pct,
    read_jsonl,
    split_solution_raw,
    top_counter,
)


OUTPUT = V1_OUT / "solution_registry_v1.json"
REPORT = V1_REPORTS / "solution_registry_v1_report.md"


def entry(canonical: str, pattern_type: str) -> Dict[str, Any]:
    return {
        "solution_name": canonical,
        "canonical_name": canonical,
        "aliases": [],
        "pattern_type": pattern_type,
        "requires_confirmation_level": confirmation_level(canonical),
        "available_count": 0,
        "response_count": 0,
        "agree_count": 0,
        "agree_rate": 0.0,
        "notes": [],
    }


def touch(registry: Dict[str, Dict[str, Any]], raw_name: str) -> Dict[str, Any]:
    canonical, pattern_type, notes = canonicalize_solution(raw_name)
    if not canonical or canonical == "无":
        return {}
    if canonical not in registry:
        registry[canonical] = entry(canonical, pattern_type)
    item = registry[canonical]
    if raw_name and raw_name != canonical and raw_name not in item["aliases"]:
        item["aliases"].append(raw_name)
    for note in notes:
        if note not in item["notes"]:
            item["notes"].append(note)
    return item


def main() -> None:
    ensure_dirs()
    case_path = get_v0_case_records_path()
    registry: Dict[str, Dict[str, Any]] = {}
    raw_values = collections.defaultdict(list)
    dirty_colon = collections.Counter()
    alias_fix_count = 0
    historical_count = 0
    response_raw_ctr = collections.Counter()
    agree_raw_ctr = collections.Counter()

    for record in read_jsonl(case_path):
        for sol in record.get("available_solutions", []):
            raw = sol.get("name", "")
            item = touch(registry, raw)
            if item:
                item["available_count"] += 1
                raw_values[item["canonical_name"]].append(raw)

        for field, count_field, counter in [
            ("response_solution_raw", "response_count", response_raw_ctr),
            ("dialogue_agree_solution_raw", "agree_count", agree_raw_ctr),
        ]:
            raw = record.get(field, "无")
            counter[raw] += 1
            comps, dirty_notes = split_solution_raw(raw)
            for note in dirty_notes:
                dirty_colon[note] += 1
            for comp in comps:
                item = touch(registry, comp)
                if item:
                    item[count_field] += 1
                    raw_values[item["canonical_name"]].append(comp)

    for item in registry.values():
        if item["response_count"]:
            item["agree_rate"] = round(item["agree_count"] / item["response_count"], 4)
        # Recompute alias stats.
        for alias in item["aliases"]:
            if "missing_dash_alias" in item["notes"]:
                alias_fix_count += 1
                break
        if "historical_red_packet_mapped_to_coupon" in item["notes"]:
            historical_count += 1

    conflicts = []
    for item in registry.values():
        level = item["requires_confirmation_level"]
        agree_rate = item["agree_rate"]
        if level == "no_confirmation_required" and item["agree_count"] > 0:
            conflicts.append((item, "no-confirm solution appears in DialogueAgreeSolution"))
        if level == "strong_confirmation_required" and item["response_count"] >= 20 and agree_rate < 0.02:
            conflicts.append((item, "strong-confirm solution rarely appears in DialogueAgreeSolution"))

    registry_list = sorted(
        registry.values(),
        key=lambda x: (-x["response_count"], -x["agree_count"], x["canonical_name"]),
    )
    dump_json(OUTPUT, registry_list)

    level_ctr = collections.Counter(item["requires_confirmation_level"] for item in registry_list)
    pattern_ctr = collections.Counter(item["pattern_type"] for item in registry_list)
    md = []
    md.append("# Solution Registry v1 报告")
    md.append("")
    md.append(f"- 输入 CaseRecord: `{case_path}`")
    md.append(f"- canonical solution 数: `{len(registry_list)}`")
    md.append(f"- alias 修正 solution 数: `{alias_fix_count}`")
    md.append(f"- 历史红包口径映射数: `{historical_count}`")
    md.append(f"- 冒号疑似复合脏格式 raw 数: `{sum(dirty_colon.values())}`")
    md.append("")
    md.append("## confirmation level 分布")
    md.append(top_counter(level_ctr, 20))
    md.append("")
    md.append("## pattern_type 分布")
    md.append(top_counter(pattern_ctr, 30))
    md.append("")
    md.append("## Alias 修正")
    for item in registry_list:
        if item["aliases"]:
            md.append(f"- `{item['canonical_name']}` aliases={item['aliases']} notes={item['notes']}")
    md.append("")
    md.append("## 冒号疑似复合脏格式")
    if dirty_colon:
        md.append(top_counter(dirty_colon, 50))
    else:
        md.append("- 未发现。")
    md.append("")
    md.append("## 数据表现和初始规则冲突，需训练师确认")
    if conflicts:
        for item, reason in conflicts:
            md.append(
                f"- `{item['canonical_name']}` level={item['requires_confirmation_level']} "
                f"response={item['response_count']} agree={item['agree_count']} rate={item['agree_rate']} reason={reason}"
            )
    else:
        md.append("- 暂无明显冲突。")
    md.append("")
    md.append("## Registry 明细")
    for item in registry_list:
        md.append(
            f"- `{item['canonical_name']}` type={item['pattern_type']} level={item['requires_confirmation_level']} "
            f"available={item['available_count']} response={item['response_count']} agree={item['agree_count']} rate={item['agree_rate']}"
        )
    REPORT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"registry": len(registry_list), "alias_fixes": alias_fix_count, "report": str(REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

