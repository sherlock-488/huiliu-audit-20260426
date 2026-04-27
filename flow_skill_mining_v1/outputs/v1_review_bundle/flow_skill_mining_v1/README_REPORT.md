# Flow Skill Mining v1 总报告

## 1. v1 相比 v0 修了什么
- 增加 solution alias/canonical registry，修正自助查看缺横线、小象单商品退款历史写法、红包到优惠券历史口径。
- 将 confirmation policy 拆成 strong_confirmation_required / user_request_is_enough / no_confirmation_required 三层。
- 重新校准 no_action_reason，避免在非退款场景泛化为 explain_refund_status。
- Global checker v1 使用 canonical/alias，R4 只约束强确认方案，R10 重新识别商品选择。
- 只生成两个 replay-ready skill：履约配送、收货品质。

## 2. solution registry alias 修正
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

## 3. confirmation policy 三分层
- `no_confirmation_required`: `18`
- `strong_confirmation_required`: `6`
- `user_request_is_enough`: `6`
- `unclear`: `1`

## 4. no_action_reason 变化
- explain_refund_status v0: `2833`
- explain_refund_status v1: `2323`
- delta: `-510`
### v1 top
- `close_conversation`: `3688`
- `explain_refund_status`: `2323`
- `ask_select_product`: `690`
- `unknown`: `675`
- `ask_user_problem`: `656`
- `ask_refund_ratio`: `535`
- `ask_upload_image`: `353`
- `unavailable_capability`: `205`
- `explain_status`: `177`
- `after_action_followup`: `129`
- `eta_answer_only`: `116`
- `clarify_intent`: `75`
- `wait_for_tool_result`: `40`
- `already_compensated`: `30`
- `policy_explain`: `11`
- `ask_refund_reason`: `7`
- `explain_order_cancelled`: `2`

## 5. checker v1 vs v0
- v0 fail/warning: `98` / `509`
- v1 fail/warning: `24` / `355`

## 6. fulfillment_delivery_v1 是否可进入离线 replay
- action_rules: `1`
- replay cases: `121`
- 建议先 replay：该场景动作集中，checker guard 相对明确。

## 7. receipt_quality_v1 风险
- action_rules: `14`
- replay cases: `120`
- 风险：图片前置、商品选择识别、退款比例/赔付边界仍需训练师确认。

## 8. replay set 样本构成
### fulfillment_delivery_replay.jsonl
- cases: `121`
#### gold ResponseSolution
- `无`: `64`
- `操作赔付-优惠券-10元`: `11`
- `系统催单`: `7`
- `智能跟单`: `7`
- `外呼骑手-催促配送`: `6`
- `操作赔付-优惠券-8元`: `6`
- `引导自助联系骑手`: `4`
- `再次外呼骑手-催促配送`: `3`
- `取消订单`: `2`
- `操作赔付-优惠券-15元`: `2`
- `外呼骑手-协商调换货品`: `2`
- `小象整单申请退款`: `2`
- `小象单商品退款-100%`: `2`
- `操作赔付-优惠券-15元;智能跟单`: `1`
- `再次外呼骑手-协商调换货品`: `1`
- `选择商品`: `1`
#### checker focus
- `no_action`: `64`
- `delivery_urge`: `16`
- `confirmation`: `12`
- `contact_rider`: `8`
- `eta_question`: `8`
- `compensation_request`: `4`
- `cancel_request`: `1`
### receipt_quality_replay.jsonl
- cases: `120`
#### gold ResponseSolution
- `无`: `43`
- `小象单商品退款-50%`: `12`
- `小象单商品退款-100%`: `12`
- `选择商品`: `10`
- `小象单商品退款-30%`: `6`
- `小象单商品退款-60%`: `5`
- `操作赔付-优惠券-8元`: `5`
- `小象单商品退款-40%`: `4`
- `小象单商品退款-10%`: `4`
- `催促退款审核;退审跟单`: `3`
- `取消订单`: `3`
- `小象单商品退款-20%`: `2`
- `小象单商品退款-80%`: `2`
- `操作赔付-优惠券-5元`: `2`
- `发送送达图片`: `2`
- `操作赔付-优惠券-3元`: `2`
- `小象单商品退款-70%`: `2`
- `加急催促退款审核`: `1`
#### checker focus
- `refund_or_compensation`: `58`
- `no_action`: `43`
- `confirmation`: `24`
- `ask_select_product`: `9`
- `ask_upload_image`: `9`
- `ask_refund_ratio`: `5`

## 9. 需要训练师确认 TOP 20
1. `小象单商品退款-xx%` confirmation level=strong_confirmation_required response=992 agree=422 unmatched=0
2. `操作赔付-优惠券-xx元` confirmation level=strong_confirmation_required response=566 agree=190 unmatched=0
3. `取消订单` confirmation level=strong_confirmation_required response=343 agree=132 unmatched=0
4. `会员卡退款` confirmation level=strong_confirmation_required response=105 agree=48 unmatched=0
5. `小象整单申请退款` confirmation level=strong_confirmation_required response=55 agree=27 unmatched=0
6. `操作赔付-运费券-3元` confirmation level=strong_confirmation_required response=15 agree=6 unmatched=0
7. fulfillment_delivery_v1: `rule_157127392e4e` support=6 confidence=0.6667 expected=操作赔付-优惠券-15元
8. fulfillment_delivery_v1: `rule_abe6bc3cbed1` support=6 confidence=0.6667 expected=无
9. fulfillment_delivery_v1: `rule_ba7ef72d2208` support=3 confidence=0.6667 expected=无
10. fulfillment_delivery_v1: `rule_b4d487b81989` support=3 confidence=0.6667 expected=操作赔付-优惠券-15元
11. fulfillment_delivery_v1: `rule_3167f22f9b37` support=3 confidence=0.6667 expected=无
12. fulfillment_delivery_v1: `rule_4d3c8981c8eb` support=3 confidence=0.6667 expected=外呼骑手-催促配送
13. receipt_quality_v1: `rule_b1c3b090ac0f` support=3 confidence=0.6667 expected=无
14. receipt_quality_v1: `rule_8431aed7359f` support=3 confidence=0.6667 expected=取消订单
15. receipt_quality_v1: `rule_574fc6159dca` support=3 confidence=0.6667 expected=小象单商品退款-50%
16. receipt_quality_v1: `rule_d0808ef2b6e1` support=3 confidence=0.6667 expected=无
17. receipt_quality_v1: `rule_3089cead4d15` support=3 confidence=0.6667 expected=无
18. receipt_quality_v1: `rule_53a47874d847` support=3 confidence=0.6667 expected=催促退款审核;退审跟单
19. R11 图片前置是否应从 warning 升级为 fail。
20. ResponseSolution=无 的 possible_missing_action 是否真的是漏操作。

## 10. 下一步 baseline prompt vs skill prompt 对比实验
1. 使用 replay jsonl 的 `input_without_target` 分别跑 baseline prompt 和插入 skill_prompt 的 prompt。
2. 保存模型输出为 model_outputs.jsonl，字段为 sample_id/Response/ResponseSolution/DialogueAgreeSolution。
3. 分别调用 `flow_skill_mining_v1/replay/evaluate_replay_outputs.py` 评估 exact/canonical/F1/checker pass。
4. 优先比较 forbidden_action_rate、missing_action_warning_rate、strong confirmation precision。
5. 对低分桶按 scene/intent/solution 回放，形成下一轮 skill patch。
