#!/usr/bin/env python3
"""Build the top-level v2 report."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_policy_v2.common import V2_REPORTS, V2_ROOT, ensure_dirs, read_jsonl, top_counter


def _report_number(path: Path, key: str) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"{re.escape(key)}:\s*`?(\d+)`?", text)
    return int(match.group(1)) if match else 0


def main() -> None:
    ensure_dirs()
    fd_rows = list(read_jsonl(V2_ROOT / "replay" / "fulfillment_delivery_oracle.jsonl"))
    rq_rows = list(read_jsonl(V2_ROOT / "replay" / "receipt_quality_oracle.jsonl"))
    all_rows = fd_rows + rq_rows
    relation_counts = Counter(row.get("gold_oracle_relation") for row in all_rows)
    conflict_rules = Counter(row.get("oracle_rule_id") for row in all_rows if row.get("needs_trainer_review"))
    fd_prompt = V2_ROOT / "replay" / "fulfillment_delivery_skill_inputs.jsonl"
    rq_prompt = V2_ROOT / "replay" / "receipt_quality_skill_inputs.jsonl"
    r12_eligible = _report_number(V2_REPORTS / "eligibility_engine_report.md", "v1_R12_with_eligible_action")
    r12_total = _report_number(V2_REPORTS / "eligibility_engine_report.md", "v1_R12_cases")

    lines = [
        "# Flow Skill Policy v2 Report",
        "",
        "## 1. 为什么 v2 引入 eligibility engine",
        "v1 的主要问题是把 prompt 中的 available_solutions 当成当前都可执行。v2 增加 eligibility engine，把候选方案先过信号、用户诉求和流程前置 guard，再给 policy / checker / replay 使用。",
        "",
        "## 2. available_solutions vs eligible_solutions",
        "- available_solutions: prompt 中列出的候选工具/方案集合，表示模型知道这些方案存在。",
        "- eligible_solutions: 在当前订单状态、骑手状态、退款/赔付/取消/图片/商品选择等信号下真正可执行的方案。",
        "- 因此 R12 漏操作不能只看 available；必须看是否 eligible。",
        "",
        "## 3. fulfillment_delivery_v2 新增显式流程规则",
        "- FD-01 普通 ETA 咨询允许 ResponseSolution=无。",
        "- FD-02/FD-04 无骑手接单时优先加急调度。",
        "- FD-03 明确催配送时使用系统催单。",
        "- FD-05/FD-06 联系骑手和再次外呼分开处理。",
        "- FD-08/FD-09 取消订单必须受 can_cancel 和用户确认约束。",
        "- FD-10/FD-11 配送赔付必须受可赔、已赔、金额上限和用户确认约束。",
        "",
        "## 4. receipt_quality_v2 新增显式流程规则",
        "- RQ-01 超售后/不可退款先拦截。",
        "- RQ-02 未选商品先选择商品。",
        "- RQ-03/RQ-04/RQ-05/RQ-06 图片、原因、比例、数量作为退款前置 guard。",
        "- RQ-07/RQ-08 区分提出退款和用户已确认退款。",
        "- RQ-09 退款进度使用催审/跟单，不要求 DialogueAgreeSolution。",
        "- RQ-11/RQ-12 赔付受可赔、已赔、金额上限和确认约束。",
        "",
        "## 5. v1 R12 eligibility 后仍疑似漏操作",
        f"- v1_R12_cases: `{r12_total}`",
        f"- v1_R12_with_eligible_action: `{r12_eligible}`",
        "这些样本更值得训练师看；剩余多数只是 available 里有方案，但当前信号不满足执行条件。",
        "",
        "## 6. Gold 与 Oracle 冲突最多的规则",
        top_counter(conflict_rules, 20) or "- none",
        "",
        "## 7. 需要训练师确认",
        "- 普通 ETA + 无骑手接单是否一定加急调度。",
        "- 系统催单与智能跟单是否可以同轮复合输出。",
        "- 品质问题缺图片/原因/比例时是否允许先提出退款。",
        "- 赔付档位如何从信号区间、问题严重度和用户分层中选择。",
        "- 外呼骑手是先自助联系还是客服直接外呼。",
        "",
        "## 8. fulfillment_delivery_policy_v2 是否可 replay",
        "建议可以进入 baseline vs skill replay。原因是配送 v2 规则明确区分 ETA、催单、无骑手、联系骑手、取消、赔付，能针对 v1 只有 1 条 action_rule 的短板做离线对比。",
        "",
        "## 9. receipt_quality_policy_v2 是否只建议离线校准",
        "仍建议先离线校准。品质场景的图片、退款原因、比例、数量等前置 guard 很强，gold/oracle 冲突可能包含标注口径差异，需要训练师先确认。",
        "",
        "## 10. 下一步如何跑模型 replay",
        f"- baseline 输入: `{fd_prompt.parent / 'fulfillment_delivery_baseline_inputs.jsonl'}` / `{rq_prompt.parent / 'receipt_quality_baseline_inputs.jsonl'}`",
        f"- skill 输入: `{fd_prompt}` / `{rq_prompt}`",
        "- 分别调用同一个模型得到 model_outputs.jsonl，再用 `flow_skill_policy_v2/replay/evaluate_replay_outputs_v2.py` 对比 gold 与 oracle 指标。",
        "",
        "## Key Metrics",
        f"- fulfillment_delivery_oracle_cases: `{len(fd_rows)}`",
        f"- receipt_quality_oracle_cases: `{len(rq_rows)}`",
        f"- gold_oracle_same_or_canonical: `{relation_counts.get('same', 0) + relation_counts.get('canonical_same', 0)}`",
        f"- gold_oracle_conflict: `{sum(v for k, v in relation_counts.items() if k not in {'same', 'canonical_same'})}`",
    ]
    (V2_ROOT / "README_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
