#!/usr/bin/env python3
"""Build v21 trainer review pack."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_policy_v21.common import V2_ROOT, V21_OUT, V21_ROOT, ensure_dirs, mask_text, read_jsonl


def _rows(path: Path) -> List[Dict[str, Any]]:
    return list(read_jsonl(path)) if path.exists() else []


def _write(path: Path, rows: List[Dict[str, Any]], title: str, limit: int = 50) -> int:
    subset = rows[:limit]
    lines = [f"# {title}", "", "训练师选项：A. gold 正确，oracle 过严；B. oracle 正确；C. 两者都可接受；D. 需要补充信号/流程。", ""]
    for i, row in enumerate(subset, 1):
        lines.extend(
            [
                f"## {i}. {row.get('sample_id')}",
                f"- scene: `{row.get('scene')}`",
                f"- last_user_query: {mask_text(row.get('last_user_query', ''))}",
                f"- current_turn_intent: `{row.get('current_turn_intent', {}).get('current_intents')}`",
                f"- gold ResponseSolution: `{row.get('gold_response_solution')}`",
                f"- oracle ResponseSolution: `{row.get('oracle_response_solution')}`",
                f"- oracle rule: `{row.get('oracle_rule_id')}`",
                f"- rationale: {'; '.join(row.get('rationale') or [])}",
                "- 训练师选择: A / B / C / D",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return len(subset)


def main() -> None:
    ensure_dirs()
    out = V21_OUT / "trainer_review_pack"
    out.mkdir(parents=True, exist_ok=True)
    fd_v2 = {r["sample_id"]: r for r in _rows(V2_ROOT / "replay" / "fulfillment_delivery_oracle.jsonl")}
    rq_v2 = {r["sample_id"]: r for r in _rows(V2_ROOT / "replay" / "receipt_quality_oracle.jsonl")}
    fd = _rows(V21_ROOT / "replay" / "fulfillment_delivery_oracle_v21.jsonl")
    rq = _rows(V21_ROOT / "replay" / "receipt_quality_oracle_v21.jsonl")
    fixed = []
    close_ack_fixed = []
    rq01_fixed = []
    for row in fd + rq:
        old = (fd_v2 | rq_v2).get(row["sample_id"])
        if not old:
            continue
        old_conf = old.get("gold_oracle_relation") not in {"same", "canonical_same"}
        new_conf = row.get("gold_oracle_relation") not in {"same", "canonical_same"}
        if old_conf and not new_conf:
            fixed.append(row)
        cur = row.get("current_turn_intent") or {}
        if old.get("oracle_response_solution") != "无" and row.get("oracle_response_solution") == "无" and (cur.get("is_close_or_thanks") or cur.get("is_ack_only") or cur.get("is_transfer_only")):
            close_ack_fixed.append(row)
        if old.get("oracle_rule_id") == "RQ-01" and row.get("oracle_rule_id") == "RQ-02":
            rq01_fixed.append(row)
    fd_conf = [r for r in fd if r.get("gold_oracle_relation") not in {"same", "canonical_same"}]
    rq_conf = [r for r in rq if r.get("gold_oracle_relation") not in {"same", "canonical_same"}]
    n_fd = _write(out / "fulfillment_delivery_conflicts_v21_sample.md", fd_conf, "Fulfillment Delivery v21 Remaining Conflicts")
    n_rq = _write(out / "receipt_quality_conflicts_v21_sample.md", rq_conf, "Receipt Quality v21 Remaining Conflicts")
    _write(out / "v2_fixed_sample.md", fixed, "V2 Conflicts Fixed By v21", 40)
    _write(out / "close_ack_fixed_sample.md", close_ack_fixed, "Close/Ack Over-action Fixed", 40)
    _write(out / "rq01_fixed_sample.md", rq01_fixed, "RQ-01 Guard Changed Back To Select Product", 40)
    (out / "current_turn_gating_questions.md").write_text(
        "# Current Turn Gating Questions\n\n- 是否同意动作只能由当前最后一条用户消息触发？\n- “嗯/好/可以”是否只在 pending strong solution 存在时才确认执行？\n- close/thanks 后是否一律 ResponseSolution=无？\n",
        encoding="utf-8",
    )
    (out / "policy_questions_v21.md").write_text(
        f"# Policy Questions v21\n\n- FD remaining conflicts sampled: `{n_fd}`\n- RQ remaining conflicts sampled: `{n_rq}`\n- v2 fixed sample count: `{len(fixed[:40])}`\n- close/ack fixed sample count: `{len(close_ack_fixed[:40])}`\n- rq01 fixed sample count: `{len(rq01_fixed[:40])}`\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
