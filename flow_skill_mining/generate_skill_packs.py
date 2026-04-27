#!/usr/bin/env python3
"""Generate draft skill packs for top scenes."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break

from flow_skill_mining.common import OUT_DIR, ROOT, ensure_dirs, load_jsonl_list, normalize_solution_name


SKILL_DIR = ROOT / "flow_skill_mining" / "skills"
REPORT_PATH = OUT_DIR / "reports" / "skill_pack_report.md"

TOP_SCENES = [
    ("收货场景-品质问题", "receipt_quality"),
    ("履约场景-修改订单问题", "fulfillment_modify_order"),
    ("履约场景-配送问题", "fulfillment_delivery"),
    ("收货场景-少送问题", "receipt_short_delivery"),
    ("发票场景", "invoice"),
    ("收货场景-错送问题", "receipt_wrong_delivery"),
    ("会员场景-续费问题", "member_renewal"),
    ("收货场景-退款问题", "receipt_refund"),
    ("活动场景-常规活动问题", "activity_regular"),
    ("会员场景-权益问题", "member_benefit"),
]


def _top(counter: collections.Counter, limit: int) -> List[str]:
    return [k for k, _ in counter.most_common(limit) if k and k != "无"]


def _sample_eval_cases(states: List[Dict[str, Any]], no_action: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_solution = collections.defaultdict(list)
    agree_rows = []
    for state in states:
        key = state.get("response_solution_raw", "无")
        by_solution[key].append(state)
        if state.get("dialogue_agree_solution_components"):
            agree_rows.append(state)
    selected = []
    seen = set()
    for key, rows in sorted(by_solution.items(), key=lambda kv: -len(kv[1])):
        take = max(1, min(20, 200 // max(len(by_solution), 1)))
        for row in rows[:take]:
            if row["sample_id"] not in seen:
                selected.append(row)
                seen.add(row["sample_id"])
    for row in agree_rows[:50]:
        if row["sample_id"] not in seen:
            selected.append(row)
            seen.add(row["sample_id"])
    selected = selected[:200]
    return [
        {
            "sample_id": row.get("sample_id"),
            "scene": row.get("scene"),
            "signals": row.get("signals", {}),
            "last_user_query": row.get("last_user_query", ""),
            "dialogue_history": row.get("dialogue_history", ""),
            "response_solution": row.get("response_solution_raw", "无"),
            "dialogue_agree_solution": row.get("dialogue_agree_solution_raw", "无"),
            "no_action_reason": no_action.get(row.get("sample_id"), {}).get("no_action_reason", ""),
        }
        for row in selected
    ]


def main() -> None:
    ensure_dirs()
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    states = load_jsonl_list(OUT_DIR / "flow_states.jsonl")
    rules = load_jsonl_list(OUT_DIR / "state_action_rules_draft.jsonl")
    policy = json.loads((OUT_DIR / "confirmation_policy_draft.json").read_text(encoding="utf-8"))
    no_action = {r.get("sample_id"): r for r in load_jsonl_list(OUT_DIR / "no_action_labeled.jsonl")}

    must_confirm = set(policy.get("must_confirm", []))
    no_confirm = set(policy.get("no_confirm", []))
    states_by_scene = collections.defaultdict(list)
    rules_by_scene = collections.defaultdict(list)
    for state in states:
        states_by_scene[state.get("scene", "")].append(state)
    for rule in rules:
        rules_by_scene[rule.get("scene", "")].append(rule)

    generated = []
    for scene, skill_id in TOP_SCENES:
        scene_states = states_by_scene.get(scene, [])
        if not scene_states:
            continue
        scene_rules = sorted(rules_by_scene.get(scene, []), key=lambda r: (-r.get("confidence", 0), -r.get("support", 0)))[:30]
        response_ctr = collections.Counter(s.get("response_solution_raw", "无") for s in scene_states)
        intent_ctr = collections.Counter(s.get("user_intent", "") for s in scene_states)
        signal_key_ctr = collections.Counter(key for s in scene_states for key, value in s.get("signals", {}).items() if value not in ("", None))
        candidate_solutions = _top(response_ctr, 30)
        confirm_solutions = sorted({normalize_solution_name(x)[0] for x in candidate_solutions if normalize_solution_name(x)[0] in must_confirm})
        no_confirm_solutions = sorted({normalize_solution_name(x)[0] for x in candidate_solutions if normalize_solution_name(x)[0] in no_confirm})
        high_conf_rules = [r for r in scene_rules if r.get("confidence", 0) >= 0.7]
        open_questions = []
        for r in scene_rules:
            if r.get("confidence", 1) < 0.7:
                open_questions.append(f"同一状态下 `{r.get('expected_response_solution')}` 与其他动作存在分歧，需要确认。")
            if len(open_questions) >= 8:
                break
        skill = {
            "skill_id": skill_id,
            "scene": scene,
            "version": "v0.1-draft",
            "source": "trainer_goodcase_mining",
            "scope": {"scene": scene, "supported_intents": _top(intent_ctr, 20)},
            "required_signals": _top(signal_key_ctr, 30),
            "candidate_solutions": candidate_solutions,
            "confirmation_required_solutions": confirm_solutions,
            "no_confirmation_required_solutions": no_confirm_solutions,
            "priority_rules": [r for r in high_conf_rules if r.get("candidate_skill_patch_type") in {"priority_rule", "tool_rule"}][:15],
            "no_action_rules": [r for r in high_conf_rules if r.get("candidate_skill_patch_type") == "no_action_rule"][:15],
            "forbidden_rules": [],
            "clarify_rules": [r for r in high_conf_rules if r.get("candidate_skill_patch_type") == "clarify_rule"][:15],
            "evidence": {
                "support_cases": len(scene_states),
                "example_sample_ids": [s.get("sample_id") for s in scene_states[:20]],
            },
            "open_questions_for_trainer": open_questions,
        }
        path = SKILL_DIR / skill_id
        path.mkdir(parents=True, exist_ok=True)
        (path / "skill.json").write_text(json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8")
        prompt = f"""# {scene} 流程 skill 草案

适用场景：仅用于 `{scene}`。本 skill 只约束流程动作，不负责生成漂亮话术。

必读信号：{', '.join(skill['required_signals'][:20])}

ResponseSolution 选择规则：优先根据用户当前诉求、订单/退款/赔付/商品选择状态选择可执行方案；高频候选方案包括：{', '.join(candidate_solutions[:15]) or '无'}。如果当前只是询问状态、缺商品、缺图片、缺退款原因，ResponseSolution 可以为“无”，但必须有明确 no_action_reason。

DialogueAgreeSolution 填写规则：只有用户已经明确同意取消、退款、赔付、会员卡退款等待确认方案时才填写。用户未明确同意时，即使客服本轮提出方案，DialogueAgreeSolution 也应为“无”。疑似需要确认的方案：{', '.join(confirm_solutions) or '待训练师确认'}。

禁止项：不要把 DialogueAgreeSolution 简单复制 ResponseSolution；不可赔付时不得填赔付方案；不可取消时不得填取消订单；需要商品或图片前置时不得直接进入单商品退款。

ResponseSolution=无 的合理原因：澄清诉求、请用户选择商品、请用户上传图片、解释订单/退款状态、等待工具结果、动作后的追问或结束会话。
"""
        (path / "skill_prompt.md").write_text(prompt[:1200] + "\n", encoding="utf-8")
        checker = [
            f"# {scene} checker rules",
            "",
            "- 检查 ResponseSolution 是否属于该场景候选方案或 available_solutions。",
            "- DialogueAgreeSolution 非无时，必须是确认型方案，且 last_user_query 应有明确同意表达。",
            "- signals['订单是否可赔付']='否' 时，不允许操作赔付。",
            "- signals['是否可取消订单']='否' 时，不允许取消订单。",
            "- 收货类单商品退款前必须有 selected_item_info；品质/实描/日期问题建议要求图片凭证。",
            "- ResponseSolution=无 时必须能归入 no_action_reason，否则标记为漏操作候选。",
        ]
        (path / "checker_rules.md").write_text("\n".join(checker) + "\n", encoding="utf-8")
        eval_cases = _sample_eval_cases(scene_states, no_action)
        with (path / "eval_cases.jsonl").open("w", encoding="utf-8") as f:
            for row in eval_cases:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        readme = [
            f"# {scene}",
            "",
            f"- support cases: `{len(scene_states)}`",
            f"- high confidence rules: `{len(high_conf_rules)}`",
            f"- eval cases: `{len(eval_cases)}`",
            "",
            "## 高置信依据",
        ]
        for r in high_conf_rules[:20]:
            readme.append(
                f"- `{r.get('rule_id')}` support={r.get('support')} confidence={r.get('confidence')} expected={r.get('expected_response_solution')}"
            )
        readme.append("")
        readme.append("## 需要训练师确认")
        readme.extend(f"- {q}" for q in open_questions) if open_questions else readme.append("- 暂无。")
        readme.append("")
        readme.append("## 离线 replay")
        readme.append("- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。")
        (path / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
        generated.append({"skill_id": skill_id, "scene": scene, "support": len(scene_states), "rules": len(high_conf_rules)})

    md = ["# Skill Pack 生成报告", "", f"- generated skill packs: `{len(generated)}`", ""]
    for item in generated:
        md.append(f"- `{item['skill_id']}` scene=`{item['scene']}` support={item['support']} high_conf_rules={item['rules']}")
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"generated_skill_packs": len(generated), "report": str(REPORT_PATH)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
