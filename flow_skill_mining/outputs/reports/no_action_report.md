# ResponseSolution=无 分类报告

- ResponseSolution=无 总数: `9712`
- unknown 数: `1080` (11.12% if nonzero)
- 漏操作候选样本数: `80`

## no_action_reason 分布
- `explain_refund_status`: `2833`
- `close_conversation`: `2257`
- `unknown`: `1080`
- `ask_user_problem`: `788`
- `ask_select_product`: `689`
- `ask_refund_ratio`: `668`
- `ask_upload_image`: `412`
- `after_action_followup`: `357`
- `unavailable_capability`: `237`
- `explain_status`: `92`
- `clarify_intent`: `88`
- `eta_answer_only`: `82`
- `wait_for_tool_result`: `63`
- `already_compensated`: `44`
- `policy_explain`: `11`
- `ask_refund_reason`: `8`
- `explain_order_cancelled`: `3`

## 按 scene 的 no_action_reason 分布
### 收货场景-品质问题
- `ask_select_product`: `381`
- `ask_upload_image`: `360`
- `close_conversation`: `310`
- `explain_refund_status`: `266`
- `ask_user_problem`: `127`
- `ask_refund_ratio`: `41`
- `clarify_intent`: `12`
- `unknown`: `12`
- `after_action_followup`: `9`
- `already_compensated`: `4`
### 履约场景-修改订单问题
- `explain_refund_status`: `471`
- `close_conversation`: `375`
- `ask_user_problem`: `167`
- `unknown`: `151`
- `after_action_followup`: `84`
- `ask_refund_ratio`: `74`
- `unavailable_capability`: `51`
- `clarify_intent`: `22`
- `explain_status`: `18`
- `wait_for_tool_result`: `14`
- `eta_answer_only`: `10`
- `ask_refund_reason`: `4`
- `already_compensated`: `3`
- `explain_order_cancelled`: `2`
### 履约场景-配送问题
- `explain_refund_status`: `548`
- `close_conversation`: `337`
- `unknown`: `151`
- `ask_user_problem`: `107`
- `after_action_followup`: `76`
- `eta_answer_only`: `54`
- `explain_status`: `41`
- `unavailable_capability`: `39`
- `wait_for_tool_result`: `29`
- `already_compensated`: `23`
- `ask_refund_ratio`: `22`
- `clarify_intent`: `6`
- `explain_order_cancelled`: `1`
### 发票场景
- `explain_refund_status`: `266`
- `close_conversation`: `109`
- `unknown`: `42`
- `unavailable_capability`: `22`
- `ask_user_problem`: `14`
- `after_action_followup`: `9`
- `ask_refund_ratio`: `8`
- `explain_status`: `7`
- `clarify_intent`: `2`
- `eta_answer_only`: `1`
- `policy_explain`: `1`
### 收货场景-少送问题
- `ask_refund_ratio`: `145`
- `close_conversation`: `136`
- `explain_refund_status`: `60`
- `ask_select_product`: `40`
- `ask_user_problem`: `24`
- `after_action_followup`: `11`
- `unknown`: `11`
- `clarify_intent`: `2`
- `explain_status`: `1`
### 活动场景-常规活动问题
- `unknown`: `101`
- `explain_refund_status`: `75`
- `close_conversation`: `66`
- `unavailable_capability`: `39`
- `ask_user_problem`: `28`
- `ask_refund_ratio`: `21`
- `after_action_followup`: `13`
- `clarify_intent`: `2`
- `wait_for_tool_result`: `1`
### 会员场景-续费问题
- `explain_refund_status`: `154`
- `close_conversation`: `99`
- `ask_user_problem`: `35`
- `unknown`: `31`
- `ask_refund_ratio`: `7`
- `after_action_followup`: `6`
- `clarify_intent`: `5`
- `unavailable_capability`: `3`
- `explain_status`: `1`
### 收货场景-退款问题
- `ask_select_product`: `105`
- `ask_refund_ratio`: `90`
- `close_conversation`: `69`
- `ask_user_problem`: `31`
- `clarify_intent`: `5`
- `explain_refund_status`: `3`
- `after_action_followup`: `1`
### <MISSING>
- `explain_refund_status`: `127`
- `close_conversation`: `72`
- `unknown`: `44`
- `ask_user_problem`: `28`
- `after_action_followup`: `7`
- `already_compensated`: `5`
- `explain_status`: `4`
- `wait_for_tool_result`: `4`
- `unavailable_capability`: `3`
- `ask_refund_reason`: `3`
- `ask_refund_ratio`: `2`
- `clarify_intent`: `2`
- `eta_answer_only`: `1`
### 收货场景-错送问题
- `ask_select_product`: `132`
- `close_conversation`: `73`
- `ask_refund_ratio`: `48`
- `explain_refund_status`: `23`
- `ask_user_problem`: `14`
- `after_action_followup`: `4`
- `unknown`: `2`
- `clarify_intent`: `2`
- `eta_answer_only`: `1`
### 会员场景-权益问题
- `unknown`: `86`
- `explain_refund_status`: `72`
- `close_conversation`: `60`
- `ask_user_problem`: `26`
- `after_action_followup`: `18`
- `unavailable_capability`: `9`
- `explain_status`: `5`
- `clarify_intent`: `4`
- `policy_explain`: `3`
- `ask_refund_ratio`: `2`
### 会员场景-退卡问题
- `explain_refund_status`: `89`
- `close_conversation`: `67`
- `unknown`: `32`
- `ask_user_problem`: `19`
- `after_action_followup`: `12`
- `unavailable_capability`: `3`
- `clarify_intent`: `2`
- `ask_refund_ratio`: `2`
### 活动场景-通用问题
- `unknown`: `69`
- `explain_refund_status`: `53`
- `close_conversation`: `35`
- `ask_user_problem`: `11`
- `after_action_followup`: `11`
- `unavailable_capability`: `9`
- `already_compensated`: `7`
- `ask_refund_ratio`: `6`
- `explain_status`: `3`
- `clarify_intent`: `2`
- `wait_for_tool_result`: `2`
- `policy_explain`: `2`
### 其他场景-投诉问题
- `unknown`: `66`
- `explain_refund_status`: `60`
- `close_conversation`: `28`
- `after_action_followup`: `20`
- `unavailable_capability`: `10`
- `ask_user_problem`: `9`
- `explain_status`: `6`
- `eta_answer_only`: `5`
- `wait_for_tool_result`: `2`
- `clarify_intent`: `1`
### 收货场景-实描不符问题
- `ask_upload_image`: `51`
- `explain_refund_status`: `44`
- `close_conversation`: `29`
- `ask_user_problem`: `11`
- `clarify_intent`: `4`
- `ask_refund_ratio`: `2`
- `after_action_followup`: `1`
- `already_compensated`: `1`
### 其他场景
- `unknown`: `53`
- `explain_refund_status`: `32`
- `close_conversation`: `16`
- `after_action_followup`: `11`
- `ask_user_problem`: `10`
- `wait_for_tool_result`: `5`
- `unavailable_capability`: `4`
- `ask_refund_ratio`: `2`
### 其他场景-账号问题
- `unknown`: `51`
- `explain_refund_status`: `30`
- `close_conversation`: `16`
- `after_action_followup`: `15`
- `unavailable_capability`: `7`
- `ask_user_problem`: `7`
- `eta_answer_only`: `4`
- `wait_for_tool_result`: `2`
- `clarify_intent`: `1`
### 收货场景-催退款进度
- `ask_refund_ratio`: `60`
- `close_conversation`: `51`
- `ask_select_product`: `14`
- `ask_user_problem`: `4`
- `clarify_intent`: `2`
- `explain_refund_status`: `1`
### 长尾场景-金融
- `explain_refund_status`: `58`
- `close_conversation`: `30`
- `unknown`: `14`
- `unavailable_capability`: `7`
- `after_action_followup`: `6`
- `ask_user_problem`: `5`
- `clarify_intent`: `1`
- `ask_refund_reason`: `1`
### 履约场景-履约中订单缺货
- `ask_refund_ratio`: `56`
- `close_conversation`: `43`
- `ask_user_problem`: `10`
- `explain_refund_status`: `6`
- `clarify_intent`: `1`
### 收货场景-重量不足问题
- `ask_refund_ratio`: `40`
- `close_conversation`: `28`
- `explain_refund_status`: `27`
- `ask_user_problem`: `12`
- `after_action_followup`: `2`
- `already_compensated`: `1`
### 金融场景-支付问题
- `close_conversation`: `34`
- `explain_refund_status`: `26`
- `unknown`: `19`
- `ask_user_problem`: `10`
- `after_action_followup`: `9`
- `unavailable_capability`: `4`
- `clarify_intent`: `2`
### 活动场景-省钱卡问题
- `explain_refund_status`: `43`
- `close_conversation`: `12`
- `unknown`: `11`
- `ask_refund_ratio`: `8`
- `ask_user_problem`: `4`
- `unavailable_capability`: `3`
- `after_action_followup`: `3`
- `policy_explain`: `2`
### 金融场景-功能问题
- `explain_refund_status`: `30`
- `close_conversation`: `20`
- `unknown`: `19`
- `after_action_followup`: `6`
- `ask_user_problem`: `5`
- `unavailable_capability`: `4`
- `policy_explain`: `1`
- `clarify_intent`: `1`
### 其他场景-其他问题
- `unknown`: `39`
- `explain_refund_status`: `13`
- `close_conversation`: `13`
- `after_action_followup`: `6`
- `unavailable_capability`: `5`
- `clarify_intent`: `2`
- `ask_user_problem`: `2`
- `eta_answer_only`: `1`
### 会员场景-退卡问题诉求
- `explain_refund_status`: `40`
- `close_conversation`: `18`
- `ask_user_problem`: `10`
- `unknown`: `9`
- `after_action_followup`: `1`
### 会员场景-开通问题
- `explain_refund_status`: `23`
- `close_conversation`: `15`
- `unknown`: `15`
- `ask_user_problem`: `9`
- `after_action_followup`: `4`
- `ask_refund_ratio`: `2`
- `clarify_intent`: `2`
- `explain_status`: `2`
- `policy_explain`: `2`
### 未识别
- `explain_refund_status`: `28`
- `ask_user_problem`: `13`
- `close_conversation`: `8`
- `ask_refund_ratio`: `3`
- `clarify_intent`: `2`
- `after_action_followup`: `1`
- `unavailable_capability`: `1`
- `unknown`: `1`
### 活动场景-常规活动问题诉求
- `explain_refund_status`: `23`
- `ask_refund_ratio`: `13`
- `close_conversation`: `11`
- `unknown`: `6`
- `ask_user_problem`: `2`
### 履约场景-无骑手接单
- `explain_refund_status`: `21`
- `close_conversation`: `8`
- `ask_user_problem`: `4`
- `eta_answer_only`: `4`
- `unknown`: `4`
- `after_action_followup`: `4`
- `wait_for_tool_result`: `2`
- `explain_status`: `1`
- `unavailable_capability`: `1`
### 其他场景-其他问题诉求
- `explain_refund_status`: `12`
- `close_conversation`: `12`
- `ask_user_problem`: `4`
- `unknown`: `4`
- `unavailable_capability`: `3`
- `after_action_followup`: `3`
- `explain_status`: `2`
- `eta_answer_only`: `1`
- `clarify_intent`: `1`
### 售前场景-下单问题
- `explain_refund_status`: `28`
- `close_conversation`: `6`
- `ask_user_problem`: `2`
- `unavailable_capability`: `1`
- `unknown`: `1`
### 其他场景-合作问题
- `unknown`: `10`
- `close_conversation`: `7`
- `after_action_followup`: `3`
- `ask_user_problem`: `2`
- `unavailable_capability`: `2`
- `explain_refund_status`: `1`
- `wait_for_tool_result`: `1`
### 收货场景-退款问题诉求
- `ask_select_product`: `12`
- `close_conversation`: `6`
- `ask_refund_ratio`: `4`
- `ask_user_problem`: `3`
### 售前场景-商品咨询问题
- `explain_refund_status`: `11`
- `close_conversation`: `4`
- `ask_refund_ratio`: `3`
- `ask_user_problem`: `2`
### 活动场景-临时活动问题
- `unknown`: `14`
- `close_conversation`: `2`
- `explain_status`: `1`
- `after_action_followup`: `1`
- `ask_user_problem`: `1`
- `wait_for_tool_result`: `1`
### 会员场景-开通问题诉求
- `explain_refund_status`: `8`
- `close_conversation`: `4`
- `ask_user_problem`: `3`
- `unknown`: `2`
### 售前场景-业务咨询问题
- `ask_refund_ratio`: `7`
- `explain_refund_status`: `5`
- `ask_user_problem`: `2`
- `close_conversation`: `2`
### 收货场景-差价问题
- `explain_refund_status`: `10`
- `close_conversation`: `3`
- `ask_user_problem`: `2`
### 售前场景-服务咨询问题
- `explain_refund_status`: `9`
- `ask_user_problem`: `3`
- `close_conversation`: `3`

## 可能是漏操作的无动作样本候选 TOP
- `1991a915a1f930ef2277889a2612d3dfd0ad429c` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `7ad982ba5f5d88a7a7c6e4605a2d3a2df22a3533` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `3844c667c4f5002a549ce44773cbb2db3f2f349c` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `e23b0658ef0da744678e436e75074aa8f232f770` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `c36e7403243efdab050f990708deba8ef75b13ea` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `24af6734016686306b294ec2b3ed6f17494d4b98` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `7389506117b831032f890b56bf24d2f67ec2320a` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `721209b72f31893e3563385e6e731511b5f1318e` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `3ad4fbd71225a27dff0f3527e903dac99ec7bf5a` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `63264ec5bcf89674e1fca5f4669b0e9d07c90a84` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `c6a869c540f30d7d04100928f022a29b20a9de2f` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `ec2492c73dc3ec0e91c8c95692faa7d560cd580f` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `6fbcf9b6ee53d9ed00ed51fb27d12697c47d1e60` scene=`履约场景-配送问题` intent=`cancel_request` reason=`unknown`
- `e01293634eba0bfb57e19547777f3bdb0b7c441f` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `301ec8ae2da22c2e750239e09f15246734cfa3b1` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `7446e54c5f5aa7d53dfe17b228826e08d7cb68b7` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `44304448466aa29afe056c3a6020fe00f21646fd` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `e632925243d86d5ec0132c410b36d948e4d1c20e` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `b4077f2aba2c802b5cfb8be9d4f93d317a79ed36` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `3c71bcbf684bd5b3dd6769e1c72da4258dd508d1` scene=`履约场景-配送问题` intent=`short_delivery` reason=`unknown`
- `591de10ed6c2a649e6df224d0fc443ecfc85c5c6` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `fd32469499cbc92ea195c77533b154be66b0b946` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `04d3eae2f29221e10ffa52af6fcd7c516a3f72d9` scene=`履约场景-配送问题` intent=`contact_rider` reason=`unknown`
- `d3bd6e201276fc71b27e533fb91bed73b2e57cc3` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `14e372922c09364da1bb6c1ab04d466cdc0a5758` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `7b1532295d19f513f4c9a677e83cef46b8f3083c` scene=`履约场景-配送问题` intent=`contact_rider` reason=`unknown`
- `2607e557114fcb1f8a928547695ed40ab1320a09` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `820182e810eb61ba29ac82d98016c31d49e18e63` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `f403a2f990c4351dc8fe0350d46e6aeb93f2f189` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `9be0384e2fa1c2f8f508dbef3327e277fd184bd2` scene=`履约场景-配送问题` intent=`contact_rider` reason=`unknown`
- `82c1e768acb3e347eb0502bbd562faabac2bac4f` scene=`履约场景-配送问题` intent=`contact_rider` reason=`unknown`
- `70246ccbcfb911a42dacf38b36be392016838f23` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `52523f518db3218c77020fbf37e2b0d10fe2a3cf` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `621b6ebefb065c45928ab0b9e61b6deee4990c47` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `10c80437c58c2e51353849b9b3b0ce552064ede5` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `61c09ceae48adeeef9032be53bd0ad72bc7bda73` scene=`履约场景-配送问题` intent=`presale_consult` reason=`unknown`
- `b907fd0838951e937b10b3c2792b7cde4afdeb30` scene=`履约场景-配送问题` intent=`contact_rider` reason=`unknown`
- `816a2a70dbaaa221e41f48cf90ff1b2e8f3e4351` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `b94d9aebb14f4841c4254553154e0c1aaf452eed` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `fbc655412060d1ff7a096ac87f06662704bf40cd` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `cd48a94c901b953a45e9292a48ad0755fd124281` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `a0a6c9e042b23c449f77e1183ac1310936620c6a` scene=`履约场景-配送问题` intent=`compensation_request` reason=`unknown`
- `5893d7897388d70fbb07ad0f21648ac3ac4280d4` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `e2938075cb138560b2a1fa7e8069ff267df98b43` scene=`履约场景-配送问题` intent=`contact_rider` reason=`unknown`
- `bc5481e0516d2b3fafc2d82127915bf123362544` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `d0d38a14756ec58e1ede246d6b7affe8f4afa1d2` scene=`履约场景-配送问题` intent=`delivery_urge` reason=`eta_answer_only`
- `9ffbc0bbbed1e65dbeb7fe4e9ad7c8f6646da9bd` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
- `65f14f49557822ab46bcc65465fd8dc238dd8c17` scene=`履约场景-配送问题` intent=`cancel_request` reason=`unknown`
- `9faf9f7ca9a740c6fc93e861d26fda5500c6ef9a` scene=`履约场景-配送问题` intent=`activity_coupon` reason=`unknown`
- `768c5b769723988f612853e7609d899cd11d3118` scene=`履约场景-配送问题` intent=`eta_question` reason=`eta_answer_only`
