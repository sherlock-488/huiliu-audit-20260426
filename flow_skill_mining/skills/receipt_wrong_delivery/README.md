# 收货场景-错送问题

- support cases: `534`
- high confidence rules: `28`
- eval cases: `155`

## 高置信依据
- `rule_cc8d3cf09844` support=10 confidence=1.0 expected=无
- `rule_79978e0cb571` support=10 confidence=1.0 expected=无
- `rule_202c4fa72c44` support=9 confidence=1.0 expected=无
- `rule_b6bd844d5029` support=7 confidence=1.0 expected=无
- `rule_d30bc2befb5d` support=6 confidence=1.0 expected=小象单商品退款-100%
- `rule_2b84de8c34d0` support=6 confidence=1.0 expected=无
- `rule_dcda1478d1dc` support=5 confidence=1.0 expected=无
- `rule_85cab776b62e` support=4 confidence=1.0 expected=选择商品
- `rule_8889b82e5058` support=4 confidence=1.0 expected=小象整单申请退款
- `rule_84ca0d705842` support=4 confidence=1.0 expected=小象单商品退款-100%
- `rule_d58ed59a9534` support=4 confidence=1.0 expected=无
- `rule_96d188f5b383` support=4 confidence=1.0 expected=小象单商品退款-100%
- `rule_184dd6c20b22` support=3 confidence=1.0 expected=无
- `rule_70f0cb7b0661` support=3 confidence=1.0 expected=无
- `rule_f7f604b7be08` support=3 confidence=1.0 expected=无
- `rule_71fca6926e19` support=3 confidence=1.0 expected=无
- `rule_6298629e2eb9` support=3 confidence=1.0 expected=无
- `rule_eba81346403c` support=3 confidence=1.0 expected=无
- `rule_87591ca4c206` support=3 confidence=1.0 expected=小象单商品退款-50%
- `rule_0cfcabb2c035` support=3 confidence=1.0 expected=无

## 需要训练师确认
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `外呼骑手-协商调换货品` 与其他动作存在分歧，需要确认。

## 离线 replay
- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。
