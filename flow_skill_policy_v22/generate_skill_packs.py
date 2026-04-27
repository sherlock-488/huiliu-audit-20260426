#!/usr/bin/env python3
"""Generate v22 skill packs."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_policy_v22.common import V22_ROOT, ensure_dirs, read_jsonl, write_jsonl


FD_PROMPT = """【履约配送流程规则 v22】
只根据当前最后一条用户消息触发动作；如果当前只是感谢、结束语、弱确认且没有待确认方案，ResponseSolution=无。
1. 短句追问也算当前诉求：“急、快点、怎么还没配送、还没送到、还得等到啥时候、5分钟？”在履约配送场景下视为继续催促或 ETA 追问。
2. 当前询问 ETA 且未超时、无风险、骑手不是无接单：ResponseSolution=无，只说明预计时间，不承诺准时。
3. 当前询问 ETA/催接单/催配送，且骑手无接单、创建履约单、已推配送或待接单：优先加急调度。
4. 当前明确催配送，或 ETA 咨询同时有超时/超时风险：系统催单 eligible 时输出系统催单。
5. 用户想联系骑手：问“怎么联系骑手”优先引导自助联系骑手；“帮我问骑手/你帮我联系/打电话给骑手”可外呼骑手；若上一轮已外呼/催单/加急且当前问“问骑手了吗/5分钟/还没到”，可智能跟单或按未接通结果再次外呼。
6. 取消订单必须当前要求取消且可取消；DialogueAgreeSolution=取消订单只在 pending 取消方案 + 当前纯确认时填写。
7. “投诉骑手”不是自动赔付；赔付必须有明确赔付/补偿/优惠券诉求，且信号可赔、未赔、金额不超上限。first_offer 取赔付区间下限。
8. 智能跟单只在上一轮已推进且当前仍要求继续关注时使用；“好谢谢/没有了”不跟单。
9. “嗯/好/可以”如果伴随“什么时候/多久/到账/还没/怎么/太少/不接受”等追问或拒绝，不算确认执行。"""


RQ_PROMPT = """【收货品质流程规则 v22】
只根据当前最后一条用户消息触发动作；感谢、结束语、弱确认且无待确认方案时 ResponseSolution=无。
1. 品质短句也是有效质量诉求：漏的、漏液、空心、碎的、坏得、干瘪、发臭、不能吃、发软、发黑、有泥、死了、不新鲜、临期、包装破等。
2. 未选商品时，不用聚合商品状态判断不可退；当前有品质/退款诉求且未选商品，先 ResponseSolution=选择商品。
3. 图片上传或图片识别结果可作为当前轮证据；若已选商品且图片、原因、比例、数量满足，可继续推进退款；未选商品但图片/文本能匹配商品名，可临时视为本轮已选，否则仍先选择商品。
4. 只有订单明确超售后，或已选商品明确不可退，才进入不可退款 guard；未选商品优先选择商品。
5. 已选商品但缺图片、退款原因、退款比例或多件商品退款数量时，ResponseSolution=无，并追问对应信息。
6. “都不能吃了就给这么少吗/至少退50/退一半/给我退”识别为退款或拒绝当前比例，应继续退款流程，不要 oracle=无。
7. “嗯，什么时候退完给我啊”是退款进度咨询，不是确认退款；只有纯确认且存在 pending 退款/赔付/取消方案时，DialogueAgreeSolution 才非空。
8. 退款进行中/客服审核/银行处理中且当前问进度，才输出催促退款审核;退审跟单；普通质量描述或结束语不触发催审。
9. 赔付必须有明确赔付/补偿/优惠券诉求且信号可赔、未赔，first_offer 取区间下限。"""


def _rows(path: Path) -> List[Dict[str, Any]]:
    return list(read_jsonl(path)) if path.exists() else []


def _eval(rows: List[Dict[str, Any]], out: Path) -> int:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        groups.setdefault(r.get("gold_response_solution", "无"), []).append({k: r.get(k) for k in ["sample_id", "scene", "last_user_query", "gold_response_solution", "oracle_response_solution", "gold_dialogue_agree_solution", "oracle_dialogue_agree_solution", "oracle_rule_id", "current_turn_intent"]})
    out_rows = []
    while len(out_rows) < 200 and groups:
        progressed = False
        for k in sorted(list(groups)):
            if groups[k]:
                out_rows.append(groups[k].pop(0))
                progressed = True
                if len(out_rows) >= 200:
                    break
            else:
                groups.pop(k, None)
        if not progressed:
            break
    return write_jsonl(out, out_rows)


def _pack(dirname: str, scene: str, skill_id: str, prompt: str, oracle: Path, recommendation: str) -> None:
    rows = _rows(oracle)
    out = V22_ROOT / "skills" / dirname
    out.mkdir(parents=True, exist_ok=True)
    rules = Counter(r.get("oracle_rule_id") for r in rows)
    skill = {
        "skill_id": skill_id,
        "scene": scene,
        "version": "v2.2-intent-recall",
        "purpose": "约束流程动作，不优化话术",
        "current_turn_gating": "只看当前最后一条用户消息触发动作；短句追问可结合安全上下文增强；历史不得单独触发动作。",
        "solution_policy": {
            "strong_confirmation_required": ["取消订单", "小象单商品退款-xx%", "小象整单申请退款", "操作赔付-优惠券-xx元", "操作赔付-运费券-3元", "会员卡退款"],
            "user_request_is_enough": ["外呼骑手-xx", "再次外呼骑手-xx", "催促退款审核", "加急催促退款审核"],
            "no_confirmation_required": ["系统催单", "加急调度", "智能跟单", "选择商品", "引导自助联系骑手"],
        },
        "action_rules": [{"rule_id": k, "support_in_oracle": v} for k, v in rules.items()],
        "guard_rules": ["close/thanks/ack-only 无 pending 时不动作", "强确认必须 pure_confirm/maybe_accept + pending", "投诉骑手不自动赔付", "未选商品不做不可退聚合判断"],
        "evidence": {"oracle_cases": len(rows), "stable_same_or_canonical": sum(1 for r in rows if r.get("gold_oracle_relation") in {"same", "canonical_same"})},
        "open_questions_for_trainer": ["短句追问召回是否过宽", "maybe_accept_pending 是否应视为确认", "赔付 first_offer 取下限是否符合口径"],
    }
    (out / "skill.json").write_text(json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "skill_prompt.md").write_text(prompt + "\n", encoding="utf-8")
    (out / "checker_rules.md").write_text("# Checker Rules v22\n\n- 当前无新诉求不得因历史关键词输出动作。\n- 纯确认必须结合 pending strong solution。\n- action-focused replay 单独看动作召回。\n", encoding="utf-8")
    n = _eval(rows, out / "eval_cases.jsonl")
    (out / "README.md").write_text(f"# {skill_id}\n\n- scene: `{scene}`\n- oracle_cases: `{len(rows)}`\n- eval_cases: `{n}`\n- recommendation: {recommendation}\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    _pack("fulfillment_delivery_policy_v22", "履约场景-配送问题", "fulfillment_delivery_policy_v22", FD_PROMPT, V22_ROOT / "replay" / "fulfillment_delivery_oracle_v22.jsonl", "建议进入正式模型 replay。")
    _pack("receipt_quality_policy_v22", "收货场景-品质问题", "receipt_quality_policy_v22", RQ_PROMPT, V22_ROOT / "replay" / "receipt_quality_oracle_v22.jsonl", "建议离线 replay + 训练师校准。")


if __name__ == "__main__":
    main()
