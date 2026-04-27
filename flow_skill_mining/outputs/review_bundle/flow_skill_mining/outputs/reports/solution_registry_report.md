# Solution Registry 报告

- solution 数: `32`
## pattern_type 分布
- `exact`: `24`
- `call_rider`: `2`
- `call_store`: `2`
- `refund_percent`: `1`
- `compensation_coupon`: `1`
- `compensation_shipping_coupon`: `1`
- `self_service_view`: `1`

## ResponseSolution raw top 30
- `无`: `9712`
- `选择商品`: `734`
- `小象单商品退款-100%`: `475`
- `取消订单`: `343`
- `操作赔付-优惠券-3元`: `188`
- `小象单商品退款-50%`: `187`
- `催促退款审核;退审跟单`: `141`
- `引导自助修改订单`: `121`
- `操作赔付-优惠券-8元`: `114`
- `操作赔付-优惠券-5元`: `111`
- `会员卡退款`: `105`
- `外呼骑手-协商调换货品`: `98`
- `开发票`: `96`
- `小象单商品退款-30%`: `88`
- `管理会员自动续费`: `88`
- `小象单商品退款-20%`: `69`
- `操作赔付-优惠券-10元`: `65`
- `小象整单申请退款`: `55`
- `操作赔付-优惠券-15元`: `51`
- `小象单商品退款-40%`: `50`
- `加急催促退款审核`: `47`
- `系统催单`: `44`
- `小象单商品退款-10%`: `37`
- `智能跟单`: `36`
- `外呼骑手-催促配送`: `33`
- `小象单商品退款-70%`: `32`
- `再次外呼骑手-协商调换货品`: `31`
- `小象单商品退款-80%`: `31`
- `操作赔付-优惠券-20元`: `28`
- `引导自助联系骑手`: `27`

## DialogueAgreeSolution raw top 30
- `无`: `12611`
- `小象单商品退款-100%`: `273`
- `取消订单`: `132`
- `操作赔付-优惠券-3元`: `64`
- `小象单商品退款-50%`: `60`
- `外呼骑手-协商调换货品`: `48`
- `会员卡退款`: `48`
- `操作赔付-优惠券-8元`: `41`
- `操作赔付-优惠券-5元`: `35`
- `小象整单申请退款`: `27`
- `操作赔付-优惠券-10元`: `21`
- `外呼骑手-修改订单`: `21`
- `小象单商品退款-80%`: `20`
- `小象单商品退款-30%`: `17`
- `操作赔付-优惠券-15元`: `16`
- `小象单商品退款-20%`: `15`
- `操作赔付-优惠券-20元`: `13`
- `小象单商品退款-70%`: `13`
- `催促退款审核`: `11`
- `小象单商品退款-40%`: `10`
- `外呼门店-修改订单`: `8`
- `小象单商品退款-60%`: `8`
- `操作赔付-运费券-3元`: `6`
- `小象单商品退款-10%`: `6`

## 规则判断与数据表现冲突
- `催促退款审核`: rule=False, data=True, response=158, agree=11
- `外呼骑手-xx`: rule=False, data=True, response=166, agree=69
- `外呼门店-xx`: rule=False, data=True, response=15, agree=8

## Top solutions
- `小象单商品退款-xx%` (refund_percent): available=13524, response=992, agree=422, rule=True, data=True
- `选择商品` (exact): available=13524, response=734, agree=0, rule=False, data=False
- `操作赔付-优惠券-xx元` (compensation_coupon): available=13524, response=565, agree=190, rule=True, data=True
- `取消订单` (exact): available=13524, response=343, agree=132, rule=True, data=True
- `外呼骑手-xx` (call_rider): available=13524, response=166, agree=69, rule=False, data=True
- `催促退款审核` (exact): available=13524, response=158, agree=11, rule=False, data=True
- `退审跟单` (exact): available=13524, response=149, agree=0, rule=False, data=False
- `引导自助修改订单` (exact): available=13524, response=121, agree=0, rule=False, data=False
- `会员卡退款` (exact): available=13524, response=105, agree=48, rule=True, data=True
- `开发票` (exact): available=13524, response=96, agree=0, rule=False, data=False
- `管理会员自动续费` (exact): available=13524, response=88, agree=0, rule=False, data=False
- `再次外呼骑手-xx` (call_rider): available=13524, response=78, agree=0, rule=False, data=False
- `小象整单申请退款` (exact): available=13524, response=55, agree=27, rule=True, data=True
- `加急催促退款审核` (exact): available=13524, response=47, agree=0, rule=False, data=False
- `智能跟单` (exact): available=13524, response=44, agree=0, rule=False, data=False
- `系统催单` (exact): available=13524, response=44, agree=0, rule=False, data=False
- `引导自助联系骑手` (exact): available=13524, response=27, agree=0, rule=False, data=False
- `发送送达图片` (exact): available=13524, response=26, agree=0, rule=False, data=False
- `无骑手接单跟单` (exact): available=13524, response=26, agree=0, rule=None, data=False
- `引导自助查看会员权益` (exact): available=0, response=18, agree=0, rule=None, data=False
- `外呼门店-xx` (call_store): available=13524, response=15, agree=8, rule=False, data=True
- `操作赔付-运费券-3元` (compensation_shipping_coupon): available=13524, response=15, agree=6, rule=True, data=True
- `加急调度` (exact): available=13524, response=13, agree=0, rule=False, data=False
- `引导自助查看配送范围` (exact): available=0, response=12, agree=0, rule=None, data=False
- `再次外呼门店-xx` (call_store): available=13524, response=7, agree=0, rule=False, data=None
- `引导自助开通会员` (exact): available=13524, response=5, agree=0, rule=False, data=None
- `引导自助查看小象开通城市` (exact): available=0, response=5, agree=0, rule=None, data=None
- `引导自助查看优惠券` (exact): available=0, response=4, agree=0, rule=None, data=None
- `引导自助管理地址` (exact): available=13524, response=2, agree=0, rule=False, data=None
- `投诉骑手` (exact): available=13524, response=1, agree=0, rule=None, data=None
- `操作赔付-优惠券-8元:智能跟单` (exact): available=0, response=1, agree=0, rule=None, data=None
- `引导自助查看-xx` (self_service_view): available=13524, response=0, agree=0, rule=False, data=None
