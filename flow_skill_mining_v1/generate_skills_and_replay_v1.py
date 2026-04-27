#!/usr/bin/env python3
"""Generate replay-ready v1 skills and replay datasets for two target scenes."""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_mining_v1.common_v1 import (
    ROOT,
    V0_OUT,
    V1_OUT,
    V1_ROOT,
    canonical_components,
    canonicalize_solution,
    confirmation_level,
    ensure_dirs,
    get_v0_case_records_path,
    get_v0_flow_states_path,
    load_jsonl,
    read_jsonl,
    write_jsonl,
)


TARGETS = {
    "履约场景-配送问题": {
        "skill_id": "fulfillment_delivery_v1",
        "dir": "fulfillment_delivery_v1",
        "replay": "fulfillment_delivery_replay.jsonl",
        "high_value": ["系统催单", "加急调度", "外呼骑手-xx", "再次外呼骑手-xx", "智能跟单", "取消订单", "操作赔付-优惠券-xx元"],
        "must_intents": ["eta_question", "delivery_urge", "contact_rider", "cancel_request", "compensation_request", "no_rider"],
    },
    "收货场景-品质问题": {
        "skill_id": "receipt_quality_v1",
        "dir": "receipt_quality_v1",
        "replay": "receipt_quality_replay.jsonl",
        "high_value": ["选择商品", "小象单商品退款-xx%", "操作赔付-优惠券-xx元", "催促退款审核", "退审跟单"],
        "must_intents": ["quality_issue", "refund_request", "refund_progress", "close_conversation"],
    },
}


def _canon(raw: str) -> str:
    comps, _ = canonical_components(raw)
    return comps[0] if comps else "无"


def _load_original_inputs(source_lines: set[int], source_file: str) -> Dict[int, str]:
    inputs = {}
    if not source_lines:
        return inputs
    with Path(source_file).open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            if line_no not in source_lines:
                continue
            try:
                obj = json.loads(line)
                inputs[line_no] = obj.get("input", "")
            except Exception:
                inputs[line_no] = ""
            if len(inputs) == len(source_lines):
                break
    return inputs


def build_skill(scene: str, cfg: Dict[str, Any], states: List[Dict[str, Any]], rules: List[Dict[str, Any]], no_action: Dict[str, Dict[str, Any]], policy: Dict[str, Any], registry: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    scene_states = [s for s in states if s.get("scene") == scene]
    candidate_rules = []
    for rule in rules:
        if rule.get("scene") != scene:
            continue
        if rule.get("support", 0) < 5 or rule.get("confidence", 0) < 0.8:
            continue
        if rule.get("expected_response_solution") == "无":
            continue
        canon = _canon(rule.get("expected_response_solution", ""))
        if canon not in cfg["high_value"]:
            continue
        r = dict(rule)
        r["expected_response_solution_canonical"] = canon
        candidate_rules.append(r)
    candidate_rules.sort(key=lambda r: (-r.get("confidence", 0), -r.get("support", 0)))

    scene_no = [no_action.get(s.get("sample_id"), {}) for s in scene_states if not s.get("response_solution_components")]
    reason_ctr = collections.Counter(r.get("no_action_reason") for r in scene_no if r.get("no_action_reason"))
    no_action_rules = [
        {"no_action_reason": reason, "support": count, "condition_hint": "see replay cases and checker focus"}
        for reason, count in reason_ctr.most_common(12)
    ]
    signals = collections.Counter(k for s in scene_states for k, v in (s.get("signals") or {}).items() if v not in ("", None))
    solutions = sorted({_canon(s.get("response_solution_raw", "")) for s in scene_states if _canon(s.get("response_solution_raw", "")) != "无"})
    policy_by_level = collections.defaultdict(list)
    for sol in solutions:
        level = registry.get(sol, {}).get("requires_confirmation_level", confirmation_level(sol))
        policy_by_level[level].append(sol)
    conflict_rules = [r for r in rules if r.get("scene") == scene and r.get("confidence", 1) < 0.7]
    open_questions = [
        f"`{r.get('rule_id')}` support={r.get('support')} confidence={r.get('confidence')} expected={r.get('expected_response_solution')}"
        for r in conflict_rules[:12]
    ]
    skill = {
        "skill_id": cfg["skill_id"],
        "scene": scene,
        "version": "v1.0-replay-draft",
        "purpose": "约束流程动作，不优化话术",
        "entry_conditions": [f"问题场景 == {scene}"],
        "required_signals": [k for k, _ in signals.most_common(30)],
        "solution_policy": {
            "strong_confirmation_required": sorted(policy_by_level.get("strong_confirmation_required", [])),
            "user_request_is_enough": sorted(policy_by_level.get("user_request_is_enough", [])),
            "no_confirmation_required": sorted(policy_by_level.get("no_confirmation_required", [])),
        },
        "action_rules": candidate_rules[:40],
        "no_action_rules": no_action_rules,
        "confirmation_rules": [
            "强确认方案：取消订单、退款、赔付、会员卡退款等，只有用户明确同意后 DialogueAgreeSolution 才能非空。",
            "外呼/催促类方案属于 user_request_is_enough，不要求 DialogueAgreeSolution 非空。",
        ],
        "guard_rules": [
            "不可赔付不得赔付",
            "已赔付过不得再次主动赔",
            "赔付金额不得超过信号上限",
            "不可取消不得取消",
            "未选商品不得单商品退款",
            "需要图片前置的质量类问题，未有图片时优先引导上传",
            "不得输出 available_solutions 中没有的方案，除非命中 alias",
        ],
        "forbidden_rules": [
            "不要把 DialogueAgreeSolution 简单复制 ResponseSolution",
            "不要在用户未确认强确认方案时填 DialogueAgreeSolution",
        ],
        "evidence": {
            "positive_cases": len(scene_states),
            "strong_rules": len(candidate_rules),
            "conflict_rules": len(conflict_rules),
        },
        "open_questions_for_trainer": open_questions,
    }
    return skill


def prompt_for_skill(skill: Dict[str, Any]) -> str:
    scene = skill["scene"]
    strong = "、".join(skill["solution_policy"]["strong_confirmation_required"]) or "无"
    user_req = "、".join(skill["solution_policy"]["user_request_is_enough"]) or "无"
    no_confirm = "、".join(skill["solution_policy"]["no_confirmation_required"][:12]) or "无"
    action_lines = []
    for rule in skill["action_rules"][:8]:
        action_lines.append(
            f"- 当状态满足 {rule.get('state_pattern')} 时，优先考虑 `{rule.get('expected_response_solution_canonical')}`。"
        )
    no_action = "；".join(f"{r['no_action_reason']}({r['support']})" for r in skill["no_action_rules"][:8])
    text = f"""# {scene} 流程 Skill v1

目的：只约束流程动作，不优化话术。进入条件：问题场景为 `{scene}`。

必读信号：{', '.join(skill['required_signals'][:18])}。

动作选择规则：
{chr(10).join(action_lines) if action_lines else '- 当前没有足够高置信动作规则，优先使用 guard 与澄清规则。'}

确认规则：强确认方案包括 {strong}。这些方案只有在用户明确同意（可以、同意、行、好、确认、退吧、赔吧、取消吧、帮我处理等）后，DialogueAgreeSolution 才能非空。{user_req} 属于用户诉求即授权，ResponseSolution 可以直接执行，DialogueAgreeSolution 可为空。

无需确认方案：{no_confirm}。

ResponseSolution=无 的合理原因：{no_action}。如果用户诉求明确且已有可执行方案，不要随意输出“无”。

守卫：不可赔付不得赔付；已赔付过不得再次主动赔；赔付金额不得超过信号上限；不可取消不得取消；未选商品不得单商品退款；质量类未有图片时优先引导上传；不得输出候选方案外的工具，除非命中 alias。
"""
    return text[:1200] + "\n"


def checker_rules_text(skill: Dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {skill['skill_id']} checker rules",
            "",
            "- ResponseSolution 必须命中 available_solutions 或 registry alias。",
            "- strong_confirmation_required 方案的 DialogueAgreeSolution 必须有用户确认表达，并匹配近 3 轮 ResponseSolution。",
            "- user_request_is_enough 方案不要求 DialogueAgreeSolution 非空。",
            "- 不可赔付/不可取消/已赔付过等 guard 失败时标 fail 或 warning。",
            "- 单商品退款必须先识别有效商品选择。",
            "- 品质类退款/赔付缺图片时先 warning，待训练师确认是否升级为 fail。",
            "- ResponseSolution=无 必须能落到 no_action_reason，否则进入漏操作候选。",
        ]
    ) + "\n"


def build_replay(scene: str, cfg: Dict[str, Any], test_records: List[Dict[str, Any]], states_by_id: Dict[str, Dict[str, Any]], no_action: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = [r for r in test_records if r.get("scene") == scene]
    by_bucket = collections.defaultdict(list)
    for r in rows:
        st = states_by_id.get(r.get("sample_id"), {})
        no = no_action.get(r.get("sample_id"), {})
        key = r.get("response_solution_raw", "无")
        if key == "无":
            key = "无:" + no.get("no_action_reason", "")
        if r.get("dialogue_agree_solution_components"):
            key = "agree:" + r.get("dialogue_agree_solution_raw", "")
        by_bucket[key].append(r)
        if st.get("user_intent") in cfg["must_intents"]:
            by_bucket["intent:" + st.get("user_intent")].append(r)
    selected = []
    seen = set()
    for _, bucket in sorted(by_bucket.items(), key=lambda kv: -len(kv[1])):
        take = max(1, min(15, 300 // max(1, len(by_bucket))))
        for r in bucket[:take]:
            if r["sample_id"] not in seen:
                selected.append(r)
                seen.add(r["sample_id"])
        if len(selected) >= 300:
            break
    selected = selected[:300]
    source_lines = {r.get("source_line") for r in selected}
    source_file = selected[0].get("source_file") if selected else ""
    original_inputs = _load_original_inputs(source_lines, source_file) if source_file else {}
    out = []
    for r in selected:
        st = states_by_id.get(r.get("sample_id"), {})
        no = no_action.get(r.get("sample_id"), {})
        focus = []
        if r.get("dialogue_agree_solution_components"):
            focus.append("confirmation")
        if r.get("response_solution_raw") == "无":
            focus.append("no_action")
        if scene == "履约场景-配送问题" and st.get("user_intent") in cfg["must_intents"]:
            focus.append(st.get("user_intent"))
        if scene == "收货场景-品质问题":
            if no.get("no_action_reason") in {"ask_select_product", "ask_upload_image", "ask_refund_reason", "ask_refund_ratio"}:
                focus.append(no.get("no_action_reason"))
            if _canon(r.get("response_solution_raw")) in {"小象单商品退款-xx%", "操作赔付-优惠券-xx元"}:
                focus.append("refund_or_compensation")
        out.append(
            {
                "sample_id": r.get("sample_id"),
                "session_id": r.get("session_id"),
                "scene": scene,
                "input_without_target": original_inputs.get(r.get("source_line"), ""),
                "signals": r.get("signals", {}),
                "available_solutions": r.get("available_solutions", []),
                "dialogue_history": r.get("dialogue_history", ""),
                "last_user_query": r.get("last_user_query", ""),
                "gold_response_solution": r.get("response_solution_raw", "无"),
                "gold_dialogue_agree_solution": r.get("dialogue_agree_solution_raw", "无"),
                "gold_no_action_reason": no.get("no_action_reason", ""),
                "skill_id": cfg["skill_id"],
                "expected_checker_focus": sorted(set(focus)),
            }
        )
    return out


def main() -> None:
    ensure_dirs()
    skill_root = V1_ROOT / "skills"
    replay_root = V1_ROOT / "replay"
    skill_root.mkdir(parents=True, exist_ok=True)
    replay_root.mkdir(parents=True, exist_ok=True)
    states = load_jsonl(get_v0_flow_states_path())
    states_by_id = {s.get("sample_id"): s for s in states}
    rules = load_jsonl(V0_OUT / "state_action_rules_draft.jsonl")
    no_action = {r.get("sample_id"): r for r in load_jsonl(V1_OUT / "no_action_labeled_v1.jsonl")}
    registry = {r["canonical_name"]: r for r in json.loads((V1_OUT / "solution_registry_v1.json").read_text(encoding="utf-8"))}
    policy = json.loads((V1_OUT / "confirmation_policy_v1.json").read_text(encoding="utf-8"))
    test_records = load_jsonl(V0_OUT / "splits" / "test.jsonl")
    summary = []
    for scene, cfg in TARGETS.items():
        skill = build_skill(scene, cfg, states, rules, no_action, policy, registry)
        path = skill_root / cfg["dir"]
        path.mkdir(parents=True, exist_ok=True)
        (path / "skill.json").write_text(json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8")
        (path / "skill_prompt.md").write_text(prompt_for_skill(skill), encoding="utf-8")
        (path / "checker_rules.md").write_text(checker_rules_text(skill), encoding="utf-8")
        questions = ["# Open Questions", ""]
        questions.extend(f"- {q}" for q in skill["open_questions_for_trainer"])
        (path / "open_questions.md").write_text("\n".join(questions) + "\n", encoding="utf-8")
        readme = [
            f"# {skill['skill_id']}",
            "",
            f"- scene: `{scene}`",
            f"- positive_cases: `{skill['evidence']['positive_cases']}`",
            f"- action_rules: `{len(skill['action_rules'])}`",
            f"- conflict_rules: `{skill['evidence']['conflict_rules']}`",
            "- purpose: 约束流程动作，不优化话术。",
        ]
        (path / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
        replay = build_replay(scene, cfg, test_records, states_by_id, no_action)
        write_jsonl(replay_root / cfg["replay"], replay)
        summary.append({"skill_id": cfg["skill_id"], "scene": scene, "action_rules": len(skill["action_rules"]), "replay": len(replay)})
    print(json.dumps({"skills": summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

