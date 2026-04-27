#!/usr/bin/env python3
"""Parse model outputs for flow replay evaluation."""

from __future__ import annotations

import ast
import json
import re
import sys
from typing import Any, Dict, Iterable, Optional


FIELDS = ("Response", "ResponseSolution", "DialogueAgreeSolution")


def _clean_fence(text: str) -> str:
    fence = re.search(r"```(?:json)?\s*(.*?)```", text or "", flags=re.S | re.I)
    return fence.group(1).strip() if fence else (text or "").strip()


def _json_candidates(text: str) -> Iterable[str]:
    cleaned = _clean_fence(text)
    yield cleaned
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        yield cleaned[start : end + 1]
    # Some wrappers store escaped JSON as a quoted string.
    try:
        unescaped = json.loads(cleaned)
        if isinstance(unescaped, str):
            yield unescaped
    except Exception:
        pass


def _coerce_payload(payload: Any) -> Optional[Dict[str, Any]]:
    if isinstance(payload, dict):
        if isinstance(payload.get("output"), str):
            nested = parse_model_output(payload["output"])
            if not nested.get("parse_error"):
                return nested
        if isinstance(payload.get("raw_output"), str) and not any(k in payload for k in FIELDS):
            nested = parse_model_output(payload["raw_output"])
            if not nested.get("parse_error"):
                return nested
        return payload
    if isinstance(payload, str):
        nested = parse_model_output(payload)
        if not nested.get("parse_error"):
            return nested
    return None


def parse_model_output(raw_text: str) -> Dict[str, Any]:
    """Parse raw model text into Response/ResponseSolution/DialogueAgreeSolution.

    Supports pure JSON, markdown code fences, leading/trailing prose around JSON,
    wrapper JSON with an `output` field, and Python-literal dicts as a fallback.
    """
    errors = []
    for candidate in _json_candidates(raw_text):
        if not candidate:
            continue
        for parser_name, parser in (("json", json.loads), ("literal", ast.literal_eval)):
            try:
                payload = parser(candidate)
                coerced = _coerce_payload(payload)
                if coerced is None:
                    continue
                return {
                    "Response": str(coerced.get("Response", "") or ""),
                    "ResponseSolution": str(coerced.get("ResponseSolution", "无") or "无").strip() or "无",
                    "DialogueAgreeSolution": str(coerced.get("DialogueAgreeSolution", "无") or "无").strip() or "无",
                    "parse_error": "",
                    "raw_output": raw_text,
                }
            except Exception as exc:  # noqa: BLE001 - collect parser failures.
                errors.append(f"{parser_name}:{type(exc).__name__}")
    return {
        "Response": "",
        "ResponseSolution": "无",
        "DialogueAgreeSolution": "无",
        "parse_error": "parse_failed:" + ",".join(errors[:5]),
        "raw_output": raw_text,
    }


def parse_model_output_row(row: Dict[str, Any]) -> Dict[str, Any]:
    if all(field in row for field in FIELDS):
        return {
            "Response": str(row.get("Response", "") or ""),
            "ResponseSolution": str(row.get("ResponseSolution", "无") or "无").strip() or "无",
            "DialogueAgreeSolution": str(row.get("DialogueAgreeSolution", "无") or "无").strip() or "无",
            "parse_error": str(row.get("parse_error", "") or ""),
            "raw_output": str(row.get("raw_output", row.get("output", "")) or ""),
        }
    raw = row.get("output", row.get("raw_output", ""))
    return parse_model_output(str(raw or ""))


def parser_test_cases() -> list[dict[str, Any]]:
    return [
        {
            "name": "pure_json",
            "raw": '{"Response":"客服:好的","ResponseSolution":"系统催单","DialogueAgreeSolution":"无"}',
            "expect_parse_error": False,
        },
        {
            "name": "code_fence_json",
            "raw": '```json\n{"Response":"客服:好的","ResponseSolution":"无","DialogueAgreeSolution":"无"}\n```',
            "expect_parse_error": False,
        },
        {
            "name": "prefix_text_json",
            "raw": '下面是结果 {"Response":"客服:好的","ResponseSolution":"加急调度","DialogueAgreeSolution":"无"} 谢谢',
            "expect_parse_error": False,
        },
        {
            "name": "non_json_text",
            "raw": "客服: 我帮您催一下",
            "expect_parse_error": True,
        },
        {
            "name": "missing_fields",
            "raw": '{"Response":"客服:好的"}',
            "expect_parse_error": False,
        },
        {
            "name": "composite_solution",
            "raw": '{"Response":"客服:好的","ResponseSolution":"系统催单;智能跟单","DialogueAgreeSolution":"无"}',
            "expect_parse_error": False,
        },
    ]


def build_report(path: str = "replay_run_effect_v1/reports/output_parser_report.md") -> None:
    rows = []
    for case in parser_test_cases():
        parsed = parse_model_output(case["raw"])
        passed = bool(parsed.get("parse_error")) == bool(case["expect_parse_error"])
        rows.append((case, parsed, passed))
    lines = [
        "# Output Parser Report",
        "",
        "## Summary",
        f"- test_cases: `{len(rows)}`",
        f"- passed: `{sum(1 for _, _, passed in rows if passed)}`",
        "",
        "## Cases",
        "| case | expected_error | actual_error | ResponseSolution | DialogueAgreeSolution | pass |",
        "|---|---:|---:|---|---|---:|",
    ]
    for case, parsed, passed in rows:
        lines.append(
            f"| `{case['name']}` | `{case['expect_parse_error']}` | `{bool(parsed.get('parse_error'))}` | "
            f"`{parsed.get('ResponseSolution')}` | `{parsed.get('DialogueAgreeSolution')}` | `{passed}` |"
        )
    from pathlib import Path

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _self_test() -> None:
    for case in parser_test_cases():
        print(json.dumps({"case": case["name"], **parse_model_output(case["raw"])}, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _self_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "--report":
        build_report(sys.argv[2] if len(sys.argv) > 2 else "replay_run_effect_v1/reports/output_parser_report.md")
    else:
        print(json.dumps(parse_model_output(sys.stdin.read()), ensure_ascii=False, indent=2))
