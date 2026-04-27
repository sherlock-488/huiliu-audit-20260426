#!/usr/bin/env python3
"""Build solution registry from normalized CaseRecords."""

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

from flow_skill_mining.common import (
    OUT_DIR,
    REPORT_DIR,
    compact_counter,
    dump_json,
    ensure_dirs,
    initial_requires_agreement,
    load_jsonl_list,
    normalize_solution_name,
    safe_div,
    split_components,
)


INPUT_PATH = OUT_DIR / "case_records.jsonl"
OUTPUT_PATH = OUT_DIR / "solution_registry.json"
REPORT_PATH = REPORT_DIR / "solution_registry_report.md"


def _entry(name: str, pattern_type: str) -> Dict[str, Any]:
    return {
        "solution_name": name,
        "normalized_name": name,
        "pattern_type": pattern_type,
        "count_in_available_solutions": 0,
        "count_in_response_solution": 0,
        "count_in_dialogue_agree_solution": 0,
        "appears_as_component": 0,
        "is_composite_only": False,
        "example_raw_values": [],
        "requires_user_agreement_by_rule": initial_requires_agreement(name),
        "requires_user_agreement_by_data": None,
        "notes": [],
    }


def _touch(registry: Dict[str, Dict[str, Any]], raw_name: str) -> Dict[str, Any]:
    norm, pattern_type = normalize_solution_name(raw_name)
    if not norm:
        norm = str(raw_name).strip()
    if norm not in registry:
        registry[norm] = _entry(norm, pattern_type)
    entry = registry[norm]
    entry["pattern_type"] = pattern_type if entry["pattern_type"] == "exact" else entry["pattern_type"]
    examples = entry["example_raw_values"]
    if raw_name and raw_name not in examples and len(examples) < 20:
        examples.append(raw_name)
    return entry


def main() -> None:
    ensure_dirs()
    records = load_jsonl_list(INPUT_PATH)
    registry: Dict[str, Dict[str, Any]] = {}
    raw_single_seen = collections.Counter()
    raw_composite_seen = collections.Counter()
    response_raw_ctr = collections.Counter()
    agree_raw_ctr = collections.Counter()
    available_ctr = collections.Counter()

    for record in records:
        for sol in record.get("available_solutions", []):
            name = sol.get("name", "")
            if not name:
                continue
            available_ctr[name] += 1
            _touch(registry, name)["count_in_available_solutions"] += 1

        resp_raw = record.get("response_solution_raw", "无")
        response_raw_ctr[resp_raw] += 1
        resp_components = split_components(resp_raw)
        if len(resp_components) > 1:
            raw_composite_seen[resp_raw] += 1
        elif resp_components:
            raw_single_seen[resp_components[0]] += 1
        for comp in resp_components:
            entry = _touch(registry, comp)
            entry["count_in_response_solution"] += 1
            entry["appears_as_component"] += 1

        agree_raw = record.get("dialogue_agree_solution_raw", "无")
        agree_raw_ctr[agree_raw] += 1
        agree_components = split_components(agree_raw)
        if len(agree_components) > 1:
            raw_composite_seen[agree_raw] += 1
        elif agree_components:
            raw_single_seen[agree_components[0]] += 1
        for comp in agree_components:
            entry = _touch(registry, comp)
            entry["count_in_dialogue_agree_solution"] += 1
            entry["appears_as_component"] += 1

    conflicts = []
    for norm, entry in registry.items():
        response_count = entry["count_in_response_solution"]
        agree_count = entry["count_in_dialogue_agree_solution"]
        agree_rate = safe_div(agree_count, response_count)
        if agree_count >= 3 and agree_rate >= 0.05:
            entry["requires_user_agreement_by_data"] = True
        elif response_count >= 10 and agree_rate <= 0.01:
            entry["requires_user_agreement_by_data"] = False
        elif response_count >= 3 and agree_rate >= 0.2:
            entry["requires_user_agreement_by_data"] = True
        else:
            entry["requires_user_agreement_by_data"] = None
        if response_count == 0 and agree_count > 0:
            entry["notes"].append("appears in DialogueAgreeSolution but not ResponseSolution")
        if (
            entry["requires_user_agreement_by_rule"] is not None
            and entry["requires_user_agreement_by_data"] is not None
            and entry["requires_user_agreement_by_rule"] != entry["requires_user_agreement_by_data"]
        ):
            entry["notes"].append("rule/data agreement conflict; needs trainer confirmation")
            conflicts.append(entry)

    for entry in registry.values():
        only_in_composite = True
        for raw in entry["example_raw_values"]:
            if raw_single_seen[raw] > 0:
                only_in_composite = False
                break
        entry["is_composite_only"] = only_in_composite and entry["appears_as_component"] > 0

    registry_list = sorted(
        registry.values(),
        key=lambda x: (
            -x["count_in_response_solution"],
            -x["count_in_dialogue_agree_solution"],
            x["normalized_name"],
        ),
    )
    dump_json(OUTPUT_PATH, registry_list)

    type_ctr = collections.Counter(e["pattern_type"] for e in registry_list)
    md = []
    md.append("# Solution Registry 报告")
    md.append("")
    md.append(f"- solution 数: `{len(registry_list)}`")
    md.append("## pattern_type 分布")
    md.append(compact_counter(type_ctr, 50))
    md.append("")
    md.append("## ResponseSolution raw top 30")
    md.append(compact_counter(response_raw_ctr, 30))
    md.append("")
    md.append("## DialogueAgreeSolution raw top 30")
    md.append(compact_counter(agree_raw_ctr, 30))
    md.append("")
    md.append("## 规则判断与数据表现冲突")
    if conflicts:
        for entry in conflicts:
            md.append(
                f"- `{entry['normalized_name']}`: rule={entry['requires_user_agreement_by_rule']}, "
                f"data={entry['requires_user_agreement_by_data']}, "
                f"response={entry['count_in_response_solution']}, agree={entry['count_in_dialogue_agree_solution']}"
            )
    else:
        md.append("- 暂无。")
    md.append("")
    md.append("## Top solutions")
    for entry in registry_list[:80]:
        md.append(
            f"- `{entry['normalized_name']}` ({entry['pattern_type']}): "
            f"available={entry['count_in_available_solutions']}, "
            f"response={entry['count_in_response_solution']}, "
            f"agree={entry['count_in_dialogue_agree_solution']}, "
            f"rule={entry['requires_user_agreement_by_rule']}, "
            f"data={entry['requires_user_agreement_by_data']}"
        )
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"solutions": len(registry_list), "report": str(REPORT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
