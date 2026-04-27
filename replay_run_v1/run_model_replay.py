#!/usr/bin/env python3
"""Run fulfillment-delivery replay against a model endpoint or internal command.

The actual model invocation is intentionally a TODO hook. Dry-run validates
inputs and output paths without fabricating predictions.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flow_skill_policy_v22.common import read_jsonl  # noqa: E402


# TODO: Configure one of the following before real replay.
MODEL_NAME = os.environ.get("REPLAY_MODEL_NAME", "")
API_ENDPOINT = os.environ.get("REPLAY_API_ENDPOINT", "")
INTERNAL_COMMAND = os.environ.get("REPLAY_INTERNAL_COMMAND", "")
DEFAULT_CONCURRENCY = int(os.environ.get("REPLAY_CONCURRENCY", "2"))
DEFAULT_RETRY = int(os.environ.get("REPLAY_RETRY", "2"))


def _parse_model_text(text: str) -> Dict[str, str]:
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return {
                "Response": str(payload.get("Response", "")),
                "ResponseSolution": str(payload.get("ResponseSolution", "无") or "无"),
                "DialogueAgreeSolution": str(payload.get("DialogueAgreeSolution", "无") or "无"),
                "parse_error": "",
            }
    except json.JSONDecodeError:
        pass
    return {"Response": "", "ResponseSolution": "无", "DialogueAgreeSolution": "无", "parse_error": "model_output_json_parse_error"}


def _call_internal_command(prompt: str, timeout: int) -> str:
    if not INTERNAL_COMMAND:
        raise RuntimeError("No INTERNAL_COMMAND configured. Set REPLAY_INTERNAL_COMMAND or use --dry-run.")
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
        raise RuntimeError(f"internal command failed: {proc.stderr[:500]}")
    return proc.stdout


def _call_model(row: Dict[str, Any], timeout: int, retry: int) -> Dict[str, Any]:
    prompt = row.get("prompt", "")
    last_error = ""
    for _ in range(max(1, retry + 1)):
        try:
            raw = _call_internal_command(prompt, timeout)
            parsed = _parse_model_text(raw)
            return {
                "sample_id": row.get("sample_id"),
                "set_type": row.get("set_type", ""),
                "raw_output": raw,
                **parsed,
            }
        except Exception as exc:  # noqa: BLE001 - report retry errors in output row.
            last_error = str(exc)
    return {
        "sample_id": row.get("sample_id"),
        "set_type": row.get("set_type", ""),
        "raw_output": "",
        "Response": "",
        "ResponseSolution": "无",
        "DialogueAgreeSolution": "无",
        "parse_error": last_error or "model_call_failed",
    }


def _run_file(input_path: Path, output_path: Path, dry_run: bool, limit: int, concurrency: int, retry: int, timeout: int) -> Dict[str, Any]:
    rows = list(read_jsonl(input_path)) if input_path.exists() else []
    if limit > 0:
        rows = rows[:limit]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        return {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "input_exists": input_path.exists(),
            "input_rows": len(rows),
            "would_call_model": False,
            "model_configured": bool(API_ENDPOINT or INTERNAL_COMMAND),
        }
    if not (API_ENDPOINT or INTERNAL_COMMAND):
        raise RuntimeError("No model API/internal command configured. Use --dry-run or set REPLAY_INTERNAL_COMMAND/API config.")
    with output_path.open("w", encoding="utf-8") as out:
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
            futures = [pool.submit(_call_model, row, timeout, retry) for row in rows]
            for fut in as_completed(futures):
                out.write(json.dumps(fut.result(), ensure_ascii=False) + "\n")
    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "input_rows": len(rows),
        "would_call_model": True,
        "model_configured": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-input", default="replay_run_v1/inputs/FD_BASELINE_INPUTS.jsonl")
    parser.add_argument("--skill-input", default="replay_run_v1/inputs/FD_SKILL_INPUTS.jsonl")
    parser.add_argument("--baseline-output", default="replay_run_v1/model_outputs/FD_BASELINE_OUTPUTS.jsonl")
    parser.add_argument("--skill-output", default="replay_run_v1/model_outputs/FD_SKILL_OUTPUTS.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", choices=["both", "baseline", "skill"], default="both")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--retry", type=int, default=DEFAULT_RETRY)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    jobs = []
    if args.only in ("both", "baseline"):
        jobs.append((Path(args.baseline_input), Path(args.baseline_output)))
    if args.only in ("both", "skill"):
        jobs.append((Path(args.skill_input), Path(args.skill_output)))
    summaries = []
    for input_path, output_path in jobs:
        summaries.append(_run_file(input_path, output_path, args.dry_run, args.limit, args.concurrency, args.retry, args.timeout))
    print(json.dumps({"MODEL_NAME": MODEL_NAME, "API_ENDPOINT": bool(API_ENDPOINT), "INTERNAL_COMMAND": bool(INTERNAL_COMMAND), "runs": summaries}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
