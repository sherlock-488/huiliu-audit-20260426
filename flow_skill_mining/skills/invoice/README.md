# 发票场景

- support cases: `578`
- high confidence rules: `29`
- eval cases: `45`

## 高置信依据
- `rule_55341fe862d3` support=109 confidence=1.0 expected=无
- `rule_13133abddc42` support=55 confidence=1.0 expected=无
- `rule_5a9502a47f9c` support=27 confidence=1.0 expected=无
- `rule_404951840ace` support=25 confidence=1.0 expected=无
- `rule_0e562e8f4432` support=11 confidence=1.0 expected=无
- `rule_9864e2585d27` support=8 confidence=1.0 expected=无
- `rule_e75a5679d649` support=5 confidence=1.0 expected=无
- `rule_9662889d9e85` support=5 confidence=1.0 expected=开发票
- `rule_75a59f65f450` support=5 confidence=1.0 expected=无
- `rule_0164cdb1a4f9` support=5 confidence=1.0 expected=无
- `rule_922b1608ad93` support=4 confidence=1.0 expected=无
- `rule_632c6e694549` support=4 confidence=1.0 expected=无
- `rule_97abf093db32` support=3 confidence=1.0 expected=无
- `rule_c753d1b51f92` support=3 confidence=1.0 expected=无
- `rule_614bb62c8715` support=3 confidence=1.0 expected=无
- `rule_6c0eb3cc69bb` support=3 confidence=1.0 expected=开发票
- `rule_87dbbe0421f1` support=3 confidence=1.0 expected=无
- `rule_58b60ed43ac5` support=3 confidence=1.0 expected=无
- `rule_8958509c409b` support=11 confidence=0.9091 expected=无
- `rule_ac1da66fdf9f` support=109 confidence=0.9083 expected=无

## 需要训练师确认
- 同一状态下 `无` 与其他动作存在分歧，需要确认。

## 离线 replay
- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。
