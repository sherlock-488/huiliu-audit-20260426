#!/usr/bin/env python3
"""Build v1 summary report."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_mining_v1.common_v1 import V0_OUT, V1_OUT, V1_REPORTS, ensure_dirs, load_jsonl, top_counter


REPORT = Path("flow_skill_mining_v1/README_REPORT.md")


def main() -> None:
    ensure_dirs()
    registry = json.loads((V1_OUT / "solution_registry_v1.json").read_text(encoding="utf-8"))
    policy = json.loads((V1_OUT / "confirmation_policy_v1.json").read_text(encoding="utf-8"))
    no_v0 = load_jsonl(V0_OUT / "no_action_labeled.jsonl")
    no_v1 = load_jsonl(V1_OUT / "no_action_labeled_v1.jsonl")
    checker_v0 = load_jsonl(V0_OUT / "global_checker_result.jsonl")
    checker_v1 = load_jsonl(V1_OUT / "global_checker_result_v1.jsonl")
    skills = {}
    for skill_file in Path("flow_skill_mining_v1/skills").glob("*_v1/skill.json"):
        skill = json.loads(skill_file.read_text(encoding="utf-8"))
        skills[skill["skill_id"]] = skill
    replay_files = {
        p.name: load_jsonl(p) for p in Path("flow_skill_mining_v1/replay").glob("*_replay.jsonl")
    }
    no_v0_ctr = collections.Counter(r.get("no_action_reason") for r in no_v0 if r.get("no_action_reason"))
    no_v1_ctr = collections.Counter(r.get("no_action_reason") for r in no_v1 if r.get("no_action_reason"))
    level_ctr = collections.Counter(r.get("requires_confirmation_level") for r in registry)
    alias_items = [r for r in registry if r.get("aliases")]
    v0_fail = sum(r.get("fail_count", 0) for r in checker_v0)
    v0_warn = sum(r.get("warning_count", 0) for r in checker_v0)
    v1_fail = sum(r.get("fail_count", 0) for r in checker_v1)
    v1_warn = sum(r.get("warning_count", 0) for r in checker_v1)

    trainer_questions = []
    for item in policy.get("solutions", []):
        if item.get("needs_trainer_confirmation") or item.get("warning_count", 0) > 0:
            trainer_questions.append(
                f"`{item.get('solution_name')}` confirmation level={item.get('requires_confirmation_level')} "
                f"response={item.get('response_count')} agree={item.get('agree_count')} unmatched={item.get('unmatched_count')}"
            )
    for skill in skills.values():
        for q in skill.get("open_questions_for_trainer", [])[:6]:
            trainer_questions.append(f"{skill['skill_id']}: {q}")
    trainer_questions.extend(
        [
            "R11 图片前置是否应从 warning 升级为 fail。",
            "ResponseSolution=无 的 possible_missing_action 是否真的是漏操作。",
            "外呼/催促类 DialogueAgreeSolution 非空是否表示授权证据还是标注噪声。",
            "引导自助查看类工具是否全部归为 no_confirmation_required。",
        ]
    )

    md = []
    md.append("# Flow Skill Mining v1 总报告")
    md.append("")
    md.append("## 1. v1 相比 v0 修了什么")
    md.append("- 增加 solution alias/canonical registry，修正自助查看缺横线、小象单商品退款历史写法、红包到优惠券历史口径。")
    md.append("- 将 confirmation policy 拆成 strong_confirmation_required / user_request_is_enough / no_confirmation_required 三层。")
    md.append("- 重新校准 no_action_reason，避免在非退款场景泛化为 explain_refund_status。")
    md.append("- Global checker v1 使用 canonical/alias，R4 只约束强确认方案，R10 重新识别商品选择。")
    md.append("- 只生成两个 replay-ready skill：履约配送、收货品质。")
    md.append("")
    md.append("## 2. solution registry alias 修正")
    if alias_items:
        for item in alias_items:
            md.append(f"- `{item['canonical_name']}` aliases={item['aliases']} notes={item['notes']}")
    else:
        md.append("- 未发现 alias。")
    md.append("")
    md.append("## 3. confirmation policy 三分层")
    md.append(top_counter(level_ctr, 10))
    md.append("")
    md.append("## 4. no_action_reason 变化")
    md.append(f"- explain_refund_status v0: `{no_v0_ctr.get('explain_refund_status', 0)}`")
    md.append(f"- explain_refund_status v1: `{no_v1_ctr.get('explain_refund_status', 0)}`")
    md.append(f"- delta: `{no_v1_ctr.get('explain_refund_status', 0) - no_v0_ctr.get('explain_refund_status', 0)}`")
    md.append("### v1 top")
    md.append(top_counter(no_v1_ctr, 30))
    md.append("")
    md.append("## 5. checker v1 vs v0")
    md.append(f"- v0 fail/warning: `{v0_fail}` / `{v0_warn}`")
    md.append(f"- v1 fail/warning: `{v1_fail}` / `{v1_warn}`")
    md.append("")
    md.append("## 6. fulfillment_delivery_v1 是否可进入离线 replay")
    fd = skills.get("fulfillment_delivery_v1", {})
    md.append(f"- action_rules: `{len(fd.get('action_rules', []))}`")
    md.append(f"- replay cases: `{len(replay_files.get('fulfillment_delivery_replay.jsonl', []))}`")
    md.append("- 建议先 replay：该场景动作集中，checker guard 相对明确。")
    md.append("")
    md.append("## 7. receipt_quality_v1 风险")
    rq = skills.get("receipt_quality_v1", {})
    md.append(f"- action_rules: `{len(rq.get('action_rules', []))}`")
    md.append(f"- replay cases: `{len(replay_files.get('receipt_quality_replay.jsonl', []))}`")
    md.append("- 风险：图片前置、商品选择识别、退款比例/赔付边界仍需训练师确认。")
    md.append("")
    md.append("## 8. replay set 样本构成")
    for name, rows in replay_files.items():
        sol_ctr = collections.Counter(r.get("gold_response_solution") for r in rows)
        focus_ctr = collections.Counter(focus for r in rows for focus in r.get("expected_checker_focus", []))
        md.append(f"### {name}")
        md.append(f"- cases: `{len(rows)}`")
        md.append("#### gold ResponseSolution")
        md.append(top_counter(sol_ctr, 20))
        md.append("#### checker focus")
        md.append(top_counter(focus_ctr, 20))
    md.append("")
    md.append("## 9. 需要训练师确认 TOP 20")
    for i, q in enumerate(trainer_questions[:20], 1):
        md.append(f"{i}. {q}")
    md.append("")
    md.append("## 10. 下一步 baseline prompt vs skill prompt 对比实验")
    md.append("1. 使用 replay jsonl 的 `input_without_target` 分别跑 baseline prompt 和插入 skill_prompt 的 prompt。")
    md.append("2. 保存模型输出为 model_outputs.jsonl，字段为 sample_id/Response/ResponseSolution/DialogueAgreeSolution。")
    md.append("3. 分别调用 `flow_skill_mining_v1/replay/evaluate_replay_outputs.py` 评估 exact/canonical/F1/checker pass。")
    md.append("4. 优先比较 forbidden_action_rate、missing_action_warning_rate、strong confirmation precision。")
    md.append("5. 对低分桶按 scene/intent/solution 回放，形成下一轮 skill patch。")
    REPORT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "v0_fail": v0_fail, "v1_fail": v1_fail}, ensure_ascii=False))


if __name__ == "__main__":
    main()

