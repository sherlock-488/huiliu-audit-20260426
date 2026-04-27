# README_FOR_GPT - flow_skill_policy_v22

## Git Context
- branch: `main`
- commit: `dab4933e68c300e25e6a66b7ec0cef67009860c9`

## 本轮目标
构建 `flow_skill_policy_v22`，在 v21 current-turn gating 的基础上提升配送/品质短句召回，收紧弱确认，并补齐 stable/action-focused/challenge replay 与 baseline/skill 输入样本。

## 已完成任务
- 增强 `current_turn_intent`：补充“怎么还没配送、急、5分钟？”等配送短句，以及“漏的、空心、碎的、臭、干瘪、不能吃”等品质短句。
- 新增 `is_pure_confirm` / `maybe_accept_pending`，避免“嗯，什么时候退完给我啊”被误作退款确认。
- 新增 safe context bridge，只在极短追问/短催促且上下文同主题时增强 intent。
- 生成 v22 oracle、stable replay、challenge replay、action-focused replay，以及 baseline/skill prompt 输入 sample。
- 生成两个 v22 skill pack：履约配送、收货品质。

## 关键摘要
- FD conflict v21 -> v22: `50 -> 45`
- RQ conflict v21 -> v22: `45 -> 41`
- FD-OTHER v21 -> v22: `27 -> 20`
- RQ-OTHER v21 -> v22: `30 -> 23`
- close/ack over-action v22: `0`
- strong confirmation over-trigger v22: `2`
- FD stable/action/challenge cases: `76 / 65 / 45`
- RQ stable/action/challenge cases: `79 / 79 / 41`

## 请 GPT 重点审阅
1. `current_turn_intent_v22` 的新增词表是否会重新引入误触发，尤其“急/5分钟/就这样吧”。
2. `confirmation_resolver_v22` 是否足够收紧弱确认，是否漏掉真实“同意退款/赔付/取消”。
3. `fulfillment_delivery_policy_v22` 是否适合进入正式 baseline vs skill replay。
4. `receipt_quality_policy_v22` 的前置 guard 是否仍过严，尤其图片/商品选择/退款比例。
5. `action-focused replay` 是否适合作为动作召回观察集，而不是主自动指标。
6. `skill_prompt.md` 是否适合插入现有 prompt，是否过度泄漏 oracle 口径。

## 我不确定、需要判断的问题
- “5分钟？”是否总应视为 ETA 追问，还是要区分用户接受/质疑。
- “行吧/就这样吧”在 pending refund/compensation/cancel 时是否可作为确认。
- 当前图片识别文本是否可以等价视为已上传图片凭证。
- 品质问题中用户直接说商品缺陷但未显式选商品时，是否应先 `选择商品`。

## GPT 必看入口
- `flow_skill_policy_v22/README_REPORT.md`
- `flow_skill_policy_v22/outputs/reports/current_turn_intent_v22_report.md`
- `flow_skill_policy_v22/outputs/reports/confirmation_resolver_v22_report.md`
- `flow_skill_policy_v22/outputs/reports/policy_oracle_v22_report.md`
- `flow_skill_policy_v22/skills/fulfillment_delivery_policy_v22/skill_prompt.md`
- `flow_skill_policy_v22/skills/receipt_quality_policy_v22/skill_prompt.md`
- `review_samples/*.jsonl`
