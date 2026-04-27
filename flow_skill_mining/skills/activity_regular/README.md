# 活动场景-常规活动问题

- support cases: `363`
- high confidence rules: `20`
- eval cases: `37`

## 高置信依据
- `rule_cafac31978bc` support=66 confidence=1.0 expected=无
- `rule_d3ad8dc2980b` support=34 confidence=1.0 expected=无
- `rule_d5c71d92dbed` support=22 confidence=1.0 expected=无
- `rule_d00e5c970d43` support=6 confidence=1.0 expected=无
- `rule_52a71cf00807` support=6 confidence=1.0 expected=无
- `rule_18a3345dfd85` support=5 confidence=1.0 expected=无
- `rule_8e77a4676279` support=5 confidence=1.0 expected=无
- `rule_e7f3b00ed83e` support=5 confidence=1.0 expected=无
- `rule_18347cce3caa` support=4 confidence=1.0 expected=无
- `rule_30d2ed9e444a` support=4 confidence=1.0 expected=无
- `rule_95cc8d8c9bb9` support=4 confidence=1.0 expected=无
- `rule_8abf4dcf0453` support=4 confidence=1.0 expected=操作赔付-优惠券-5元
- `rule_fe40680be751` support=3 confidence=1.0 expected=无
- `rule_d52e77da59dc` support=30 confidence=0.9333 expected=无
- `rule_831088663cb1` support=13 confidence=0.9231 expected=无
- `rule_76b346f61d08` support=5 confidence=0.8 expected=无
- `rule_1a35103de8fb` support=5 confidence=0.8 expected=无
- `rule_78e060480378` support=4 confidence=0.75 expected=无
- `rule_5a8a41535249` support=7 confidence=0.7143 expected=无
- `rule_ea8143a20d13` support=7 confidence=0.7143 expected=无

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
