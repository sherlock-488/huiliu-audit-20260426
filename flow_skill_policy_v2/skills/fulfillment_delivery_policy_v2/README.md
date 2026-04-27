# fulfillment_delivery_policy_v2

- scene: `履约场景-配送问题`
- positive_cases: `1893`
- eval_cases: `121`
- recommendation: 允许进入 baseline vs skill 模型 replay。

## Open Questions
- 普通 ETA 咨询但 rider_status=无骑手接单时，是否总应加急调度，还是先解释预计时间？
- 系统催单与智能跟单是否允许同轮复合输出，还是主 ResponseSolution 只保留系统催单？
- 配送超时赔付的优惠券档位应取信号区间上限、下限，还是由训练师根据用户分层决定？
- 用户要求客服联系骑手时，优先外呼还是先引导自助联系的边界需确认。
