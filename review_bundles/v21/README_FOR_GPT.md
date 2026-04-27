# README FOR GPT: flow_skill_policy_v21 Review Bundle

## Git State
- base commit before v21 staging: `157a15294f33264c420a86e3b56344d452508cd1`
- branch: `main`

## 本轮目标
修正 v2 oracle 过度触发动作的问题，核心是 current-turn gating：动作只由当前最后一条用户消息触发，历史只用于 pending confirmation / 外呼结果等上下文证据。

## 已完成
- 新增 `current_turn_intent.py`，只看 last_user_query。
- 新增 `confirmation_resolver.py`，弱确认必须结合 pending strong solution。
- 修正 normalizer：未选商品不再聚合 item 状态误判不可退。
- 修正 eligibility / FD / RQ policy。
- 重建 v21 oracle、stable/challenge replay、skills、trainer review pack。

## 关键指标
```text
# Fulfillment Delivery Policy v21 Report

- conflict_v2: `65`
- conflict_v21: `50`
- oracle_no_gold_action_v2: `30`
- oracle_no_gold_action_v21: `8`
- close_ack_transfer_over_action_v2: `12`
- close_ack_transfer_over_action_v21: `0`
- close_ack_transfer_fixed: `20`

# Receipt Quality Policy v21 Report

- conflict_v2: `72`
- conflict_v21: `45`
- oracle_no_gold_action_v2: `21`
- oracle_no_gold_action_v21: `3`
- close_ack_transfer_over_action_v2: `11`
- close_ack_transfer_over_action_v21: `0`
- close_ack_transfer_fixed: `17`

# Replay Sets v21 Report

- fulfillment_delivery stable/challenge: `71` / `50`
- receipt_quality stable/challenge: `75` / `45`
- FD DialogueAgree non-empty stable/challenge: `5` / `7`
- RQ DialogueAgree non-empty stable/challenge: `23` / `7`
```

## 请 GPT 重点审阅
1. current-turn gating 是否过严，会不会漏掉真实短句追问。
2. weak ack + pending strong solution 的确认逻辑是否合理。
3. FD-03 / FD-05A / FD-08 剩余冲突是否合理。
4. RQ-01 / RQ-09 / RQ-CONFIRM 剩余冲突是否合理。
5. stable replay 是否可作为主指标，challenge 是否足够用于训练师校准。
6. 两个 skill_prompt 是否适合插入现有 prompt。
