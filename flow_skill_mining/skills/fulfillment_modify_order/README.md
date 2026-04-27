# 履约场景-修改订单问题

- support cases: `1933`
- high confidence rules: `30`
- eval cases: `167`

## 高置信依据
- `rule_3ec9a5beeb75` support=43 confidence=1.0 expected=无
- `rule_db83c30a9cae` support=38 confidence=1.0 expected=无
- `rule_d30bc4b5a060` support=22 confidence=1.0 expected=无
- `rule_2d1f329c8069` support=21 confidence=1.0 expected=无
- `rule_6d8986ec4313` support=20 confidence=1.0 expected=无
- `rule_c929fd65e82d` support=17 confidence=1.0 expected=无
- `rule_e451e3c5e709` support=17 confidence=1.0 expected=无
- `rule_de7915fb1aca` support=17 confidence=1.0 expected=取消订单
- `rule_a18a8b5098ba` support=15 confidence=1.0 expected=无
- `rule_46776b198390` support=13 confidence=1.0 expected=无
- `rule_a3dd2904f162` support=12 confidence=1.0 expected=无
- `rule_f4359c939f57` support=12 confidence=1.0 expected=无
- `rule_67bb8b8fb4de` support=9 confidence=1.0 expected=无
- `rule_6430e33485b1` support=9 confidence=1.0 expected=无
- `rule_445518f59256` support=9 confidence=1.0 expected=取消订单
- `rule_d67c28b9c644` support=9 confidence=1.0 expected=无
- `rule_679bafb0dfbc` support=9 confidence=1.0 expected=无
- `rule_54ff6f6a24f6` support=8 confidence=1.0 expected=无
- `rule_cffeccb506a0` support=8 confidence=1.0 expected=无
- `rule_dfc745e5cf8e` support=8 confidence=1.0 expected=无

## 需要训练师确认
- 暂无。

## 离线 replay
- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。
