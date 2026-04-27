#!/usr/bin/env python3
"""Evaluate one fulfillment-delivery replay model output file."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from flow_skill_policy_v22.common import canonical_components, relation  # noqa: E402
from output_parser import parse_model_output_row  # noqa: E402


STRONG_CONFIRMATION = {
    "取消订单",
    "小象单商品退款-xx%",
    "小象整单申请退款",
    "操作赔付-优惠券-xx元",
    "操作赔付-运费券-3元",
    "会员卡退款",
}
CLOSE_ACK_TERMS = ["没有了", "没了", "不用了", "谢谢", "好的谢谢", "没事了", "嗯嗯", "好的"]


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def split_raw(raw: Any) -> List[str]:
    text = "" if raw is None else str(raw).strip()
    if not text or text == "无":
        return []
    out = []
    for piece in re.split(r"[;；]", text):
        piece = piece.strip()
        if piece:
            out.append(piece)
    return out


def exact_match(pred: Any, target: Any) -> bool:
    return split_raw(pred) == split_raw(target)


def canonical_match(pred: Any, target: Any) -> bool:
    return relation(str(pred or "无"), str(target or "无")) in {"same", "canonical_same"}


def canonical_set(value: Any) -> set[str]:
    return set(canonical_components(value or "无"))


def is_action(value: Any) -> bool:
    return bool(split_raw(value))


def is_strong(value: Any) -> bool:
    return bool(canonical_set(value) & STRONG_CONFIRMATION)


def corresponding_strong(pred: Any, gold: Any, oracle: Any) -> bool:
    pred_s = canonical_set(pred) & STRONG_CONFIRMATION
    expected = (canonical_set(gold) | canonical_set(oracle)) & STRONG_CONFIRMATION
    return bool(pred_s and pred_s & expected)


def rate(num: int, den: int) -> float:
    return 0.0 if den <= 0 else num / den


def close_ack_query(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text or "")
    return any(term in normalized for term in CLOSE_ACK_TERMS)


def enrich_row(raw: Dict[str, Any]) -> Dict[str, Any]:
    parsed = parse_model_output_row(raw)
    return {**raw, **parsed}


def evaluate(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Counter], Dict[str, Counter], List[Dict[str, Any]]]:
    counters: Dict[str, Counter] = defaultdict(Counter)
    buckets: Dict[str, Counter] = defaultdict(Counter)
    results = []
    for raw in rows:
        row = enrich_row(raw)
        set_type = row.get("set_type", "")
        pred = row.get("ResponseSolution", "无")
        agree = row.get("DialogueAgreeSolution", "无")
        gold = row.get("gold_response_solution", "无")
        oracle = row.get("oracle_response_solution", "无")
        gold_agree = row.get("gold_dialogue_agree_solution", "无")
        oracle_agree = row.get("oracle_dialogue_agree_solution", "无")
        pred_action = is_action(pred)
        gold_action = is_action(gold)
        oracle_action = is_action(oracle)
        gold_exact = exact_match(pred, gold)
        oracle_exact = exact_match(pred, oracle)
        gold_canon = canonical_match(pred, gold)
        oracle_canon = canonical_match(pred, oracle)
        gold_oracle_no_action = not gold_action and not oracle_action
        close_ack_over = close_ack_query(row.get("last_user_query", "")) and gold_oracle_no_action and pred_action
        strong_over = is_strong(agree) and not corresponding_strong(agree, gold_agree, oracle_agree)
        result = {
            "sample_id": row.get("sample_id"),
            "set_type": set_type,
            "mode": row.get("mode", ""),
            "oracle_rule_id": row.get("oracle_rule_id", ""),
            "last_user_query": row.get("last_user_query", ""),
            "gold_response_solution": gold,
            "oracle_response_solution": oracle,
            "pred_response_solution": pred,
            "gold_dialogue_agree_solution": gold_agree,
            "oracle_dialogue_agree_solution": oracle_agree,
            "pred_dialogue_agree_solution": agree,
            "parse_error": row.get("parse_error", ""),
            "gold_exact_match": gold_exact,
            "gold_canonical_match": gold_canon,
            "oracle_exact_match": oracle_exact,
            "oracle_canonical_match": oracle_canon,
            "pred_action": pred_action,
            "gold_action": gold_action,
            "oracle_action": oracle_action,
            "over_action": gold_oracle_no_action and pred_action,
            "missing_gold": gold_action and not pred_action,
            "missing_oracle": oracle_action and not pred_action,
            "wrong_action": pred_action and not gold_canon and not oracle_canon,
            "strong_confirm_over_trigger": strong_over,
            "close_ack_over_action": close_ack_over,
            "challenge_closer_to_gold": set_type == "challenge" and gold_canon and not oracle_canon,
            "challenge_closer_to_oracle": set_type == "challenge" and oracle_canon and not gold_canon,
            "challenge_third_solution": set_type == "challenge" and pred_action and not gold_canon and not oracle_canon,
            "challenge_pred_no_action": set_type == "challenge" and not pred_action,
        }
        results.append(result)
        groups = ["global", set_type or "unknown"]
        for group in groups:
            c = counters[group]
            c["total"] += 1
            c["parse_error"] += int(bool(result["parse_error"]))
            c["gold_exact"] += int(gold_exact)
            c["gold_canonical"] += int(gold_canon)
            c["oracle_exact"] += int(oracle_exact)
            c["oracle_canonical"] += int(oracle_canon)
            c["no_action_den"] += int(gold_oracle_no_action)
            c["no_action_correct"] += int(gold_oracle_no_action and not pred_action)
            c["over_action"] += int(result["over_action"])
            c["dialogue_agree_exact"] += int(str(agree) == str(gold_agree))
            c["pred_action"] += int(pred_action)
            c["gold_action"] += int(gold_action)
            c["oracle_action"] += int(oracle_action)
            c["missing_gold"] += int(result["missing_gold"])
            c["missing_oracle"] += int(result["missing_oracle"])
            c["wrong_action"] += int(result["wrong_action"])
            c["strong_pred"] += int(is_strong(agree))
            c["strong_hit"] += int(corresponding_strong(agree, gold_agree, oracle_agree))
            c["strong_over"] += int(strong_over)
            c["dialogue_agree_non_empty"] += int(is_action(agree))
            c["close_ack_over_action"] += int(close_ack_over)
            c["challenge_closer_to_gold"] += int(result["challenge_closer_to_gold"])
            c["challenge_closer_to_oracle"] += int(result["challenge_closer_to_oracle"])
            c["challenge_third_solution"] += int(result["challenge_third_solution"])
            c["challenge_pred_no_action"] += int(result["challenge_pred_no_action"])
        for key_name in ("gold_response_solution", "oracle_response_solution", "oracle_rule_id"):
            key = f"{key_name}={row.get(key_name, '')}"
            b = buckets[key]
            b["total"] += 1
            b["gold_canonical"] += int(gold_canon)
            b["oracle_canonical"] += int(oracle_canon)
            b["missing_gold"] += int(result["missing_gold"])
            b["missing_oracle"] += int(result["missing_oracle"])
            b["wrong_action"] += int(result["wrong_action"])
    return results, counters, buckets, rows


def metrics(c: Counter, prefix: str = "") -> Dict[str, Any]:
    total = c["total"]
    pred_action = c["pred_action"]
    return {
        f"{prefix}total": total,
        f"{prefix}gold_response_exact_match_rate": rate(c["gold_exact"], total),
        f"{prefix}gold_response_canonical_match_rate": rate(c["gold_canonical"], total),
        f"{prefix}oracle_response_exact_match_rate": rate(c["oracle_exact"], total),
        f"{prefix}oracle_response_canonical_match_rate": rate(c["oracle_canonical"], total),
        f"{prefix}no_action_precision": rate(c["no_action_correct"], c["no_action_den"]),
        f"{prefix}over_action_rate": rate(c["over_action"], c["no_action_den"]),
        f"{prefix}dialogue_agree_exact_match_rate": rate(c["dialogue_agree_exact"], total),
        f"{prefix}parse_error_rate": rate(c["parse_error"], total),
        f"{prefix}action_trigger_rate": rate(c["pred_action"], total),
        f"{prefix}missing_gold_rate": rate(c["missing_gold"], c["gold_action"]),
        f"{prefix}missing_oracle_rate": rate(c["missing_oracle"], c["oracle_action"]),
        f"{prefix}wrong_rate": rate(c["wrong_action"], pred_action),
        f"{prefix}strong_confirm_over_trigger_rate": rate(c["strong_over"], total),
        f"{prefix}close_ack_over_action_rate": rate(c["close_ack_over_action"], total),
    }


def action_metrics(c: Counter) -> Dict[str, Any]:
    total = c["total"]
    pred_action = c["pred_action"]
    return {
        "action_total": total,
        "action_trigger_rate": rate(c["pred_action"], total),
        "action_gold_exact_match_rate": rate(c["gold_exact"], total),
        "action_gold_canonical_match_rate": rate(c["gold_canonical"], total),
        "action_oracle_exact_match_rate": rate(c["oracle_exact"], total),
        "action_oracle_canonical_match_rate": rate(c["oracle_canonical"], total),
        "action_missing_gold_rate": rate(c["missing_gold"], c["gold_action"]),
        "action_missing_oracle_rate": rate(c["missing_oracle"], c["oracle_action"]),
        "action_wrong_rate": rate(c["wrong_action"], pred_action),
    }


def write_report(path: Path, label: str, counters: Dict[str, Counter], buckets: Dict[str, Counter], results: List[Dict[str, Any]]) -> None:
    global_m = metrics(counters["global"], "global_")
    stable_m = metrics(counters["stable"], "stable_")
    action_m = action_metrics(counters["action"])
    strong_precision = rate(counters["global"]["strong_hit"], counters["global"]["strong_pred"])
    lines = [
        f"# FD Replay Eval Report - {label}",
        "",
        "## Overall",
        *[f"- {k}: `{v:.4f}`" if isinstance(v, float) else f"- {k}: `{v}`" for k, v in global_m.items()],
        f"- strong_confirm_precision: `{strong_precision:.4f}`",
        f"- dialogue_agree_non_empty_count: `{counters['global']['dialogue_agree_non_empty']}`",
        "",
        "## Stable",
        *[f"- {k}: `{v:.4f}`" if isinstance(v, float) else f"- {k}: `{v}`" for k, v in stable_m.items()],
        "",
        "## Action",
        *[f"- {k}: `{v:.4f}`" if isinstance(v, float) else f"- {k}: `{v}`" for k, v in action_m.items()],
        "",
        "## DialogueAgreeSolution",
        f"- global_strong_confirm_over_trigger_rate: `{rate(counters['global']['strong_over'], counters['global']['total']):.4f}`",
        f"- stable_strong_confirm_over_trigger_rate: `{rate(counters['stable']['strong_over'], counters['stable']['total']):.4f}`",
        f"- action_strong_confirm_over_trigger_rate: `{rate(counters['action']['strong_over'], counters['action']['total']):.4f}`",
        f"- strong_confirm_precision: `{strong_precision:.4f}`",
        f"- dialogue_agree_non_empty_count: `{counters['global']['dialogue_agree_non_empty']}`",
        "",
        "## Challenge Analysis",
        f"- challenge_total: `{counters['challenge']['total']}`",
        f"- closer_to_gold: `{counters['challenge']['challenge_closer_to_gold']}`",
        f"- closer_to_oracle: `{counters['challenge']['challenge_closer_to_oracle']}`",
        f"- third_solution: `{counters['challenge']['challenge_third_solution']}`",
        f"- pred_no_action: `{counters['challenge']['challenge_pred_no_action']}`",
    ]
    sample_sections = [
        ("Parse Error Examples", lambda r: bool(r["parse_error"])),
        ("Action Wrong Examples", lambda r: bool(r["wrong_action"])),
        ("Strong Confirmation Over-Trigger Examples", lambda r: bool(r["strong_confirm_over_trigger"])),
        ("Close/Ack Over-Action Examples", lambda r: bool(r["close_ack_over_action"])),
    ]
    for title, pred in sample_sections:
        lines.extend(["", f"## {title}"])
        examples = [r for r in results if pred(r)][:20]
        if not examples:
            lines.append("- None")
        for r in examples:
            lines.append(
                f"- `{r['sample_id']}` set=`{r['set_type']}` q=`{r['last_user_query']}` "
                f"pred=`{r['pred_response_solution']}` gold=`{r['gold_response_solution']}` oracle=`{r['oracle_response_solution']}` "
                f"agree=`{r['pred_dialogue_agree_solution']}` rule=`{r['oracle_rule_id']}` parse_error=`{r['parse_error']}`"
            )
    lines.extend(["", "## By Bucket", "| bucket | total | gold_canonical | oracle_canonical | missing_gold | missing_oracle | wrong_action |", "|---|---:|---:|---:|---:|---:|---:|"])
    for key, counter in sorted(buckets.items(), key=lambda kv: kv[1]["total"], reverse=True)[:120]:
        total = counter["total"] or 1
        lines.append(
            f"| `{key}` | {counter['total']} | {rate(counter['gold_canonical'], total):.3f} | "
            f"{rate(counter['oracle_canonical'], total):.3f} | {rate(counter['missing_gold'], total):.3f} | "
            f"{rate(counter['missing_oracle'], total):.3f} | {rate(counter['wrong_action'], total):.3f} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary = {**global_m, **stable_m, **action_m, "strong_confirm_precision": strong_precision, "close_ack_over_action_rate": rate(counters["global"]["close_ack_over_action"], counters["global"]["total"])}
    path.with_suffix(".summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-outputs", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--label", default="model")
    args = parser.parse_args()
    rows = read_jsonl(Path(args.model_outputs))
    if not rows:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text("", encoding="utf-8")
        Path(args.report).write_text(
            f"# FD Replay Eval Report - {args.label}\n\nNo model outputs found. No metrics are fabricated.\n",
            encoding="utf-8",
        )
        return
    results, counters, buckets, _ = evaluate(rows)
    write_jsonl(Path(args.output), results)
    write_report(Path(args.report), args.label, counters, buckets, results)


if __name__ == "__main__":
    main()
