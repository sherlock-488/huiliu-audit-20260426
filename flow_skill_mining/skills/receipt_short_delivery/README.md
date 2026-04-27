# 收货场景-少送问题

- support cases: `817`
- high confidence rules: `30`
- eval cases: `128`

## 高置信依据
- `rule_4528f76d60ec` support=91 confidence=1.0 expected=无
- `rule_a03a7ce49e29` support=21 confidence=1.0 expected=无
- `rule_913f32343c86` support=19 confidence=1.0 expected=选择商品
- `rule_e91cd115a385` support=18 confidence=1.0 expected=小象单商品退款-100%
- `rule_5cecb7fe01b9` support=16 confidence=1.0 expected=小象单商品退款-100%
- `rule_b005bb65c80a` support=14 confidence=1.0 expected=无
- `rule_6ed944762a22` support=11 confidence=1.0 expected=操作赔付-优惠券-3元
- `rule_7d1da703a6f1` support=10 confidence=1.0 expected=操作赔付-优惠券-3元
- `rule_bf85dbcb4b02` support=7 confidence=1.0 expected=操作赔付-优惠券-3元
- `rule_b0b5336217ee` support=6 confidence=1.0 expected=无
- `rule_4e4693d45e88` support=6 confidence=1.0 expected=选择商品
- `rule_bfbb8402ecf7` support=6 confidence=1.0 expected=无
- `rule_a7e4966ef249` support=6 confidence=1.0 expected=无
- `rule_849ed3912646` support=5 confidence=1.0 expected=小象单商品退款-100%
- `rule_39faa9bc5903` support=5 confidence=1.0 expected=小象单商品退款-100%
- `rule_5f23a0d58af6` support=5 confidence=1.0 expected=无
- `rule_bf62bb30ed07` support=5 confidence=1.0 expected=无
- `rule_e61c260c54bf` support=5 confidence=1.0 expected=无
- `rule_d88509b62fdc` support=4 confidence=1.0 expected=无
- `rule_4a9a237ec3e4` support=4 confidence=1.0 expected=选择商品

## 需要训练师确认
- 暂无。

## 离线 replay
- 使用 `eval_cases.jsonl` 输入现有模型，比较 ResponseSolution / DialogueAgreeSolution 与 checker 结果。
