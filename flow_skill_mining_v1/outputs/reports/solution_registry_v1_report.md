# Solution Registry v1 报告

- 输入 CaseRecord: `/Users/sherlock/Desktop/01_项目代码/回流/flow_skill_mining/outputs/case_records.jsonl`
- canonical solution 数: `31`
- alias 修正 solution 数: `4`
- 历史红包口径映射数: `0`
- 冒号疑似复合脏格式 raw 数: `1`

## confirmation level 分布
- `no_confirmation_required`: `18`
- `strong_confirmation_required`: `6`
- `user_request_is_enough`: `6`
- `unclear`: `1`

## pattern_type 分布
- `exact`: `21`
- `self_service_view`: `5`
- `call_rider`: `2`
- `call_store`: `2`
- `compensation_shipping_coupon`: `1`

## Alias 修正
- `小象单商品退款-xx%` aliases=['小象单商品退款-30%', '小象单商品退款-20%', '小象单商品退款-40%', '小象单商品退款-50%', '小象单商品退款-100%', '小象单商品退款-80%', '小象单商品退款-70%', '小象单商品退款-60%', '小象单商品退款-10%'] notes=[]
- `操作赔付-优惠券-xx元` aliases=['操作赔付-优惠券-10元', '操作赔付-优惠券-15元', '操作赔付-优惠券-20元', '操作赔付-优惠券-8元', '操作赔付-优惠券-5元', '操作赔付-优惠券-3元'] notes=[]
- `外呼骑手-xx` aliases=['外呼骑手-催促配送', '外呼骑手-协商调换货品', '外呼骑手-修改订单', '外呼骑手-核实情况'] notes=[]
- `再次外呼骑手-xx` aliases=['再次外呼骑手-催促配送', '再次外呼骑手-协商调换货品', '再次外呼骑手-修改订单', '再次外呼骑手-核实情况'] notes=[]
- `引导自助查看-会员权益` aliases=['引导自助查看会员权益'] notes=['missing_dash_alias']
- `外呼门店-xx` aliases=['外呼门店-修改订单'] notes=[]
- `引导自助查看-配送范围` aliases=['引导自助查看配送范围'] notes=['missing_dash_alias']
- `再次外呼门店-xx` aliases=['再次外呼门店-修改订单'] notes=[]
- `引导自助查看-小象开通城市` aliases=['引导自助查看小象开通城市'] notes=['missing_dash_alias']
- `引导自助查看-优惠券` aliases=['引导自助查看优惠券'] notes=['missing_dash_alias']

## 冒号疑似复合脏格式
- `colon_composite:操作赔付-优惠券-8元:智能跟单`: `1`

## 数据表现和初始规则冲突，需训练师确认
- 暂无明显冲突。

## Registry 明细
- `小象单商品退款-xx%` type=exact level=strong_confirmation_required available=13524 response=992 agree=422 rate=0.4254
- `选择商品` type=exact level=no_confirmation_required available=13524 response=734 agree=0 rate=0.0
- `操作赔付-优惠券-xx元` type=exact level=strong_confirmation_required available=13524 response=566 agree=190 rate=0.3357
- `取消订单` type=exact level=strong_confirmation_required available=13524 response=343 agree=132 rate=0.3848
- `外呼骑手-xx` type=call_rider level=user_request_is_enough available=13524 response=166 agree=69 rate=0.4157
- `催促退款审核` type=exact level=user_request_is_enough available=13524 response=158 agree=11 rate=0.0696
- `退审跟单` type=exact level=no_confirmation_required available=13524 response=149 agree=0 rate=0.0
- `引导自助修改订单` type=exact level=no_confirmation_required available=13524 response=121 agree=0 rate=0.0
- `会员卡退款` type=exact level=strong_confirmation_required available=13524 response=105 agree=48 rate=0.4571
- `开发票` type=exact level=no_confirmation_required available=13524 response=96 agree=0 rate=0.0
- `管理会员自动续费` type=exact level=no_confirmation_required available=13524 response=88 agree=0 rate=0.0
- `再次外呼骑手-xx` type=call_rider level=user_request_is_enough available=13524 response=78 agree=0 rate=0.0
- `小象整单申请退款` type=exact level=strong_confirmation_required available=13524 response=55 agree=27 rate=0.4909
- `加急催促退款审核` type=exact level=user_request_is_enough available=13524 response=47 agree=0 rate=0.0
- `智能跟单` type=exact level=no_confirmation_required available=13524 response=45 agree=0 rate=0.0
- `系统催单` type=exact level=no_confirmation_required available=13524 response=44 agree=0 rate=0.0
- `引导自助联系骑手` type=exact level=no_confirmation_required available=13524 response=27 agree=0 rate=0.0
- `发送送达图片` type=exact level=no_confirmation_required available=13524 response=26 agree=0 rate=0.0
- `无骑手接单跟单` type=exact level=no_confirmation_required available=13524 response=26 agree=0 rate=0.0
- `引导自助查看-会员权益` type=self_service_view level=no_confirmation_required available=0 response=18 agree=0 rate=0.0
- `外呼门店-xx` type=call_store level=user_request_is_enough available=13524 response=15 agree=8 rate=0.5333
- `操作赔付-运费券-3元` type=compensation_shipping_coupon level=strong_confirmation_required available=13524 response=15 agree=6 rate=0.4
- `加急调度` type=exact level=no_confirmation_required available=13524 response=13 agree=0 rate=0.0
- `引导自助查看-配送范围` type=self_service_view level=no_confirmation_required available=0 response=12 agree=0 rate=0.0
- `再次外呼门店-xx` type=call_store level=user_request_is_enough available=13524 response=7 agree=0 rate=0.0
- `引导自助开通会员` type=exact level=no_confirmation_required available=13524 response=5 agree=0 rate=0.0
- `引导自助查看-小象开通城市` type=self_service_view level=no_confirmation_required available=0 response=5 agree=0 rate=0.0
- `引导自助查看-优惠券` type=self_service_view level=no_confirmation_required available=0 response=4 agree=0 rate=0.0
- `引导自助管理地址` type=exact level=no_confirmation_required available=13524 response=2 agree=0 rate=0.0
- `投诉骑手` type=exact level=unclear available=13524 response=1 agree=0 rate=0.0
- `引导自助查看-xx` type=self_service_view level=no_confirmation_required available=13524 response=0 agree=0 rate=0.0
