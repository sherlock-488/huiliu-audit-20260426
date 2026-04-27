#!/usr/bin/env python3
"""Create trainer-facing samples for v2 policy calibration."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_policy_v2.common import V2_OUT, V2_ROOT, ensure_dirs, mask_text, read_jsonl


KEY_SIGNAL_NAMES = [
    "订单状态",
    "是否为配送单",
    "订单骑手状态",
    "订单是否超时",
    "履约中未超时订单是否有超时风险",
    "是否可取消订单",
    "订单是否可赔付",
    "是否赔付过",
    "赔付金额",
    "订单退款状态",
    "订单是否超售后",
    "商品退款状态",
    "是否已收集图片凭证",
    "建议退款比例",
]


def _key_signals(signals: Dict[str, Any]) -> str:
    pairs = []
    for key in KEY_SIGNAL_NAMES:
        if key in signals and signals.get(key) not in (None, ""):
            pairs.append(f"{key}={signals.get(key)}")
    if not pairs:
        for key, value in list(signals.items())[:8]:
            pairs.append(f"{key}={value}")
    return "; ".join(pairs)


def _write_conflicts(path: Path, rows: List[Dict[str, Any]], title: str) -> int:
    conflicts = [row for row in rows if row.get("needs_trainer_review")][:50]
    lines = [
        f"# {title}",
        "",
        "请对每条样本选择：A. gold 正确，oracle 过严/过度执行；B. oracle 正确，训练标注漏流程；C. 两者都可接受；D. 需要补充信号/流程。",
        "",
    ]
    for i, row in enumerate(conflicts, 1):
        lines.extend(
            [
                f"## {i}. {row.get('sample_id')}",
                f"- scene: `{row.get('scene')}`",
                f"- last_user_query: {mask_text(row.get('last_user_query', ''))}",
                f"- key_signals: {mask_text(_key_signals(row.get('signals') or {}))}",
                f"- gold ResponseSolution: `{row.get('gold_response_solution')}`",
                f"- oracle ResponseSolution: `{row.get('oracle_response_solution')}`",
                f"- oracle rule: `{row.get('oracle_rule_id')}`",
                f"- 差异原因: {'; '.join(row.get('rationale') or [])}",
                "- 训练师选择: A / B / C / D",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return len(conflicts)


def main() -> None:
    ensure_dirs()
    out_dir = V2_OUT / "trainer_review_pack"
    out_dir.mkdir(parents=True, exist_ok=True)
    fd_rows = list(read_jsonl(V2_ROOT / "replay" / "fulfillment_delivery_oracle.jsonl"))
    rq_rows = list(read_jsonl(V2_ROOT / "replay" / "receipt_quality_oracle.jsonl"))
    fd_n = _write_conflicts(out_dir / "fulfillment_delivery_conflicts_sample.md", fd_rows, "履约配送 Policy 冲突样本")
    rq_n = _write_conflicts(out_dir / "receipt_quality_conflicts_sample.md", rq_rows, "收货品质 Policy 冲突样本")

    (out_dir / "confirmation_questions.md").write_text(
        "\n".join(
            [
                "# Confirmation Questions",
                "",
                "1. 取消订单、单商品退款、整单退款、赔付是否都必须在用户明确同意后才允许 DialogueAgreeSolution 非空？",
                "2. 外呼骑手、再次外呼骑手、催促退款审核、加急催促退款审核是否属于 user_request_is_enough，不强制 DialogueAgreeSolution？",
                "3. 用户说“帮我处理/给我退/那就这样”是否都可视为强确认？",
                "4. 如果客服上一轮提出赔付，本轮用户只说“嗯”，是否足够写 DialogueAgreeSolution？",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    rule_counts = Counter(row.get("oracle_rule_id") for row in fd_rows + rq_rows if row.get("needs_trainer_review"))
    (out_dir / "policy_questions.md").write_text(
        "\n".join(
            [
                "# Policy Questions",
                "",
                f"- fulfillment_delivery sampled conflicts: `{fd_n}`",
                f"- receipt_quality sampled conflicts: `{rq_n}`",
                "",
                "## 冲突最多的 oracle rules",
                *[f"- `{k}`: `{v}`" for k, v in rule_counts.most_common(20)],
                "",
                "## 需要优先确认",
                "- 配送普通 ETA 与无骑手接单同时出现时，是否总是加急调度。",
                "- 品质场景缺图片/原因/比例时，是否允许先提出退款比例，还是必须追问。",
                "- 赔付档位取信号上限还是根据用户分层/问题严重程度决定。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (V2_OUT / "reports" / "trainer_review_pack_report.md").write_text(
        f"# Trainer Review Pack Report\n\n- fulfillment_delivery_conflicts_sample: `{fd_n}`\n- receipt_quality_conflicts_sample: `{rq_n}`\n- output_dir: `{out_dir}`\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
