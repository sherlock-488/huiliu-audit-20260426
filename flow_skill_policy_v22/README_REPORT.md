# Flow Skill Policy v22 Report

## 1. v22 相比 v21 修了什么
- 扩充 current_turn_intent 词表，补足配送 ETA/催促、无骑手、联系骑手、品质短句、退款进度、退款诉求等召回。
- 新增 `is_pure_confirm` / `maybe_accept_pending`，避免“嗯，什么时候退完”误确认。
- 新增 safe context bridge，只在极短追问/短催促且上下文同主题时增强 intent。
- replay 增加 action-focused 集，避免 stable 集无动作占比过高时看不出动作选择提升。

## 2. current_turn_intent 召回提升
覆盖了“怎么还没配送、急、还得等到啥时候、5分钟？”等配送短句，以及“漏的、空心、碎的、干瘪、臭、不能吃”等品质短句；图片识别文本可直接标 upload_image。

## 3. Conflict 对比
- FD conflict v21 -> v22: `50` -> `45`
- RQ conflict v21 -> v22: `45` -> `41`
- FD-OTHER v21 -> v22: `27` -> `20`
- RQ-OTHER v21 -> v22: `30` -> `23`

## 4. 安全性
- close/ack over-action v22: `0`
- strong confirmation over-trigger v22: `2`

## 5. Replay 使用方式
- FD stable/action/challenge: `76` / `65` / `45`
- RQ stable/action/challenge: `79` / `79` / `41`
- stable: 主自动指标。
- action-focused: 单独看动作召回，不替代主指标。
- challenge: 训练师校准，不混入主分。

## 6. 是否进入模型 replay
fulfillment_delivery_policy_v22 建议进入正式模型 replay；receipt_quality_policy_v22 建议先离线 replay + 训练师校准。

## 7. 仍需训练师确认
- 短句“5分钟？”等是否应视为 ETA 追问。
- “行吧/就这样吧”在 pending 退款/赔付/取消下是否都算接受。
- 品质图文识别能否作为图片凭证和商品选择证据。
- 赔付 first_offer 取区间下限是否符合训练师口径。
