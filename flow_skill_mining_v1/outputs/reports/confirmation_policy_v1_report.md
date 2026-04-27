# Confirmation Policy v1 报告

## 三分层汇总
- `strong_confirmation_required`: solutions=6 response=2076 agree=825 rate=39.74%
- `no_confirmation_required`: solutions=18 response=1415 agree=0 rate=0.00%
- `user_request_is_enough`: solutions=6 response=471 agree=88 rate=18.68%
- `unclear`: solutions=1 response=1 agree=0 rate=0.00%

## strong confirmation 方案
- `小象单商品退款-xx%` response=992 agree=422 rate=0.4254
- `操作赔付-优惠券-xx元` response=566 agree=190 rate=0.3357
- `取消订单` response=343 agree=132 rate=0.3848
- `会员卡退款` response=105 agree=48 rate=0.4571
- `小象整单申请退款` response=55 agree=27 rate=0.4909
- `操作赔付-运费券-3元` response=15 agree=6 rate=0.4

## user request is enough 方案
- `外呼骑手-xx` response=166 agree=69 rate=0.4157
- `催促退款审核` response=158 agree=11 rate=0.0696
- `再次外呼骑手-xx` response=78 agree=0 rate=0.0
- `加急催促退款审核` response=47 agree=0 rate=0.0
- `外呼门店-xx` response=15 agree=8 rate=0.5333
- `再次外呼门店-xx` response=7 agree=0 rate=0.0

## no confirmation 方案
- `选择商品` response=734 agree=0 rate=0.0
- `退审跟单` response=149 agree=0 rate=0.0
- `引导自助修改订单` response=121 agree=0 rate=0.0
- `开发票` response=96 agree=0 rate=0.0
- `管理会员自动续费` response=88 agree=0 rate=0.0
- `智能跟单` response=45 agree=0 rate=0.0
- `系统催单` response=44 agree=0 rate=0.0
- `引导自助联系骑手` response=27 agree=0 rate=0.0
- `发送送达图片` response=26 agree=0 rate=0.0
- `无骑手接单跟单` response=26 agree=0 rate=0.0
- `引导自助查看-会员权益` response=18 agree=0 rate=0.0
- `加急调度` response=13 agree=0 rate=0.0
- `引导自助查看-配送范围` response=12 agree=0 rate=0.0
- `引导自助开通会员` response=5 agree=0 rate=0.0
- `引导自助查看-小象开通城市` response=5 agree=0 rate=0.0
- `引导自助查看-优惠券` response=4 agree=0 rate=0.0
- `引导自助管理地址` response=2 agree=0 rate=0.0
- `引导自助查看-xx` response=0 agree=0 rate=0.0

## unmatched DialogueAgreeSolution TOP 50
- 暂无。

## 需要训练师确认
- 部分 strong_confirmation_required 的 DialogueAgreeSolution 缺少显式确认词，需要抽样判断口语确认覆盖。
- user_request_is_enough 类方案可将 DialogueAgreeSolution 视为授权证据，但不要求非空。
