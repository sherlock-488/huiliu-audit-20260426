# 会员场景-续费问题

- support cases: `405`
- high confidence rules: `23`
- eval cases: `49`

## 高置信依据
- `rule_15223f839315` support=98 confidence=1.0 expected=无
- `rule_a42d172fe47c` support=47 confidence=1.0 expected=无
- `rule_60b9fe7d9d55` support=12 confidence=1.0 expected=无
- `rule_6b9c1e4bd736` support=10 confidence=1.0 expected=无
- `rule_b9c99455a9e8` support=8 confidence=1.0 expected=无
- `rule_c2f43b9eee0f` support=7 confidence=1.0 expected=无
- `rule_fdc00e7bf2b2` support=6 confidence=1.0 expected=无
- `rule_9b772340e0ea` support=5 confidence=1.0 expected=无
- `rule_e2b4648590b7` support=5 confidence=1.0 expected=无
- `rule_3cfc91830233` support=3 confidence=1.0 expected=无
- `rule_2caf38740bf1` support=3 confidence=1.0 expected=无
- `rule_4e2431d5e549` support=3 confidence=1.0 expected=无
- `rule_b6aaa12c1fd9` support=2 confidence=1.0 expected=会员卡退款
- `rule_f3f9f52b1d35` support=28 confidence=0.8571 expected=无
- `rule_a38c85ae4c2d` support=14 confidence=0.8571 expected=无
- `rule_180a8bbbf256` support=86 confidence=0.8488 expected=无
- `rule_ae0c1850d585` support=5 confidence=0.8 expected=管理会员自动续费
- `rule_0b59a1427b8d` support=44 confidence=0.7955 expected=无
- `rule_f74bf9029bc6` support=4 confidence=0.75 expected=无
- `rule_7b6f7aac4bec` support=4 confidence=0.75 expected=无

## 需要训练师确认
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `无` 与其他动作存在分歧，需要确认。
- 同一状态下 `管理会员自动续费` 与其他动作存在分歧，需要确认。
- 同一状态下 `管理会员自动续费` 与其他动作存在分歧，需要确认。
- 同一状态下 `管理会员自动续费` 与其他动作存在分歧，需要确认。

## 离线 replay
- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。
