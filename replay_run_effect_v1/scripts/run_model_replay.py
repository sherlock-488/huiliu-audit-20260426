#!/usr/bin/env python3
"""Model replay runner for FD baseline/skill/gold-guided inputs.

This script is intentionally configurable and supports dry-run. It does not
fake model outputs when no endpoint or internal command is configured.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from output_parser import parse_model_output  # noqa: E402


MODEL_NAME = os.environ.get("REPLAY_MODEL_NAME", "")
API_ENDPOINT = os.environ.get("REPLAY_API_ENDPOINT", "")
INTERNAL_COMMAND = os.environ.get("REPLAY_INTERNAL_COMMAND", "")
DEFAULT_CONCURRENCY = int(os.environ.get("REPLAY_CONCURRENCY", "2"))
DEFAULT_RETRY = int(os.environ.get("REPLAY_RETRY", "2"))


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def call_internal(prompt: str, timeout: int) -> str:
    if not INTERNAL_COMMAND:
        raise RuntimeError("No REPLAY_INTERNAL_COMMAND configured.")
    proc = subprocess.run(
        INTERNAL_COMMAND,
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


def call_model(row: Dict[str, Any], timeout: int, retry: int) -> Dict[str, Any]:
    last_error = ""
    for _ in range(max(1, retry + 1)):
        try:
            raw = call_internal(row.get("prompt", ""), timeout)
            parsed = parse_model_output(raw)
            return {
                "sample_id": row.get("sample_id"),
                "set_type": row.get("set_type"),
                "raw_output": raw,
                **parsed,
            }
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
    return {
        "sample_id": row.get("sample_id"),
        "set_type": row.get("set_type"),
        "raw_output": "",
        "Response": "",
        "ResponseSolution": "无",
        "DialogueAgreeSolution": "无",
        "parse_error": last_error or "model_call_failed",
    }


def run_one(label: str, input_path: Path, output_path: Path, args: argparse.Namespace) -> Dict[str, Any]:
    rows = read_jsonl(input_path)
    if args.limit > 0:
        rows = rows[: args.limit]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "label": label,
        "input_path": str(input_path),
        "output_path": str(output_path),
        "input_exists": input_path.exists(),
        "input_rows": len(rows),
        "dry_run": args.dry_run,
        "model_configured": bool(API_ENDPOINT or INTERNAL_COMMAND),
    }
    if args.dry_run:
        return summary
    if not (API_ENDPOINT or INTERNAL_COMMAND):
        raise RuntimeError("No model endpoint/internal command configured. Use --dry-run or set REPLAY_INTERNAL_COMMAND.")
    with output_path.open("w", encoding="utf-8") as f:
        with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
            futures = [pool.submit(call_model, row, args.timeout, args.retry) for row in rows]
            for future in as_completed(futures):
                f.write(json.dumps(future.result(), ensure_ascii=False) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="replay_run_effect_v1/inputs")
    parser.add_argument("--output-dir", default="replay_run_effect_v1/model_outputs")
    parser.add_argument("--only", choices=["all", "baseline", "skill", "gold_guided"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--retry", type=int, default=DEFAULT_RETRY)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    jobs = {
        "baseline": (input_dir / "FD_BASELINE_INPUTS.jsonl", output_dir / "FD_BASELINE_OUTPUTS.jsonl"),
        "skill": (input_dir / "FD_SKILL_INPUTS.jsonl", output_dir / "FD_SKILL_OUTPUTS.jsonl"),
        "gold_guided": (input_dir / "FD_GOLD_GUIDED_INPUTS.jsonl", output_dir / "FD_GOLD_GUIDED_OUTPUTS.jsonl"),
    }
    labels = jobs if args.only == "all" else {args.only: jobs[args.only]}
    summaries = [run_one(label, src, dst, args) for label, (src, dst) in labels.items()]
    print(json.dumps({"MODEL_NAME": MODEL_NAME, "API_ENDPOINT": bool(API_ENDPOINT), "INTERNAL_COMMAND": bool(INTERNAL_COMMAND), "runs": summaries}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
