# 收货场景-退款问题

- support cases: `395`
- high confidence rules: `30`
- eval cases: `68`

## 高置信依据
- `rule_deeb4b6ccbf1` support=56 confidence=1.0 expected=无
- `rule_65336b2af23c` support=11 confidence=1.0 expected=无
- `rule_7f595b81d3c0` support=10 confidence=1.0 expected=无
- `rule_f1c2d9542ab5` support=7 confidence=1.0 expected=无
- `rule_df1111c3c2a9` support=6 confidence=1.0 expected=无
- `rule_0dfae4dbdb91` support=5 confidence=1.0 expected=无
- `rule_97f8d71aa666` support=5 confidence=1.0 expected=选择商品
- `rule_20c112d5d826` support=5 confidence=1.0 expected=无
- `rule_26441841816e` support=5 confidence=1.0 expected=无
- `rule_56cc89c0ad01` support=5 confidence=1.0 expected=无
- `rule_c8caa6d4fe21` support=5 confidence=1.0 expected=无
- `rule_0e3b34232107` support=4 confidence=1.0 expected=无
- `rule_ce0e01ddc100` support=4 confidence=1.0 expected=无
- `rule_37b323eabc99` support=4 confidence=1.0 expected=无
- `rule_f59f874a88a3` support=4 confidence=1.0 expected=无
- `rule_97123253d280` support=4 confidence=1.0 expected=无
- `rule_12d9f953249b` support=3 confidence=1.0 expected=无
- `rule_6ca5bcb5edf8` support=3 confidence=1.0 expected=无
- `rule_8822071698f7` support=3 confidence=1.0 expected=无
- `rule_15cffec575a0` support=3 confidence=1.0 expected=无

## 需要训练师确认
- 暂无。

## 离线 replay
- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。
