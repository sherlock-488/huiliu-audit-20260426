# receipt_quality_policy_v2

- scene: `收货场景-品质问题`
- positive_cases: `2565`
- eval_cases: `120`
- recommendation: 仅建议 offline replay 和训练师校准，暂不建议线上。

## Open Questions
- 哪些品质子类必须图片前置，哪些可以仅凭文字描述进入退款？
- 建议退款比例缺失时，是否允许客服先提出经验比例，还是必须追问？
- 赔付与退款可以同轮复合输出的边界是什么？
- 多数量商品用户只说“这个坏了”时，是否默认 1 件还是必须询问数量？
