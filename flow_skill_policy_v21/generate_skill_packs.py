#!/usr/bin/env python3
"""Generate v21 policy skill packs."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_policy_v21.common import V21_ROOT, ensure_dirs, read_jsonl, write_jsonl


FD_PROMPT = """【履约配送流程规则 v21】
只有当前最后一条用户消息仍表达对应诉求时，才触发动作；如果用户当前只是感谢、结束语、弱确认且没有待确认方案，ResponseSolution 应为“无”。
1. 先读信号：订单状态、是否配送单、骑手状态、是否超时/有超时风险、是否可取消、是否可赔付、是否已赔付、赔付金额、骑手手机号。
2. 当前用户只是问 ETA，订单履约中，未超时且无超时风险，骑手不是无骑手/待接单：ResponseSolution=无，只告知预计时间，不承诺一定准时。
3. 当前用户询问 ETA / 催接单 / 催配送，且骑手无接单、创建履约单、已推配送或待接单时，优先 ResponseSolution=加急调度。
4. 当前明确催配送，或 ETA 咨询同时存在超时/超时风险，且系统催单可执行：ResponseSolution=系统催单。
5. 当前用户想联系骑手且骑手已接单/配送中：未明确要求客服外呼时优先引导自助联系骑手；明确“帮我问骑手/客服帮忙打电话”时可外呼骑手。外呼类不要求 DialogueAgreeSolution。
6. 当前要求取消且可取消：ResponseSolution=取消订单，DialogueAgreeSolution 仍为“无”；只有存在上一轮待确认取消且当前明确同意时，DialogueAgreeSolution=取消订单。不可取消时禁止取消订单。
7. 当前要求赔付/强烈不满且可赔、未赔、金额在区间内时，才可提出赔付；first_offer 取信号区间下限。只有 pending 赔付方案被当前确认时，DialogueAgreeSolution 才非空。
8. 上一轮已催单/加急/外呼后，当前仍说“继续帮我盯着/还没到/别忘了”才可智能跟单；当前结束语不跟单。
9. ResponseSolution=无 的合理原因：普通 ETA、感谢/结束语、弱确认无 pending、只转人工无具体诉求、状态解释、不可取消/不可赔的解释。"""


RQ_PROMPT = """【收货品质流程规则 v21】
只有当前最后一条用户消息仍表达对应诉求时，才触发动作；如果用户当前只是感谢、结束语、弱确认且没有待确认方案，ResponseSolution 应为“无”。
1. 先读信号：是否已选商品、商品退款状态、订单是否超售后、图片凭证、退款原因、退款比例、退款数量、退款状态、是否可赔、是否已赔、赔付金额。
2. 未选商品时，不要用聚合商品退款状态判断不可退；当前仍有品质/退款诉求且未选商品，ResponseSolution=选择商品。
3. 只有订单明确超售后，或已选商品明确不可退，才进入不可退款 guard；此时 ResponseSolution=无，解释政策/不可退原因。
4. 当前仍在推进品质退款且已选商品但缺图片：ResponseSolution=无，要求上传图片；缺退款原因则追问原因；缺退款比例则追问/确认比例；多数量缺退款数量则追问数量。
5. 退款进行中/审核中/银行处理中，且当前明确问退款进度或催退款时，才输出催促退款审核;退审跟单；普通质量描述、结束语、弱确认不触发催审。
6. 前置满足且当前仍有退款/品质诉求，可提出小象单商品退款-xx%；未确认前 DialogueAgreeSolution=无。只有 pending 退款方案被当前明确同意时，DialogueAgreeSolution 才填退款方案。
7. 当前要求赔付/强烈不满，且可赔、未赔、金额不超过上限时才可提出赔付；first_offer 取信号区间下限。只有 pending 赔付被当前确认时 DialogueAgreeSolution 才非空。
8. 已赔或不可赔时禁止赔付。ResponseSolution=无 的合理原因：结束语、弱确认无 pending、转人工无具体诉求、缺图片/原因/比例/数量、退款已完成解释、不可退政策解释。"""


def _sample_eval(oracle_path: Path, out_path: Path, limit: int = 200) -> int:
    rows = list(read_jsonl(oracle_path)) if oracle_path.exists() else []
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row.get("gold_response_solution", "无"), []).append(
            {
                "sample_id": row.get("sample_id"),
                "scene": row.get("scene"),
                "last_user_query": row.get("last_user_query", ""),
                "gold_response_solution": row.get("gold_response_solution"),
                "oracle_response_solution": row.get("oracle_response_solution"),
                "gold_dialogue_agree_solution": row.get("gold_dialogue_agree_solution"),
                "oracle_dialogue_agree_solution": row.get("oracle_dialogue_agree_solution"),
                "oracle_rule_id": row.get("oracle_rule_id"),
                "current_turn_intent": row.get("current_turn_intent"),
            }
        )
    out = []
    while len(out) < limit and groups:
        progressed = False
        for key in sorted(list(groups)):
            if groups[key]:
                out.append(groups[key].pop(0))
                progressed = True
                if len(out) >= limit:
                    break
            else:
                groups.pop(key, None)
        if not progressed:
            break
    return write_jsonl(out_path, out)


def _write_pack(dirname: str, scene: str, skill_id: str, prompt: str, oracle: Path, online: str) -> None:
    out_dir = V21_ROOT / "skills" / dirname
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = list(read_jsonl(oracle)) if oracle.exists() else []
    rule_counts = Counter(r.get("oracle_rule_id") for r in rows)
    skill = {
        "skill_id": skill_id,
        "scene": scene,
        "version": "v2.1-current-turn-gated",
        "purpose": "约束流程动作，不优化话术",
        "entry_conditions": [f"问题场景 == {scene}"],
        "current_turn_gating": "只有当前最后一条用户消息仍表达对应诉求时才触发动作；感谢/结束/弱确认无 pending 时 ResponseSolution=无。",
        "solution_policy": {
            "strong_confirmation_required": ["取消订单", "小象单商品退款-xx%", "小象整单申请退款", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元", "会员卡退款"],
            "user_request_is_enough": ["外呼骑手-xx", "再次外呼骑手-xx", "催促退款审核", "加急催促退款审核"],
            "no_confirmation_required": ["系统催单", "加急调度", "智能跟单", "选择商品", "发送送达图片", "引导自助联系骑手"],
        },
        "action_rules": [{"rule_id": k, "support_in_oracle": v} for k, v in rule_counts.items() if k and not str(k).endswith(("CLOSE", "ACK"))],
        "guard_rules": ["不可赔付不得赔付", "已赔付不得再次主动赔", "不可取消不得取消", "未选商品不得单商品退款", "强确认方案必须有 pending + 当前确认才填 DialogueAgreeSolution"],
        "evidence": {"oracle_cases": len(rows), "stable_same_or_canonical": sum(1 for r in rows if r.get("gold_oracle_relation") in {"same", "canonical_same"})},
        "open_questions_for_trainer": [
            "current-turn gating 是否过严，是否会漏掉用户简短追问？",
            "first_offer 取赔付区间下限是否符合训练师口径？",
            "弱确认词是否只在 pending strong solution 时才执行？",
        ],
    }
    (out_dir / "skill.json").write_text(json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "skill_prompt.md").write_text(prompt + "\n", encoding="utf-8")
    (out_dir / "checker_rules.md").write_text(
        "# Checker Rules v21\n\n- close/thanks/ack-only/transfer-only 无 pending strong solution 时不得输出动作。\n- strong confirmation 方案的 DialogueAgreeSolution 必须有 pending strong solution + 当前确认。\n- 所有动作必须由当前最后一条用户消息触发，不得由历史关键词单独触发。\n",
        encoding="utf-8",
    )
    n = _sample_eval(oracle, out_dir / "eval_cases.jsonl")
    (out_dir / "README.md").write_text(f"# {skill_id}\n\n- scene: `{scene}`\n- oracle_cases: `{len(rows)}`\n- eval_cases: `{n}`\n- recommendation: {online}\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    _write_pack("fulfillment_delivery_policy_v21", "履约场景-配送问题", "fulfillment_delivery_policy_v21", FD_PROMPT, V21_ROOT / "replay" / "fulfillment_delivery_oracle_v21.jsonl", "建议进入模型 replay。")
    _write_pack("receipt_quality_policy_v21", "收货场景-品质问题", "receipt_quality_policy_v21", RQ_PROMPT, V21_ROOT / "replay" / "receipt_quality_oracle_v21.jsonl", "建议先离线 replay + 训练师校准。")


if __name__ == "__main__":
    main()
