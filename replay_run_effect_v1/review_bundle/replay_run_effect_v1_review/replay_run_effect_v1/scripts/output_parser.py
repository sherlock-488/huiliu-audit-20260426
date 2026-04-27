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
                }
            except Exception as exc:  # noqa: BLE001 - collect parser failures.
                errors.append(f"{parser_name}:{type(exc).__name__}")
    return {
        "Response": "",
        "ResponseSolution": "无",
        "DialogueAgreeSolution": "无",
        "parse_error": "parse_failed:" + ",".join(errors[:5]),
    }


def parse_model_output_row(row: Dict[str, Any]) -> Dict[str, Any]:
    if all(field in row for field in FIELDS):
        return {
            "Response": str(row.get("Response", "") or ""),
            "ResponseSolution": str(row.get("ResponseSolution", "无") or "无").strip() or "无",
            "DialogueAgreeSolution": str(row.get("DialogueAgreeSolution", "无") or "无").strip() or "无",
            "parse_error": str(row.get("parse_error", "") or ""),
        }
    raw = row.get("output", row.get("raw_output", ""))
    return parse_model_output(str(raw or ""))


def _self_test() -> None:
    cases = [
        '{"Response":"客服:好的","ResponseSolution":"系统催单","DialogueAgreeSolution":"无"}',
        '```json\n{"Response":"客服:好的","ResponseSolution":"无","DialogueAgreeSolution":"无"}\n```',
        '下面是结果 {"Response":"客服:好的","ResponseSolution":"加急调度","DialogueAgreeSolution":"无"} 谢谢',
        '{"sample_id":"1","output":"{\\"Response\\":\\"客服:好的\\",\\"ResponseSolution\\":\\"智能跟单\\",\\"DialogueAgreeSolution\\":\\"无\\"}"}',
        "{'Response':'客服:好的','ResponseSolution':'外呼骑手-催促配送','DialogueAgreeSolution':'无'}",
    ]
    for case in cases:
        print(json.dumps(parse_model_output(case), ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        _self_test()
    else:
        print(json.dumps(parse_model_output(sys.stdin.read()), ensure_ascii=False, indent=2))
