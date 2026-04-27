# FlowState 报告

- FlowState 数: `13524`
- user_intent 是弱规则标签，只用于聚合分析，不能替代训练师 `问题场景`。

## 核心信号覆盖率
- `订单状态`: `12392` (91.63%)
- `是否为配送单`: `12373` (91.49%)
- `是否为自提单`: `12345` (91.28%)
- `订单类型`: `12345` (91.28%)
- `订单骑手状态`: `10988` (81.25%)
- `订单门店状态`: `12319` (91.09%)
- `订单是否超时`: `10988` (81.25%)
- `履约中未超时订单是否有超时风险`: `2541` (18.79%)
- `是否可取消订单`: `12345` (91.28%)
- `订单退款状态`: `11277` (83.39%)
- `订单是否有退款记录`: `11278` (83.39%)
- `订单是否超售后`: `11278` (83.39%)
- `是否赔付过`: `12344` (91.27%)
- `订单是否可赔付`: `6134` (45.36%)
- `用户分层标签`: `13524` (100.00%)
- `是否有骑手真实手机号`: `12345` (91.28%)
- `骑手是否有送达图片`: `1341` (9.92%)
- `是否会员`: `13524` (100.00%)

## 各 scene 的 user_intent 分布 TOP
### 收货场景-品质问题
- `other`: `890`
- `confirm_compensation`: `709`
- `quality_issue`: `295`
- `close_conversation`: `234`
- `transfer_request`: `155`
- `refund_request`: `67`
- `presale_consult`: `38`
- `compensation_request`: `36`
- `delivery_urge`: `32`
- `cancel_request`: `28`
- `short_delivery`: `21`
- `not_received_after_delivered`: `19`
### 履约场景-修改订单问题
- `other`: `1022`
- `close_conversation`: `375`
- `transfer_request`: `200`
- `modify_order`: `119`
- `cancel_request`: `106`
- `eta_question`: `29`
- `presale_consult`: `29`
- `contact_rider`: `15`
- `delivery_urge`: `12`
- `date_issue`: `6`
- `refund_request`: `5`
- `payment_issue`: `2`
### 履约场景-配送问题
- `other`: `955`
- `close_conversation`: `347`
- `delivery_urge`: `141`
- `eta_question`: `128`
- `transfer_request`: `118`
- `contact_rider`: `64`
- `compensation_request`: `39`
- `cancel_request`: `31`
- `not_received_after_delivered`: `16`
- `short_delivery`: `14`
- `payment_issue`: `10`
- `presale_consult`: `10`
### 收货场景-少送问题
- `confirm_compensation`: `258`
- `other`: `252`
- `close_conversation`: `91`
- `short_delivery`: `82`
- `refund_request`: `31`
- `transfer_request`: `29`
- `compensation_request`: `28`
- `not_received_after_delivered`: `14`
- `payment_issue`: `6`
- `delivery_urge`: `6`
- `compensation_accept`: `6`
- `cancel_request`: `4`
### 发票场景
- `other`: `203`
- `invoice_request`: `178`
- `close_conversation`: `109`
- `refund_request`: `21`
- `transfer_request`: `20`
- `member_benefit`: `18`
- `member_auto_renew`: `5`
- `presale_consult`: `5`
- `quality_issue`: `5`
- `modify_order`: `5`
- `activity_coupon`: `2`
- `payment_issue`: `2`
### <MISSING>
- `other`: `249`
- `close_conversation`: `74`
- `quality_issue`: `56`
- `delivery_urge`: `33`
- `transfer_request`: `31`
- `wrong_delivery`: `17`
- `not_received_after_delivered`: `17`
- `refund_request`: `15`
- `invoice_request`: `14`
- `presale_consult`: `11`
- `compensation_request`: `10`
- `short_delivery`: `7`
### 收货场景-错送问题
- `other`: `165`
- `confirm_compensation`: `164`
- `wrong_delivery`: `81`
- `close_conversation`: `48`
- `transfer_request`: `20`
- `delivery_urge`: `17`
- `presale_consult`: `11`
- `refund_request`: `8`
- `not_received_after_delivered`: `5`
- `eta_question`: `5`
- `cancel_request`: `4`
- `short_delivery`: `3`
### 会员场景-续费问题
- `other`: `150`
- `close_conversation`: `98`
- `member_auto_renew`: `65`
- `transfer_request`: `44`
- `member_benefit`: `24`
- `cancel_request`: `12`
- `payment_issue`: `4`
- `delivery_urge`: `2`
- `refund_request`: `2`
- `activity_coupon`: `2`
- `cannot_refund`: `1`
- `compensation_accept`: `1`
### 收货场景-退款问题
- `other`: `110`
- `confirm_refund`: `74`
- `close_conversation`: `56`
- `refund_request`: `43`
- `transfer_request`: `40`
- `refund_progress`: `14`
- `cancel_request`: `12`
- `presale_consult`: `7`
- `delivery_urge`: `6`
- `cannot_refund`: `6`
- `member_benefit`: `5`
- `compensation_request`: `4`
### 活动场景-常规活动问题
- `other`: `175`
- `close_conversation`: `66`
- `activity_coupon`: `48`
- `transfer_request`: `30`
- `member_benefit`: `15`
- `date_issue`: `11`
- `compensation_request`: `8`
- `member_auto_renew`: `3`
- `cancel_request`: `3`
- `presale_consult`: `2`
- `compensation_accept`: `1`
- `eta_question`: `1`
### 会员场景-权益问题
- `other`: `121`
- `close_conversation`: `61`
- `member_benefit`: `58`
- `transfer_request`: `31`
- `member_auto_renew`: `16`
- `activity_coupon`: `8`
- `payment_issue`: `6`
- `compensation_request`: `5`
- `date_issue`: `2`
- `presale_consult`: `2`
- `compensation_accept`: `2`
- `delivery_urge`: `1`
### 收货场景-实描不符问题
- `other`: `172`
- `close_conversation`: `29`
- `transfer_request`: `15`
- `presale_consult`: `14`
- `delivery_urge`: `10`
- `refund_request`: `7`
- `short_delivery`: `7`
- `compensation_accept`: `4`
- `compensation_request`: `3`
- `payment_issue`: `1`
- `activity_coupon`: `1`
- `refund_progress`: `1`
### 会员场景-退卡问题
- `other`: `93`
- `close_conversation`: `66`
- `member_benefit`: `30`
- `transfer_request`: `24`
- `member_auto_renew`: `22`
- `refund_request`: `9`
- `cancel_request`: `7`
- `payment_issue`: `4`
- `activity_coupon`: `3`
- `delivery_urge`: `1`
- `compensation_accept`: `1`
- `compensation_request`: `1`
### 收货场景-催退款进度
- `other`: `86`
- `confirm_refund`: `42`
- `delivery_urge`: `34`
- `refund_progress`: `33`
- `close_conversation`: `29`
- `transfer_request`: `14`
- `refund_request`: `9`
- `presale_consult`: `4`
- `quality_issue`: `1`
- `short_delivery`: `1`
- `cancel_request`: `1`
- `wrong_delivery`: `1`
### 活动场景-通用问题
- `other`: `114`
- `close_conversation`: `33`
- `activity_coupon`: `21`
- `transfer_request`: `13`
- `date_issue`: `13`
- `not_received_after_delivered`: `6`
- `compensation_request`: `6`
- `compensation_accept`: `4`
- `presale_consult`: `3`
- `short_delivery`: `2`
- `cancel_request`: `2`
- `member_auto_renew`: `1`
### 收货场景-重量不足问题
- `other`: `143`
- `close_conversation`: `29`
- `transfer_request`: `13`
- `delivery_urge`: `8`
- `short_delivery`: `6`
- `presale_consult`: `5`
- `compensation_accept`: `4`
- `payment_issue`: `2`
- `compensation_request`: `2`
- `refund_progress`: `2`
- `refund_request`: `2`
- `quality_issue`: `1`
### 其他场景-投诉问题
- `other`: `142`
- `close_conversation`: `28`
- `presale_consult`: `12`
- `transfer_request`: `10`
- `eta_question`: `5`
- `not_received_after_delivered`: `4`
- `activity_coupon`: `4`
- `cancel_request`: `3`
- `delivery_urge`: `3`
- `member_benefit`: `2`
### 履约场景-履约中订单缺货
- `other`: `101`
- `close_conversation`: `44`
- `presale_consult`: `27`
- `transfer_request`: `12`
- `short_delivery`: `8`
- `compensation_request`: `7`
- `cancel_request`: `6`
- `refund_request`: `2`
- `payment_issue`: `1`
- `compensation_accept`: `1`
### 其他场景
- `other`: `99`
- `close_conversation`: `16`
- `transfer_request`: `11`
- `presale_consult`: `5`
- `not_received_after_delivered`: `2`
- `quality_issue`: `2`
- `delivery_urge`: `2`
- `activity_coupon`: `2`
- `compensation_request`: `1`
- `cancel_request`: `1`
### 其他场景-账号问题
- `other`: `90`
- `close_conversation`: `16`
- `presale_consult`: `11`
- `transfer_request`: `8`
- `activity_coupon`: `4`
- `eta_question`: `4`
- `member_benefit`: `3`
- `modify_order`: `1`
- `compensation_request`: `1`
### 长尾场景-金融
- `other`: `64`
- `close_conversation`: `34`
- `payment_issue`: `16`
- `transfer_request`: `6`
- `cancel_request`: `6`
### 金融场景-支付问题
- `other`: `51`
- `close_conversation`: `34`
- `transfer_request`: `12`
- `payment_issue`: `9`
- `member_benefit`: `1`
- `delivery_urge`: `1`
- `date_issue`: `1`
### 会员场景-退卡问题诉求
- `other`: `36`
- `close_conversation`: `18`
- `transfer_request`: `11`
- `member_benefit`: `9`
- `refund_request`: `8`
- `payment_issue`: `4`
- `member_auto_renew`: `4`
- `activity_coupon`: `3`
- `cancel_request`: `2`
- `compensation_accept`: `2`
- `member_refund`: `1`
### 活动场景-省钱卡问题
- `other`: `34`
- `close_conversation`: `12`
- `member_benefit`: `11`
- `compensation_request`: `10`
- `activity_coupon`: `7`
- `transfer_request`: `4`
- `refund_request`: `4`
- `date_issue`: `3`
- `member_auto_renew`: `1`
- `not_received_after_delivered`: `1`
- `compensation_accept`: `1`
- `quality_issue`: `1`
### 会员场景-开通问题
- `other`: `26`
- `close_conversation`: `15`
- `member_benefit`: `14`
- `transfer_request`: `11`
- `member_auto_renew`: `5`
- `refund_request`: `4`
- `payment_issue`: `4`
- `activity_coupon`: `3`
- `compensation_request`: `2`
- `compensation_accept`: `1`
- `cancel_request`: `1`
### 金融场景-功能问题
- `other`: `49`
- `close_conversation`: `20`
- `payment_issue`: `10`
- `transfer_request`: `6`
- `cancel_request`: `1`
### 其他场景-其他问题
- `other`: `50`
- `close_conversation`: `13`
- `presale_consult`: `6`
- `transfer_request`: `4`
- `activity_coupon`: `2`
- `date_issue`: `1`
- `member_auto_renew`: `1`
- `compensation_request`: `1`
- `invoice_request`: `1`
- `cancel_request`: `1`
- `payment_issue`: `1`
- `eta_question`: `1`
### 未识别
- `other`: `30`
- `transfer_request`: `15`
- `close_conversation`: `8`
- `cancel_request`: `7`
- `member_benefit`: `4`
- `not_received_after_delivered`: `3`
- `refund_request`: `2`
- `quality_issue`: `2`
- `delivery_urge`: `2`
- `member_auto_renew`: `1`
- `presale_consult`: `1`
- `short_delivery`: `1`
### 履约场景-无骑手接单
- `other`: `39`
- `close_conversation`: `8`
- `transfer_request`: `5`
- `delivery_urge`: `5`
- `no_rider`: `4`
- `cancel_request`: `2`
- `eta_question`: `2`
- `contact_rider`: `2`
- `payment_issue`: `1`
- `compensation_reject`: `1`
- `compensation_request`: `1`
### 活动场景-常规活动问题诉求
- `other`: `27`
- `close_conversation`: `11`
- `activity_coupon`: `9`
- `transfer_request`: `2`
- `date_issue`: `2`
- `cancel_request`: `1`
- `compensation_accept`: `1`
- `presale_consult`: `1`
- `short_delivery`: `1`

## 各 scene 的 ResponseSolution 分布 TOP
### 收货场景-品质问题
- `无`: `1522`
- `选择商品`: `323`
- `小象单商品退款-100%`: `214`
- `小象单商品退款-50%`: `109`
- `小象单商品退款-30%`: `53`
- `小象单商品退款-20%`: `44`
- `催促退款审核;退审跟单`: `43`
- `小象单商品退款-40%`: `38`
- `操作赔付-优惠券-5元`: `34`
- `小象单商品退款-10%`: `32`
- `小象单商品退款-70%`: `27`
- `操作赔付-优惠券-8元`: `22`
### 履约场景-修改订单问题
- `无`: `1446`
- `取消订单`: `261`
- `引导自助修改订单`: `112`
- `无骑手接单跟单`: `26`
- `外呼骑手-修改订单`: `25`
- `再次外呼骑手-修改订单`: `16`
- `外呼门店-修改订单`: `15`
- `操作赔付-运费券-3元`: `15`
- `再次外呼门店-修改订单`: `7`
- `引导自助联系骑手`: `4`
- `外呼骑手-协商调换货品`: `3`
- `引导自助管理地址`: `2`
### 履约场景-配送问题
- `无`: `1434`
- `操作赔付-优惠券-10元`: `62`
- `操作赔付-优惠券-15元`: `50`
- `操作赔付-优惠券-8元`: `50`
- `取消订单`: `47`
- `系统催单`: `44`
- `智能跟单`: `35`
- `外呼骑手-催促配送`: `32`
- `操作赔付-优惠券-20元`: `26`
- `再次外呼骑手-催促配送`: `23`
- `引导自助联系骑手`: `23`
- `操作赔付-优惠券-5元`: `14`
### 收货场景-少送问题
- `无`: `430`
- `小象单商品退款-100%`: `139`
- `选择商品`: `123`
- `操作赔付-优惠券-3元`: `110`
- `操作赔付-优惠券-8元`: `5`
- `小象单商品退款-50%`: `4`
- `催促退款审核;退审跟单`: `3`
- `操作赔付-优惠券-5元`: `2`
- `加急催促退款审核`: `1`
### 发票场景
- `无`: `481`
- `开发票`: `92`
- `会员卡退款`: `2`
- `引导自助查看会员权益`: `2`
- `选择商品`: `1`
### <MISSING>
- `无`: `302`
- `选择商品`: `40`
- `小象单商品退款-100%`: `39`
- `小象整单申请退款`: `20`
- `外呼骑手-协商调换货品`: `18`
- `操作赔付-优惠券-3元`: `17`
- `催促退款审核;退审跟单`: `16`
- `小象单商品退款-50%`: `15`
- `操作赔付-优惠券-5元`: `12`
- `操作赔付-优惠券-8元`: `10`
- `加急催促退款审核`: `10`
- `发送送达图片`: `9`
### 收货场景-错送问题
- `无`: `299`
- `外呼骑手-协商调换货品`: `73`
- `小象单商品退款-100%`: `46`
- `选择商品`: `39`
- `小象整单申请退款`: `30`
- `再次外呼骑手-协商调换货品`: `22`
- `小象单商品退款-50%`: `15`
- `小象单商品退款-40%`: `4`
- `小象单商品退款-20%`: `2`
- `小象单商品退款-30%`: `2`
- `小象单商品退款-80%`: `2`
### 会员场景-续费问题
- `无`: `341`
- `管理会员自动续费`: `55`
- `会员卡退款`: `9`
### 收货场景-退款问题
- `无`: `304`
- `选择商品`: `49`
- `催促退款审核`: `11`
- `催促退款审核;退审跟单`: `6`
- `退审跟单`: `5`
- `小象单商品退款-100%`: `4`
- `会员卡退款`: `3`
- `操作赔付-优惠券-3元`: `3`
- `小象单商品退款-50%`: `2`
- `小象单商品退款-30%`: `2`
- `操作赔付-优惠券-5元`: `2`
- `小象单商品退款-40%`: `1`
### 活动场景-常规活动问题
- `无`: `346`
- `操作赔付-优惠券-5元`: `14`
- `引导自助查看会员权益`: `2`
- `引导自助修改订单`: `1`
### 会员场景-权益问题
- `无`: `285`
- `会员卡退款`: `13`
- `引导自助查看会员权益`: `9`
- `引导自助开通会员`: `4`
- `管理会员自动续费`: `3`
- `引导自助查看优惠券`: `3`
### 收货场景-实描不符问题
- `无`: `143`
- `选择商品`: `32`
- `小象单商品退款-50%`: `27`
- `小象单商品退款-30%`: `14`
- `小象单商品退款-20%`: `11`
- `催促退款审核;退审跟单`: `11`
- `小象单商品退款-100%`: `7`
- `操作赔付-优惠券-3元`: `6`
- `加急催促退款审核`: `3`
- `会员卡退款`: `2`
- `小象单商品退款-70%`: `2`
- `小象单商品退款-10%`: `2`
### 会员场景-退卡问题
- `无`: `226`
- `会员卡退款`: `21`
- `管理会员自动续费`: `15`
- `操作赔付-优惠券-5元`: `2`
- `操作赔付-优惠券-3元`: `1`
### 收货场景-催退款进度
- `无`: `132`
- `选择商品`: `56`
- `催促退款审核;退审跟单`: `48`
- `加急催促退款审核`: `16`
- `小象单商品退款-100%`: `2`
- `操作赔付-优惠券-3元`: `1`
### 活动场景-通用问题
- `无`: `210`
- `操作赔付-优惠券-5元`: `6`
- `管理会员自动续费`: `1`
- `发送送达图片`: `1`
- `外呼骑手-核实情况`: `1`
- `再次外呼骑手-核实情况`: `1`
### 收货场景-重量不足问题
- `无`: `110`
- `选择商品`: `28`
- `小象单商品退款-30%`: `14`
- `小象单商品退款-100%`: `12`
- `小象单商品退款-50%`: `11`
- `催促退款审核;退审跟单`: `10`
- `操作赔付-优惠券-3元`: `9`
- `小象单商品退款-20%`: `8`
- `小象单商品退款-40%`: `4`
- `加急催促退款审核`: `4`
- `操作赔付-优惠券-5元`: `3`
- `小象单商品退款-10%`: `3`
### 其他场景-投诉问题
- `无`: `207`
- `引导自助查看配送范围`: `3`
- `引导自助查看小象开通城市`: `3`
### 履约场景-履约中订单缺货
- `无`: `116`
- `选择商品`: `30`
- `操作赔付-优惠券-8元`: `24`
- `操作赔付-优惠券-3元`: `20`
- `操作赔付-优惠券-5元`: `15`
- `取消订单`: `4`
### 其他场景
- `无`: `133`
- `引导自助查看配送范围`: `2`
- `引导自助查看小象开通城市`: `2`
- `选择商品`: `1`
- `小象单商品退款-50%`: `1`
- `小象单商品退款-100%`: `1`
- `催促退款审核;退审跟单`: `1`
### 其他场景-账号问题
- `无`: `133`
- `引导自助查看配送范围`: `5`

## 各 scene 的 DialogueAgreeSolution 分布 TOP
### 收货场景-品质问题
- `无`: `2297`
- `小象单商品退款-100%`: `133`
- `小象单商品退款-50%`: `37`
- `小象单商品退款-80%`: `13`
- `小象单商品退款-70%`: `11`
- `操作赔付-优惠券-5元`: `11`
- `操作赔付-优惠券-8元`: `10`
- `小象单商品退款-30%`: `10`
- `小象单商品退款-20%`: `10`
- `取消订单`: `7`
- `小象单商品退款-40%`: `7`
- `小象单商品退款-60%`: `7`
### 履约场景-修改订单问题
- `无`: `1805`
- `取消订单`: `93`
- `外呼骑手-修改订单`: `20`
- `外呼门店-修改订单`: `8`
- `操作赔付-运费券-3元`: `6`
- `外呼骑手-协商调换货品`: `1`
### 履约场景-配送问题
- `无`: `1795`
- `取消订单`: `24`
- `操作赔付-优惠券-10元`: `20`
- `操作赔付-优惠券-15元`: `16`
- `操作赔付-优惠券-8元`: `13`
- `操作赔付-优惠券-20元`: `12`
- `小象单商品退款-100%`: `4`
- `操作赔付-优惠券-5元`: `3`
- `外呼骑手-协商调换货品`: `2`
- `小象整单申请退款`: `2`
- `外呼骑手-修改订单`: `1`
- `小象单商品退款-80%`: `1`
### 收货场景-少送问题
- `无`: `706`
- `小象单商品退款-100%`: `69`
- `操作赔付-优惠券-3元`: `39`
- `操作赔付-优惠券-8元`: `2`
- `小象单商品退款-50%`: `1`
### 发票场景
- `无`: `577`
- `会员卡退款`: `1`
### <MISSING>
- `无`: `481`
- `小象单商品退款-100%`: `23`
- `小象整单申请退款`: `12`
- `外呼骑手-协商调换货品`: `9`
- `操作赔付-优惠券-8元`: `5`
- `操作赔付-优惠券-3元`: `5`
- `操作赔付-优惠券-5元`: `4`
- `小象单商品退款-50%`: `3`
- `小象单商品退款-80%`: `3`
- `取消订单`: `2`
- `小象单商品退款-60%`: `1`
- `小象单商品退款-20%`: `1`
### 收货场景-错送问题
- `无`: `455`
- `外呼骑手-协商调换货品`: `36`
- `小象单商品退款-100%`: `23`
- `小象整单申请退款`: `12`
- `小象单商品退款-50%`: `7`
- `小象单商品退款-80%`: `1`
### 会员场景-续费问题
- `无`: `401`
- `会员卡退款`: `4`
### 收货场景-退款问题
- `无`: `381`
- `催促退款审核`: `8`
- `小象单商品退款-100%`: `2`
- `小象单商品退款-30%`: `1`
- `会员卡退款`: `1`
- `操作赔付-优惠券-3元`: `1`
- `操作赔付-优惠券-5元`: `1`
### 活动场景-常规活动问题
- `无`: `357`
- `操作赔付-优惠券-5元`: `6`
### 会员场景-权益问题
- `无`: `311`
- `会员卡退款`: `6`
### 收货场景-实描不符问题
- `无`: `236`
- `小象单商品退款-50%`: `10`
- `小象单商品退款-100%`: `7`
- `操作赔付-优惠券-3元`: `3`
- `小象单商品退款-20%`: `2`
- `小象单商品退款-30%`: `2`
- `会员卡退款`: `1`
- `小象单商品退款-70%`: `1`
- `小象单商品退款-40%`: `1`
- `小象单商品退款-10%`: `1`
- `操作赔付-优惠券-5元`: `1`
- `小象单商品退款-80%`: `1`
### 会员场景-退卡问题
- `无`: `255`
- `会员卡退款`: `9`
- `操作赔付-优惠券-5元`: `1`
### 收货场景-催退款进度
- `无`: `253`
- `操作赔付-优惠券-3元`: `1`
- `小象单商品退款-100%`: `1`
### 活动场景-通用问题
- `无`: `217`
- `操作赔付-优惠券-5元`: `3`
### 收货场景-重量不足问题
- `无`: `193`
- `小象单商品退款-100%`: `8`
- `小象单商品退款-30%`: `4`
- `操作赔付-优惠券-3元`: `4`
- `小象单商品退款-40%`: `2`
- `小象单商品退款-20%`: `2`
- `小象单商品退款-50%`: `2`
- `操作赔付-优惠券-5元`: `1`
- `小象单商品退款-10%`: `1`
- `小象单商品退款-80%`: `1`
### 其他场景-投诉问题
- `无`: `213`
### 履约场景-履约中订单缺货
- `无`: `188`
- `操作赔付-优惠券-8元`: `10`
- `操作赔付-优惠券-3元`: `5`
- `取消订单`: `3`
- `操作赔付-优惠券-5元`: `3`
### 其他场景
- `无`: `140`
- `小象单商品退款-100%`: `1`
### 其他场景-账号问题
- `无`: `138`

## 缺关键信号最多的场景
- `收货场景-品质问题`: `5906`
- `履约场景-配送问题`: `5608`
- `履约场景-修改订单问题`: `4986`
- `活动场景-常规活动问题`: `3571`
- `会员场景-权益问题`: `3255`
- `会员场景-续费问题`: `2278`
- `其他场景-投诉问题`: `2163`
- `会员场景-退卡问题`: `2011`
- `收货场景-少送问题`: `1838`
- `活动场景-通用问题`: `1765`
- `发票场景`: `1764`
- `其他场景`: `1658`
- `其他场景-账号问题`: `1587`
- `收货场景-错送问题`: `1410`
- `其他场景-其他问题`: `1009`
- `收货场景-退款问题`: `987`
- `<MISSING>`: `960`
- `金融场景-支付问题`: `881`
- `收货场景-催退款进度`: `765`
- `活动场景-省钱卡问题`: `728`
- `收货场景-实描不符问题`: `658`
- `会员场景-开通问题`: `638`
- `会员场景-退卡问题诉求`: `615`
- `金融场景-功能问题`: `594`
- `收货场景-重量不足问题`: `546`
- `其他场景-合作问题`: `416`
- `其他场景-其他问题诉求`: `348`
- `履约场景-履约中订单缺货`: `347`
- `活动场景-临时活动问题`: `254`
- `活动场景-常规活动问题诉求`: `241`
