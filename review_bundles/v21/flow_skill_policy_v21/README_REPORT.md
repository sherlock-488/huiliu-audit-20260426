# Flow Skill Policy v21 Report

## 1. v21 修了哪些 v2 误触发问题
- 动作触发只看当前最后一条用户消息，不再把 `dialogue_history[-800:]` 和当前 query 混在一起触发动作。
- 订单超时/超时风险不再单独等价于催配送意图，必须当前用户仍问 ETA 或催配送。
- “嗯/好/可以”只在存在 pending strong-confirmation solution 时才确认执行。
- RQ-09 退款催审必须当前询问退款进度，且退款状态明确进行中/审核中。
- 未选商品时不再用聚合 item 退款状态误判不可退。

## 2. current-turn gating 如何工作
`classify_current_turn()` 只读取 `last_user_query`，识别 close/thanks、ack_only、transfer_only 和动作意图；policy 最前面先处理结束/弱确认/转人工，只有当前轮仍有新诉求或 pending strong solution 被确认时才输出动作。

## 3. v2/v21 gold-oracle conflict 对比
- fulfillment_delivery: `65` -> `50`
- receipt_quality: `72` -> `45`

## 4. close/ack/transfer 类误触发下降
- close_ack_transfer_fixed: `37`
- FD oracle_no_gold_action: `30` -> `8`
- RQ oracle_no_gold_action: `21` -> `3`

## 5. 重点规则冲突下降
- FD-03/FD-05A/FD-08 详情见 `outputs/reports/fulfillment_delivery_policy_v21_report.md` 的 V2/V21 conflict rules。
- RQ-01/RQ-07/RQ-09/RQ-11 详情见 `outputs/reports/receipt_quality_policy_v21_report.md`。

## 6. 是否进入模型 replay
fulfillment_delivery_policy_v21 建议进入模型 replay：current-turn gating 修掉了主要历史关键词误触发，stable replay 可作为主指标。

## 7. receipt_quality 是否仍需训练师校准
receipt_quality_policy_v21 仍建议先离线校准：图片/原因/比例/数量等前置 guard 牵涉训练师口径，challenge replay 应先人工看。

## 8. stable vs challenge replay
- FD stable/challenge: `71` / `50`
- RQ stable/challenge: `75` / `45`
- stable replay：gold 与 oracle same/canonical_same，作为自动主指标。
- challenge replay：gold/oracle 冲突，给训练师校准，不混入主指标。

## 9. 下一步如何跑 baseline vs skill
使用 stable 的 baseline_inputs / skill_inputs 分别调用同一模型，输出 model_outputs.jsonl 后运行 `flow_skill_policy_v21/replay/evaluate_replay_outputs_v21.py`。challenge 集只做分析，不作为主分数。
