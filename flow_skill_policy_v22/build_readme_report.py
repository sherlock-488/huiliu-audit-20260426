#!/usr/bin/env python3
"""Build v22 total report."""

from __future__ import annotations

import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flow_skill_policy_v22.common import V22_REPORTS, V22_ROOT, ensure_dirs


def _num(path: Path, key: str) -> int:
    if not path.exists():
        return 0
    m = re.search(rf"{re.escape(key)}: `?(\d+)`?", path.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else 0


def main() -> None:
    ensure_dirs()
    fd = V22_REPORTS / "fulfillment_delivery_policy_v22_report.md"
    rq = V22_REPORTS / "receipt_quality_policy_v22_report.md"
    replay = V22_REPORTS / "replay_sets_v22_report.md"
    fd_v21, fd_v22 = _num(fd, "conflict_v21"), _num(fd, "conflict_v22")
    rq_v21, rq_v22 = _num(rq, "conflict_v21"), _num(rq, "conflict_v22")
    fd_other21, fd_other22 = _num(fd, "OTHER_count_v21"), _num(fd, "OTHER_count_v22")
    rq_other21, rq_other22 = _num(rq, "OTHER_count_v21"), _num(rq, "OTHER_count_v22")
    close_over = _num(fd, "close_ack_transfer_over_action_v22") + _num(rq, "close_ack_transfer_over_action_v22")
    strong_over = _num(fd, "strong_confirmation_over_trigger_v22") + _num(rq, "strong_confirmation_over_trigger_v22")
    rep = replay.read_text(encoding="utf-8") if replay.exists() else ""
    fd_sets = re.search(r"fulfillment_delivery stable/action/challenge: `(\d+)` / `(\d+)` / `(\d+)`", rep)
    rq_sets = re.search(r"receipt_quality stable/action/challenge: `(\d+)` / `(\d+)` / `(\d+)`", rep)
    lines = [
        "# Flow Skill Policy v22 Report",
        "",
        "## 1. v22 相比 v21 修了什么",
        "- 扩充 current_turn_intent 词表，补足配送 ETA/催促、无骑手、联系骑手、品质短句、退款进度、退款诉求等召回。",
        "- 新增 `is_pure_confirm` / `maybe_accept_pending`，避免“嗯，什么时候退完”误确认。",
        "- 新增 safe context bridge，只在极短追问/短催促且上下文同主题时增强 intent。",
        "- replay 增加 action-focused 集，避免 stable 集无动作占比过高时看不出动作选择提升。",
        "",
        "## 2. current_turn_intent 召回提升",
        "覆盖了“怎么还没配送、急、还得等到啥时候、5分钟？”等配送短句，以及“漏的、空心、碎的、干瘪、臭、不能吃”等品质短句；图片识别文本可直接标 upload_image。",
        "",
        "## 3. Conflict 对比",
        f"- FD conflict v21 -> v22: `{fd_v21}` -> `{fd_v22}`",
        f"- RQ conflict v21 -> v22: `{rq_v21}` -> `{rq_v22}`",
        f"- FD-OTHER v21 -> v22: `{fd_other21}` -> `{fd_other22}`",
        f"- RQ-OTHER v21 -> v22: `{rq_other21}` -> `{rq_other22}`",
        "",
        "## 4. 安全性",
        f"- close/ack over-action v22: `{close_over}`",
        f"- strong confirmation over-trigger v22: `{strong_over}`",
        "",
        "## 5. Replay 使用方式",
        f"- FD stable/action/challenge: `{fd_sets.group(1) if fd_sets else 0}` / `{fd_sets.group(2) if fd_sets else 0}` / `{fd_sets.group(3) if fd_sets else 0}`",
        f"- RQ stable/action/challenge: `{rq_sets.group(1) if rq_sets else 0}` / `{rq_sets.group(2) if rq_sets else 0}` / `{rq_sets.group(3) if rq_sets else 0}`",
        "- stable: 主自动指标。",
        "- action-focused: 单独看动作召回，不替代主指标。",
        "- challenge: 训练师校准，不混入主分。",
        "",
        "## 6. 是否进入模型 replay",
        "fulfillment_delivery_policy_v22 建议进入正式模型 replay；receipt_quality_policy_v22 建议先离线 replay + 训练师校准。",
        "",
        "## 7. 仍需训练师确认",
        "- 短句“5分钟？”等是否应视为 ETA 追问。",
        "- “行吧/就这样吧”在 pending 退款/赔付/取消下是否都算接受。",
        "- 品质图文识别能否作为图片凭证和商品选择证据。",
        "- 赔付 first_offer 取区间下限是否符合训练师口径。",
    ]
    (V22_ROOT / "README_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
