#!/usr/bin/env python3
"""Build train/dev/test splits by session_id and final README report."""

from __future__ import annotations

import collections
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import OUT_DIR, REPORT_DIR, compact_counter, ensure_dirs, load_jsonl_list, pct, write_jsonl


INPUT_PATH = OUT_DIR / "case_records.jsonl"
SPLIT_DIR = OUT_DIR / "splits"
REPORT_PATH = REPORT_DIR / "split_report.md"
README_REPORT = OUT_DIR / "README_REPORT.md"


def _split_sessions(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    sessions = collections.defaultdict(list)
    for record in records:
        sessions[record.get("session_id", "")].append(record)
    items = list(sessions.items())
    random.Random(42).shuffle(items)
    target = {"train": 0.8 * len(records), "dev": 0.1 * len(records), "test": 0.1 * len(records)}
    splits = {"train": [], "dev": [], "test": []}
    counts = {"train": 0, "dev": 0, "test": 0}
    for _, rows in sorted(items, key=lambda kv: -len(kv[1])):
        ratios = {name: counts[name] / target[name] if target[name] else 0 for name in counts}
        chosen = min(ratios, key=ratios.get)
        splits[chosen].extend(rows)
        counts[chosen] += len(rows)
    return splits


def _dist(rows: List[Dict[str, Any]], field: str, limit: int = 20) -> str:
    ctr = collections.Counter(r.get(field, "") for r in rows)
    return compact_counter(ctr, limit)


def _solution_dist(rows: List[Dict[str, Any]], field: str, limit: int = 20) -> str:
    ctr = collections.Counter(r.get(field, "") for r in rows)
    return compact_counter(ctr, limit)


def _load_report_json(name: str) -> Dict[str, Any]:
    path = REPORT_DIR / name
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _final_report(records: List[Dict[str, Any]], splits: Dict[str, List[Dict[str, Any]]]) -> None:
    case_summary = _load_report_json("case_record_report.json")
    policy = json.loads((OUT_DIR / "confirmation_policy_draft.json").read_text(encoding="utf-8")) if (OUT_DIR / "confirmation_policy_draft.json").exists() else {}
    rules = load_jsonl_list(OUT_DIR / "state_action_rules_draft.jsonl")
    checker = load_jsonl_list(OUT_DIR / "global_checker_result.jsonl")
    skill_root = Path(__file__).resolve().parent / "skills"
    skill_dirs = [p for p in skill_root.iterdir() if p.is_dir()] if skill_root.exists() else []
    no_action = load_jsonl_list(OUT_DIR / "no_action_labeled.jsonl")

    response_ctr = collections.Counter(r.get("response_solution_raw", "") for r in records)
    agree_ctr = collections.Counter(r.get("dialogue_agree_solution_raw", "") for r in records)
    scene_ctr = collections.Counter(r.get("scene", "") for r in records)
    no_reason_ctr = collections.Counter(r.get("no_action_reason", "") for r in no_action if r.get("no_action_reason"))
    strong_rules = [r for r in rules if r.get("confidence", 0) >= 0.7]
    conflict_rules = [r for r in rules if r.get("confidence", 0) < 0.7]
    strong_by_top = collections.Counter(r.get("scene", "") for r in strong_rules)
    conflict_by_scene = collections.Counter(r.get("scene", "") for r in conflict_rules)
    fail_count = sum(r.get("fail_count", 0) for r in checker)
    warning_count = sum(r.get("warning_count", 0) for r in checker)
    trainer_questions = []
    for r in conflict_rules[:50]:
        trainer_questions.append(f"规则 `{r.get('rule_id')}` 在 `{r.get('scene')}` 下 action 分歧，是否应拆更细状态？")
    for item in policy.get("solutions", []):
        if item.get("needs_trainer_confirmation"):
            trainer_questions.append(f"`{item.get('solution_name')}` 的确认语义与数据/规则存在冲突。")
    trainer_questions.extend(
        [
            "ResponseSolution=无 的 unknown 样本是否为漏操作，需训练师复核。",
            "R11 图片前置是否应从 warning 升级为 fail。",
            "外呼类方案是否真的不需要 DialogueAgreeSolution。",
            "工具名泛化（xx）和具体工具名是否应统一 registry。",
        ]
    )

    md = []
    md.append("# 流程型 Skill 自进化挖掘总报告")
    md.append("")
    md.append("## 1. 数据结构")
    md.append("这批数据是训练师精标 goodcase JSONL，每行包含 `sessionId`、`问题场景`、`source`、`input`、`target`。`input` 内含方案列表、当前时间、系统信号、商品/已选商品信息和对话历史；`target` 是 JSON 字符串，包含 `Response`、`ResponseSolution`、`DialogueAgreeSolution`。")
    md.append("")
    md.append("## 2. 为什么适合流程 skill")
    md.append("它的核心监督信号是方案选择、确认态和信号约束，而不是话术风格。`ResponseSolution` 和 `DialogueAgreeSolution` 能直接对应流程动作、前置条件与执行确认。")
    md.append("")
    md.append("## 3. 解析成功率")
    total = len(records)
    md.append(f"- CaseRecord 数: `{total}`")
    md.append(f"- target 成功解析: `{case_summary.get('target_parse_ok', 0)}` ({pct(case_summary.get('target_parse_ok', 0), total)})")
    md.append(f"- available_solutions 非空: `{case_summary.get('available_solutions_nonempty', 0)}` ({pct(case_summary.get('available_solutions_nonempty', 0), total)})")
    md.append(f"- signals 非空: `{case_summary.get('signals_nonempty', 0)}` ({pct(case_summary.get('signals_nonempty', 0), total)})")
    md.append(f"- dialogue_history 非空: `{case_summary.get('dialogue_history_nonempty', 0)}` ({pct(case_summary.get('dialogue_history_nonempty', 0), total)})")
    md.append("")
    md.append("## 4. 场景分布")
    md.append(compact_counter(scene_ctr, 30))
    md.append("")
    md.append("## 5. ResponseSolution 分布")
    md.append(compact_counter(response_ctr, 50))
    md.append("")
    md.append("## 6. DialogueAgreeSolution 分布")
    md.append(compact_counter(agree_ctr, 50))
    md.append("")
    md.append("## 7. DialogueAgreeSolution 确认语义")
    md.append("数据支持将 DialogueAgreeSolution 视为“用户已同意待确认方案”的强信号，但 unmatched 和规则冲突样本需要训练师确认，不能将其简单复制 ResponseSolution。")
    md.append("")
    md.append("## 8. 需要用户同意的 solution")
    md.append("\n".join(f"- `{x}`" for x in policy.get("must_confirm", [])[:80]) or "- 暂无")
    md.append("")
    md.append("## 9. 通常不需要用户同意的 solution")
    md.append("\n".join(f"- `{x}`" for x in policy.get("no_confirm", [])[:80]) or "- 暂无")
    md.append("")
    md.append("## 10. ResponseSolution=无 的 no_action_reason")
    md.append(compact_counter(no_reason_ctr, 40))
    md.append("")
    md.append("## 11. TOP 10 场景 strong state-action rule 数")
    for scene, _ in scene_ctr.most_common(10):
        md.append(f"- `{scene}`: `{strong_by_top.get(scene, 0)}`")
    md.append("")
    md.append("## 12. 规则冲突最多的场景")
    md.append(compact_counter(conflict_by_scene, 30))
    md.append("")
    md.append("## 13. Checker 潜在问题")
    md.append(f"- global checker fail: `{fail_count}`")
    md.append(f"- global checker warning: `{warning_count}`")
    md.append("- 这批是 goodcase，checker 命中不等于数据错误，优先解读为规则过严、工具名兼容或确认语义待确认。")
    md.append("")
    md.append("## 14. 需要训练师确认")
    for q in trainer_questions[:50]:
        md.append(f"- {q}")
    md.append("")
    md.append("## 15. 下一步接入 badcase")
    md.append("- 将 badcase 归一化成同一 CaseRecord/FlowState。")
    md.append("- 用 checker 找出 badcase 违反的流程约束。")
    md.append("- 对比 goodcase strong rules 与 badcase error pattern，形成 skill patch 候选。")
    md.append("- 将训练师确认后的 patch 写入对应 skill pack，并用 eval_cases 离线 replay。")
    md.append("")
    md.append("## 推荐下一步")
    md.append("- 第一个可实验 skill：`收货场景-品质问题`，样本量最大，流程前置（选商品/图片/退款）明确。")
    md.append("- 第二个可实验 skill：`履约场景-配送问题`，动作空间集中在催单/加急/跟单/取消。")
    md.append("- 暂不建议自动 skill 化：缺失场景、未识别、长尾金融/高危食安等，需要人工整理边界和合规规则。")
    md.append("")
    md.append("## 产物")
    md.append(f"- generated skill packs: `{len(skill_dirs)}`")
    md.append(f"- state_action_rules: `{len(rules)}`")
    md.append(f"- train/dev/test: `{len(splits['train'])}` / `{len(splits['dev'])}` / `{len(splits['test'])}`")
    README_REPORT.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    records = load_jsonl_list(INPUT_PATH)
    splits = _split_sessions(records)
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    for name, rows in splits.items():
        rows.sort(key=lambda r: (r.get("session_id", ""), r.get("source_line", 0)))
        write_jsonl(SPLIT_DIR / f"{name}.jsonl", rows)

    md = ["# Train/Dev/Test 切分报告", ""]
    for name, rows in splits.items():
        sessions = {r.get("session_id", "") for r in rows}
        md.append(f"## {name}")
        md.append(f"- 样本数: `{len(rows)}`")
        md.append(f"- session 数: `{len(sessions)}`")
        md.append("### scene 分布")
        md.append(_dist(rows, "scene", 30))
        md.append("### ResponseSolution 分布")
        md.append(_solution_dist(rows, "response_solution_raw", 30))
        md.append("### DialogueAgreeSolution 分布")
        md.append(_solution_dist(rows, "dialogue_agree_solution_raw", 30))
        md.append("")
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    _final_report(records, splits)
    print(json.dumps({"train": len(splits["train"]), "dev": len(splits["dev"]), "test": len(splits["test"]), "report": str(REPORT_PATH), "readme": str(README_REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
