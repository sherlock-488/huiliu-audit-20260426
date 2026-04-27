#!/usr/bin/env python3
"""Parse all-scene prompt into structured pieces."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ in (None, ""):
    for parent in Path(__file__).resolve().parents:
        if parent.name == "flow_skill_mining":
            sys.path.insert(0, str(parent.parent))
            break


def _section_after(text: str, header_pattern: str) -> str:
    match = re.search(header_pattern, text)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"\n##\s+", text[start:])
    if not next_match:
        return text[start:]
    return text[start : start + next_match.start()]


def _subsection_after(text: str, header_pattern: str) -> str:
    match = re.search(header_pattern, text)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"\n###\s+|\n##\s+", text[start:])
    if not next_match:
        return text[start:]
    return text[start : start + next_match.start()]


def _parse_brace_signal(line: str) -> Dict[str, str]:
    body = line.strip()[1:-1].strip()
    if not body:
        return {}
    sep_positions = [pos for pos in (body.find(":"), body.find("：")) if pos >= 0]
    if not sep_positions:
        return {}
    pos = min(sep_positions)
    key = body[:pos].strip().strip("'\"")
    value = body[pos + 1 :].strip().strip("'\"")
    return {key: value} if key else {}


def _literal_dict(line: str) -> Any:
    try:
        return ast.literal_eval(line)
    except Exception:
        return None


def _last_line_with_prefix(history: str, prefixes: List[str]) -> str:
    for raw_line in reversed(history.splitlines()):
        line = raw_line.strip()
        for prefix in prefixes:
            if line.startswith(prefix):
                return line[len(prefix) :].strip()
    return ""


def parse_all_scene_prompt(input_text: str) -> dict:
    result = {
        "available_solutions": [],
        "current_time": "",
        "signals": {},
        "items": [],
        "selected_item_info": {},
        "dialogue_history": "",
        "last_user_query": "",
        "last_assistant_response": "",
        "parse_errors": [],
    }
    if not input_text:
        result["parse_errors"].append("empty input_text")
        return result

    text = input_text.replace("\\n", "\n")

    solution_block = _section_after(text, r"##\s*你查询到的方案列表\s*\n")
    if not solution_block:
        result["parse_errors"].append("missing available solution section")
    else:
        for line_no, line in enumerate(solution_block.splitlines(), 1):
            stripped = line.strip()
            if not stripped:
                continue
            if not stripped.startswith("{"):
                continue
            try:
                obj = json.loads(stripped)
                if isinstance(obj, dict) and obj.get("name"):
                    result["available_solutions"].append(
                        {
                            "name": str(obj.get("name", "")).strip(),
                            "description": str(obj.get("description", "")).strip(),
                        }
                    )
            except Exception as exc:
                result["parse_errors"].append(f"available_solution line {line_no}: {exc}")

    time_match = re.search(r"###\s*当前时间\s*\n([^\n]+)", text)
    if time_match:
        result["current_time"] = time_match.group(1).strip()
    else:
        result["parse_errors"].append("missing current_time")

    signal_block = _subsection_after(text, r"###\s*系统信号\s*\n")
    if not signal_block:
        result["parse_errors"].append("missing system signal section")
    else:
        for line_no, line in enumerate(signal_block.splitlines(), 1):
            stripped = line.strip()
            if not stripped or not (stripped.startswith("{") and stripped.endswith("}")):
                continue
            dict_obj = None
            if ("'" in stripped or '"' in stripped) and ":" in stripped:
                dict_obj = _literal_dict(stripped)
            if isinstance(dict_obj, dict):
                if "商品名称" in dict_obj:
                    result["items"].append(dict_obj)
                elif any(
                    key in dict_obj
                    for key in [
                        "已选择退款商品",
                        "已选择商品",
                        "是否已收集图片凭证",
                        "是否已收集退款原因",
                        "建议退款比例",
                        "退款申请结果",
                    ]
                ):
                    result["selected_item_info"].update(dict_obj)
                else:
                    for key, value in dict_obj.items():
                        result["signals"][str(key)] = "" if value is None else str(value)
                continue

            parsed = _parse_brace_signal(stripped)
            if not parsed:
                result["parse_errors"].append(f"signal line {line_no}: unparsed brace line")
                continue
            key = next(iter(parsed))
            value = parsed[key]
            if key.startswith("已选择") or key in {
                "已选择退款商品",
                "已选择商品",
                "是否已收集图片凭证",
                "是否已收集退款原因",
                "建议退款比例",
                "退款申请结果",
            }:
                result["selected_item_info"][key] = value
            else:
                result["signals"][key] = value

    history_match = re.search(r"(?:##|###)\s*你与用户的对话历史\s*\n(.*)", text, re.DOTALL)
    if history_match:
        history = history_match.group(1).strip()
        trailing_assistant = re.search(r"\nAssistant:\s*$", history)
        if trailing_assistant:
            history = history[: trailing_assistant.start()].rstrip()
        result["dialogue_history"] = history
        result["last_user_query"] = _last_line_with_prefix(history, ["用户:"])
        result["last_assistant_response"] = _last_line_with_prefix(history, ["客服:", "Assistant:"])
    else:
        result["parse_errors"].append("missing dialogue_history")

    return result


if __name__ == "__main__":
    import sys

    print(json.dumps(parse_all_scene_prompt(sys.stdin.read()), ensure_ascii=False, indent=2))
