#!/usr/bin/env python3
"""Generate policy-based v2 skill packs for two replay scenes."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_policy_v2.common import V2_ROOT, ensure_dirs, get_case_records_path, read_jsonl, write_jsonl
from flow_skill_policy_v2.policies.fulfillment_delivery_policy import OPEN_QUESTIONS_FOR_TRAINER as FD_QUESTIONS
from flow_skill_policy_v2.policies.receipt_quality_policy import OPEN_QUESTIONS_FOR_TRAINER as RQ_QUESTIONS


FD_PROMPT = """【履约配送流程规则 v2】
适用：问题场景为“履约场景-配送问题”，目标是约束流程动作，不优化话术。
1. 先读信号：订单状态、是否配送单、骑手状态、是否超时/有超时风险、是否可取消、是否可赔付、是否已赔付、赔付金额、是否有骑手手机号、送达图片。
2. 普通 ETA：用户只是问什么时候送到，订单履约中，未超时且无超时风险，骑手不是无骑手接单时，ResponseSolution 应为“无”；只说明预计时间，不承诺一定准时。
3. ETA 或催促且无骑手接单/待接单/已推配送时，优先 ResponseSolution=加急调度，不要误用系统催单。
4. 用户明确催配送、配送慢、超时催促，且订单履约中可催时，ResponseSolution=系统催单；智能跟单只作为后续持续关注，不替代主动作。
5. 用户要联系骑手：骑手已接单/配送中时先引导自助联系骑手；用户明确要求客服帮忙联系或自助无效时，ResponseSolution=外呼骑手-催促配送。外呼/催促类不要求 DialogueAgreeSolution。
6. 最近外呼骑手未接通且用户持续追问，才可 ResponseSolution=再次外呼骑手-催促配送。
7. 用户要求取消且 can_cancel=true 时，ResponseSolution=取消订单；只有用户明确“取消吧/确认取消/不要了”等，DialogueAgreeSolution 才填“取消订单”。can_cancel=false 时禁止取消订单。
8. 用户因超时/配送慢要求赔付或强烈不满，且 can_compensate=true、未赔付过、金额在信号区间内，才可提出赔付；DialogueAgreeSolution 只有用户明确同意后才非空。已赔/不可赔禁止再次主动赔。
9. 已送达/已完成且用户只是确认状态、表示找到了或结束对话，ResponseSolution=无，不触发催单/加急。
10. ResponseSolution=无 仅在 ETA 普通咨询、解释状态、结束语、不可取消/不可赔的解释等情况下合理。"""


RQ_PROMPT = """【收货品质流程规则 v2】
适用：问题场景为“收货场景-品质问题”，仅用于离线 replay 校准，重点约束流程前置。
1. 先读信号：订单/商品是否超售后、已选择商品、商品退款状态、是否已收集图片凭证、退款原因、建议退款比例、实际退款数量、退款状态、是否可赔付、是否已赔付、赔付金额。
2. 超售后或商品不可退款时，不得选择小象单商品退款；ResponseSolution=无，解释不可退/政策原因，也不要错误引导重新选择商品。
3. 品质、日期、口感、实描等质量问题未选具体商品时，ResponseSolution=选择商品，DialogueAgreeSolution=无。
4. 已选商品但缺图片凭证时，ResponseSolution=无，no_action_reason=ask_upload_image；不得直接退款或赔付。
5. 已选商品且有图片，但缺退款原因，ResponseSolution=无，追问退款原因；缺建议退款比例时，ResponseSolution=无，追问/确认退款比例。
6. 多数量商品缺退款数量时，ResponseSolution=无，追问退款数量，不得默认数量。
7. 前置满足后，可提出小象单商品退款-xx%；用户尚未确认比例/金额时 DialogueAgreeSolution=无，用户明确同意后才填对应退款方案。
8. 退款进行中/审核中且用户问进度，首次可 ResponseSolution=催促退款审核;退审跟单，持续催促可用加急催促退款审核；不要求 DialogueAgreeSolution。
9. 已退款/退款完成时 ResponseSolution=无，只解释退款状态。
10. 用户要求赔付或强烈不满，且可赔、未赔、金额不超过上限时才可提出操作赔付-优惠券-xx元；用户明确同意后 DialogueAgreeSolution 才非空。已赔或不可赔禁止赔付。"""


def _count_scene(scene: str) -> int:
    return sum(1 for row in read_jsonl(get_case_records_path()) if row.get("scene") == scene)


def _sample_eval(replay_path: Path, out_path: Path, limit: int = 200) -> int:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for row in read_jsonl(replay_path):
        buckets.setdefault(row.get("gold_response_solution", "无"), []).append(
            {
                "sample_id": row.get("sample_id"),
                "scene": row.get("scene"),
                "signals": row.get("signals", {}),
                "last_user_query": row.get("last_user_query", ""),
                "dialogue_history": row.get("dialogue_history", ""),
                "response_solution": row.get("gold_response_solution"),
                "dialogue_agree_solution": row.get("gold_dialogue_agree_solution"),
                "no_action_reason": row.get("gold_no_action_reason", ""),
            }
        )
    rows: List[Dict[str, Any]] = []
    while len(rows) < limit and buckets:
        progressed = False
        for key in sorted(list(buckets)):
            if buckets[key]:
                rows.append(buckets[key].pop(0))
                progressed = True
                if len(rows) >= limit:
                    break
            else:
                buckets.pop(key, None)
        if not progressed:
            break
    return write_jsonl(out_path, rows)


def _write_pack(
    dirname: str,
    scene: str,
    skill_id: str,
    prompt: str,
    action_rules: List[Dict[str, Any]],
    no_action_rules: List[Dict[str, Any]],
    questions: List[str],
    replay_path: Path,
    online_recommendation: str,
) -> Dict[str, Any]:
    out_dir = V2_ROOT / "skills" / dirname
    out_dir.mkdir(parents=True, exist_ok=True)
    positive_cases = _count_scene(scene)
    skill = {
        "skill_id": skill_id,
        "scene": scene,
        "version": "v2.0-policy-replay-draft",
        "purpose": "约束流程动作，不优化话术",
        "entry_conditions": [f"问题场景 == {scene}"],
        "required_signals": [
            "订单状态",
            "是否为配送单",
            "订单骑手状态",
            "订单是否超时",
            "履约中未超时订单是否有超时风险",
            "是否可取消订单",
            "订单是否可赔付",
            "是否赔付过",
            "赔付金额",
            "商品退款状态",
            "是否已收集图片凭证",
            "建议退款比例",
        ],
        "solution_policy": {
            "strong_confirmation_required": ["取消订单", "小象单商品退款-xx%", "小象整单申请退款", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元"],
            "user_request_is_enough": ["外呼骑手-xx", "再次外呼骑手-xx", "催促退款审核", "加急催促退款审核"],
            "no_confirmation_required": ["系统催单", "加急调度", "智能跟单", "选择商品", "发送送达图片", "引导自助联系骑手"],
        },
        "action_rules": action_rules,
        "no_action_rules": no_action_rules,
        "confirmation_rules": [
            "取消、退款、赔付等 strong_confirmation_required 方案：ResponseSolution 可提出，DialogueAgreeSolution 只有用户明确同意后才非空。",
            "外呼/催促/催审类属于 user_request_is_enough，不要求 DialogueAgreeSolution 非空。",
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
            "不要把 available_solutions 当成当前都可执行",
            "不要把 DialogueAgreeSolution 简单复制 ResponseSolution",
        ],
        "evidence": {"positive_cases": positive_cases, "policy_rules": len(action_rules), "source": "trainer_goodcase + v2 eligibility"},
        "open_questions_for_trainer": questions,
    }
    (out_dir / "skill.json").write_text(json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "skill_prompt.md").write_text(prompt + "\n", encoding="utf-8")
    (out_dir / "checker_rules.md").write_text(
        "\n".join(
            [
                "# Checker Rules",
                "",
                "- strong confirmation 方案在 DialogueAgreeSolution 非空时必须有用户明确确认。",
                "- 不可取消/不可赔/已赔付/金额超上限直接拦截。",
                "- 品质场景未选商品、缺图片、缺原因、缺比例、缺数量时不得直接退款。",
                "- 配送场景 ETA 普通咨询不得被误判为必须催单；无骑手接单场景优先加急调度。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    eval_count = _sample_eval(replay_path, out_dir / "eval_cases.jsonl")
    (out_dir / "README.md").write_text(
        "\n".join(
            [
                f"# {skill_id}",
                "",
                f"- scene: `{scene}`",
                f"- positive_cases: `{positive_cases}`",
                f"- eval_cases: `{eval_count}`",
                f"- recommendation: {online_recommendation}",
                "",
                "## Open Questions",
                *[f"- {q}" for q in questions],
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {"skill_id": skill_id, "positive_cases": positive_cases, "eval_cases": eval_count, "action_rules": len(action_rules)}


def main() -> None:
    ensure_dirs()
    fd_action_rules = [
        {"rule_id": "FD-01", "when": "普通 ETA 咨询且无超时/无风险/非无骑手", "response_solution": "无", "no_action_reason": "eta_answer_only"},
        {"rule_id": "FD-02", "when": "ETA + 无骑手接单", "response_solution": "加急调度"},
        {"rule_id": "FD-03", "when": "明确催配送且系统催单 eligible", "response_solution": "系统催单"},
        {"rule_id": "FD-04", "when": "催配送但无骑手接单", "response_solution": "加急调度"},
        {"rule_id": "FD-05", "when": "用户要求联系骑手", "response_solution": "引导自助联系骑手/外呼骑手-催促配送"},
        {"rule_id": "FD-08", "when": "用户要求取消且可取消", "response_solution": "取消订单", "dialogue_agree_solution": "仅用户明确确认后非空"},
        {"rule_id": "FD-10", "when": "超时/配送慢且可赔未赔", "response_solution": "操作赔付-优惠券-xx元", "dialogue_agree_solution": "仅用户明确确认后非空"},
    ]
    rq_action_rules = [
        {"rule_id": "RQ-01", "when": "超售后或不可退款", "response_solution": "无", "no_action_reason": "explain_cannot_refund/policy_explain"},
        {"rule_id": "RQ-02", "when": "质量问题未选商品", "response_solution": "选择商品"},
        {"rule_id": "RQ-03", "when": "已选商品但缺图片", "response_solution": "无", "no_action_reason": "ask_upload_image"},
        {"rule_id": "RQ-04", "when": "缺退款原因", "response_solution": "无", "no_action_reason": "ask_refund_reason"},
        {"rule_id": "RQ-05", "when": "缺退款比例", "response_solution": "无", "no_action_reason": "ask_refund_ratio"},
        {"rule_id": "RQ-07/RQ-08", "when": "退款前置满足", "response_solution": "小象单商品退款-xx%", "dialogue_agree_solution": "仅用户明确确认后非空"},
        {"rule_id": "RQ-09", "when": "退款进行中且用户催进度", "response_solution": "催促退款审核;退审跟单/加急催促退款审核"},
        {"rule_id": "RQ-11", "when": "强烈不满且可赔未赔", "response_solution": "操作赔付-优惠券-xx元", "dialogue_agree_solution": "仅用户明确确认后非空"},
    ]
    packs = [
        _write_pack(
            "fulfillment_delivery_policy_v2",
            "履约场景-配送问题",
            "fulfillment_delivery_policy_v2",
            FD_PROMPT,
            fd_action_rules,
            [{"reason": "eta_answer_only"}, {"reason": "explain_status"}, {"reason": "close_conversation"}, {"reason": "unavailable_capability"}],
            FD_QUESTIONS,
            V2_ROOT.parent / "flow_skill_mining_v1" / "replay" / "fulfillment_delivery_replay.jsonl",
            "允许进入 baseline vs skill 模型 replay。",
        ),
        _write_pack(
            "receipt_quality_policy_v2",
            "收货场景-品质问题",
            "receipt_quality_policy_v2",
            RQ_PROMPT,
            rq_action_rules,
            [{"reason": "ask_upload_image"}, {"reason": "ask_refund_reason"}, {"reason": "ask_refund_ratio"}, {"reason": "explain_refund_status"}],
            RQ_QUESTIONS,
            V2_ROOT.parent / "flow_skill_mining_v1" / "replay" / "receipt_quality_replay.jsonl",
            "仅建议 offline replay 和训练师校准，暂不建议线上。",
        ),
    ]
    (V2_ROOT / "outputs" / "reports" / "policy_skill_report.md").write_text(
        "# Policy Skill Report\n\n" + "\n".join(f"- `{p['skill_id']}` action_rules=`{p['action_rules']}` eval_cases=`{p['eval_cases']}` positive_cases=`{p['positive_cases']}`" for p in packs) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
