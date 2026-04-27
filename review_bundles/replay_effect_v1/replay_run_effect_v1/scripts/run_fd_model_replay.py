#!/usr/bin/env python3
"""Run a fulfillment-delivery replay input through a model command."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from output_parser import parse_model_output  # noqa: E402


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


def invoke_command(command: str, prompt: str, timeout: int) -> str:
    proc = subprocess.run(
        command,
        input=prompt,
        text=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[:1000] or f"internal command exited {proc.returncode}")
    return proc.stdout


def output_row(row: Dict[str, Any], mode: str, raw_output: str, parse_error: str = "") -> Dict[str, Any]:
    parsed = parse_model_output(raw_output) if raw_output else {
        "Response": "",
        "ResponseSolution": "无",
        "DialogueAgreeSolution": "无",
        "parse_error": parse_error,
        "raw_output": raw_output,
    }
    if parse_error and not parsed.get("parse_error"):
        parsed["parse_error"] = parse_error
    return {
        "sample_id": row.get("sample_id", ""),
        "set_type": row.get("set_type", ""),
        "mode": mode,
        "raw_output": raw_output,
        "Response": parsed.get("Response", ""),
        "ResponseSolution": parsed.get("ResponseSolution", "无"),
        "DialogueAgreeSolution": parsed.get("DialogueAgreeSolution", "无"),
        "parse_error": parsed.get("parse_error", ""),
        "gold_response_solution": row.get("gold_response_solution", "无"),
        "gold_dialogue_agree_solution": row.get("gold_dialogue_agree_solution", "无"),
        "oracle_response_solution": row.get("oracle_response_solution", "无"),
        "oracle_dialogue_agree_solution": row.get("oracle_dialogue_agree_solution", "无"),
        "oracle_rule_id": row.get("oracle_rule_id", ""),
        "gold_oracle_relation": row.get("gold_oracle_relation", ""),
        "last_user_query": row.get("last_user_query", ""),
        "scene": row.get("scene", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=["baseline", "skill", "gold_guided", "challenge"], required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--internal-command", default="")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    command = args.internal_command or os.environ.get("REPLAY_INTERNAL_COMMAND", "")
    rows = read_jsonl(Path(args.input))
    if args.limit > 0:
        rows = rows[: args.limit]
    summary = {
        "input": args.input,
        "output": args.output,
        "mode": args.mode,
        "input_exists": Path(args.input).exists(),
        "rows": len(rows),
        "dry_run": args.dry_run,
        "has_internal_command": bool(command),
    }
    if args.dry_run:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return
    if not command:
        raise SystemExit("缺模型命令：请传 --internal-command 或设置 REPLAY_INTERNAL_COMMAND；不会伪造输出。")
    out_rows = []
    for row in rows:
        try:
            raw = invoke_command(command, row.get("prompt", ""), args.timeout)
            out_rows.append(output_row(row, args.mode, raw))
        except Exception as exc:  # noqa: BLE001
            out_rows.append(output_row(row, args.mode, "", str(exc)))
    write_jsonl(Path(args.output), out_rows)
    print(json.dumps({**summary, "written": len(out_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
