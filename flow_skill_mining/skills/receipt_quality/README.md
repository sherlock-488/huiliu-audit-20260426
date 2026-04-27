# 收货场景-品质问题

- support cases: `2565`
- high confidence rules: `30`
- eval cases: `176`

## 高置信依据
- `rule_f238fa329e86` support=97 confidence=1.0 expected=无
- `rule_e0af306056a7` support=62 confidence=1.0 expected=无
- `rule_50bf6b0054eb` support=22 confidence=1.0 expected=小象单商品退款-100%
- `rule_3fea30b4eb52` support=22 confidence=1.0 expected=无
- `rule_58c94abfd28d` support=19 confidence=1.0 expected=小象单商品退款-100%
- `rule_cf0085254a2b` support=18 confidence=1.0 expected=无
- `rule_42180ea6d507` support=16 confidence=1.0 expected=无
- `rule_016678251e96` support=14 confidence=1.0 expected=无
- `rule_011b5f030c44` support=13 confidence=1.0 expected=小象单商品退款-50%
- `rule_2a6ae64428d9` support=13 confidence=1.0 expected=无
- `rule_b04d4d1806e1` support=11 confidence=1.0 expected=无
- `rule_1a340a256636` support=10 confidence=1.0 expected=小象单商品退款-100%
- `rule_1ef55bf3bf72` support=10 confidence=1.0 expected=小象单商品退款-100%
- `rule_2ffbcb3284ce` support=10 confidence=1.0 expected=无
- `rule_a32a29c82c34` support=9 confidence=1.0 expected=小象单商品退款-100%
- `rule_1cab46422c71` support=9 confidence=1.0 expected=小象单商品退款-100%
- `rule_4d17bf20b4f0` support=8 confidence=1.0 expected=小象单商品退款-20%
- `rule_f7c37d65df54` support=8 confidence=1.0 expected=无
- `rule_6fc63911c42a` support=7 confidence=1.0 expected=无
- `rule_c479c44e7089` support=7 confidence=1.0 expected=小象单商品退款-30%

## 需要训练师确认
- 暂无。

## 离线 replay
- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。
