# 会员场景-权益问题

- support cases: `317`
- high confidence rules: `18`
- eval cases: `52`

## 高置信依据
- `rule_beb3ee5d4373` support=24 confidence=1.0 expected=无
- `rule_eb97ebb1e639` support=9 confidence=1.0 expected=无
- `rule_75ec6054f48b` support=5 confidence=1.0 expected=会员卡退款
- `rule_e5987c66fc84` support=5 confidence=1.0 expected=无
- `rule_e6f8357279bc` support=5 confidence=1.0 expected=无
- `rule_f926b4396bc0` support=4 confidence=1.0 expected=无
- `rule_39c2ef02d449` support=4 confidence=1.0 expected=无
- `rule_46e5a91dcced` support=4 confidence=1.0 expected=无
- `rule_a187a099f9ab` support=4 confidence=1.0 expected=无
- `rule_4b4a6e5a7df0` support=3 confidence=1.0 expected=无
- `rule_4882b9ea4d3d` support=61 confidence=0.9836 expected=无
- `rule_b6cde9e6dad7` support=12 confidence=0.9167 expected=无
- `rule_f56de6993eda` support=9 confidence=0.8889 expected=无
- `rule_92d6038843d6` support=24 confidence=0.875 expected=无
- `rule_bf8cb397249e` support=27 confidence=0.8519 expected=无
- `rule_247603ccfb99` support=13 confidence=0.8462 expected=无
- `rule_9333988fee53` support=31 confidence=0.8387 expected=无
- `rule_57c3b60a96fe` support=4 confidence=0.75 expected=无

## 需要训练师确认
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。

## 离线 replay
- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。
