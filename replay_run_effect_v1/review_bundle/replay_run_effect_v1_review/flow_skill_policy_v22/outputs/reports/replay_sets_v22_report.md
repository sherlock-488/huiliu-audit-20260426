# Replay Sets v22 Report

- fulfillment_delivery stable/action/challenge: `76` / `65` / `45`
- receipt_quality stable/action/challenge: `79` / `79` / `41`
- FD DialogueAgree non-empty stable/action/challenge: `5` / `13` / `8`
- RQ DialogueAgree non-empty stable/action/challenge: `20` / `25` / `5`
- FD close/ack/transfer stable/action/challenge: `26` / `7` / `5`
- RQ close/ack/transfer stable/action/challenge: `24` / `10` / `3`

## FD Stable ResponseSolution
- `无`: `56`
- `操作赔付-优惠券-10元`: `7`
- `系统催单`: `6`
- `引导自助联系骑手`: `4`
- `操作赔付-优惠券-8元`: `2`
- `智能跟单`: `1`

## FD Action Intent Distribution
- `delivery_urge`: `24`
- `<NONE>`: `20`
- `eta_question`: `6`
- `contact_rider`: `4`
- `compensation_request`: `3`
- `eta_question,contact_rider`: `1`
- `delivery_urge,compensation_request`: `1`
- `delivery_urge,compensation_request,confirm_compensation`: `1`
- `delivery_urge,contact_rider`: `1`
- `eta_question,delivery_urge`: `1`
- `refund_request,confirm_refund`: `1`
- `refund_request`: `1`
- `upload_image`: `1`

## FD Challenge Rule Distribution
- `FD-OTHER`: `20`
- `FD-03`: `17`
- `FD-CONFIRM`: `2`
- `FD-02`: `2`
- `FD-04`: `1`
- `FD-05A`: `1`
- `FD-ACK`: `1`
- `FD-CLOSE`: `1`

## RQ Stable ResponseSolution
- `无`: `41`
- `选择商品`: `8`
- `小象单商品退款-100%`: `8`
- `小象单商品退款-50%`: `7`
- `小象单商品退款-30%`: `4`
- `小象单商品退款-10%`: `2`
- `操作赔付-优惠券-8元`: `2`
- `小象单商品退款-60%`: `2`
- `操作赔付-优惠券-3元`: `2`
- `小象单商品退款-40%`: `1`
- `小象单商品退款-80%`: `1`
- `操作赔付-优惠券-5元`: `1`

## RQ Action Intent Distribution
- `<NONE>`: `31`
- `quality_issue`: `8`
- `quality_issue,upload_image`: `8`
- `upload_image`: `8`
- `refund_request`: `5`
- `compensation_request`: `5`
- `refund_request,quality_issue`: `3`
- `quality_issue,select_product`: `2`
- `confirm_refund`: `2`
- `refund_request,quality_issue,select_product`: `1`
- `compensation_request,select_product`: `1`
- `refund_request,confirm_refund`: `1`
- `compensation_request,quality_issue`: `1`
- `refund_progress`: `1`
- `eta_question,delivery_urge,refund_progress,refund_request`: `1`
- `eta_question,delivery_urge`: `1`

## RQ Challenge Rule Distribution
- `RQ-OTHER`: `23`
- `RQ-01`: `8`
- `RQ-11`: `4`
- `RQ-02`: `4`
- `RQ-CLARIFY_OR_TRANSFER`: `1`
- `RQ-CONFIRM`: `1`
