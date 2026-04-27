# Confirmation Resolver v22 Report

- v21_confirm_like_with_pending: `1108`
- v21_trigger_but_v22_blocked: `371`
- v22_maybe_accept_pending: `368`
- dialogue_agree_non_empty_cases: `913`
- dialogue_agree_covered_or_preserved: `913`

## Blocked Examples
- `dd43828ff8a815dc8e882052e90545f40e888c4a` `无门槛，可以直接用吗` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
- `a69339951971bc8b0d5cbc11b9b6f2da45a565bc` `不可以，少了` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
- `acf69f36e77f9708e9e807c99cd72c501151deb2` `行知道了，超时这么久` pending=`操作赔付-优惠券-xx元` debug=`['intent:delivery_urge', 'confirm_like']`
- `b00da3c6930d44dc3d4a2e35ba061ba60734cac4` `不行太少` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like', 'confirm_blocked_by_question_or_reject']`
- `ed2028c80d0475b161bc4cb8b6f0bc7c6e581ead` `不想接受` pending=`小象单商品退款-xx%` debug=`['confirm_like']`
- `07e5183e41e3c21734056c2a4b9292b379d72ae1` `什么情况啊，我要吃东西啊，你给我退了我吃什么啊？` pending=`小象整单申请退款` debug=`['intent:refund_request', 'confirm_like', 'confirm_blocked_by_question_or_reject']`
- `089bec1cb08d101bb0460e652ba1d6c55237e859` `好的，你帮我操作了是吧` pending=`小象单商品退款-xx%` debug=`['confirm_like']`
- `625806a7923ffe766499a8f953b7c027ea501179` `我等着做饭呢，你给我退了我吃什么啊？` pending=`小象整单申请退款` debug=`['intent:refund_request', 'confirm_like', 'confirm_blocked_by_question_or_reject']`
- `4c783a6cbdbb0f5b96d3200751f5c16e769fe31f` `行，我填一下吧` pending=`小象整单申请退款` debug=`['confirm_like']`
- `6d1c95ab725a4bdebea41738fb890b5a3d6784ca` `可以直接用吗` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
- `6fef94893aad26b2eb12cb0bb130b0a127019ba2` `行，好的，到账了吗，在哪里查看` pending=`操作赔付-优惠券-xx元` debug=`['intent:refund_progress', 'confirm_like', 'confirm_blocked_by_question_or_reject']`
- `5ea3265ed63accf8242b823c9f9e116bf393e931` `我可以加钱` pending=`取消订单` debug=`['confirm_like']`
- `6b40637b8fe27e243291f678a2f3c3d092ad4a21` `可以，你帮我退了吧` pending=`会员卡退款` debug=`['intent:refund_request', 'confirm_like']`
- `cb0f103ebf5df1f041dea124577baf32509cce53` `好，也可以` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
- `fb5f440b5bb56b9cffb9babc29bbe02089c51130` `好的，麻烦了` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
- `42e54a11a61939e04554cb4bdd7dbf8b8700a5f4` `不行，才10元，不要` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like', 'confirm_blocked_by_question_or_reject']`
- `ebd6e7eb92f1a32eeb0a5cf620440a6ce45e702c` `不行，我要更多，给我20` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like', 'confirm_blocked_by_question_or_reject']`
- `3383530c34f01ffcf7a9a025f2077c676479c417` `行行行` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
- `da560283d1d82034823bcaccdf2276b129348147` `行，拜拜` pending=`会员卡退款` debug=`['confirm_like']`
- `e0481f25fa26d6662f3000a8a0b0b0befe1daa69` `退了就行` pending=`会员卡退款` debug=`['confirm_like']`
- `8be1ef1f1f2f1531473c5565a535e0f0066d97b1` `我看了一下使用规则，好像也还行` pending=`会员卡退款` debug=`['confirm_like']`
- `c24e897ff4d5ed5c22d2c0791fcc8c140dfe1510` `行，退就行` pending=`会员卡退款` debug=`['confirm_like']`
- `5c7adf55dbaf55b3b92d60d0cee0a8c330eee1a8` `不行` pending=`小象单商品退款-xx%` debug=`['confirm_like', 'confirm_blocked_by_question_or_reject']`
- `a9103f4820db446c532ec00899813a92dc13eecc` `可以的可以的` pending=`小象单商品退款-xx%` debug=`['confirm_like']`
- `a06ec4731fc67105ea65ba0ae82b36912b3fd4e3` `行，我看你们这有一个不回本包退，这是什么` pending=`会员卡退款` debug=`['confirm_like']`
- `cb6e93ceb49a197d24c08bd49e9cfa139a1c5208` `确认退款` pending=`会员卡退款` debug=`['intent:refund_request', 'confirm_like']`
- `839e721d341b6840a971280ff3d2d9004044236c` `好的，我还想问一下怎么查询省钱记录？` pending=`会员卡退款` debug=`['confirm_like', 'confirm_blocked_by_question_or_reject']`
- `0d98d0ee855417c9580f42c4bd1030ac12f96272` `行，可以` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
- `19178038e9e62634fc0b00ca1e88fd01c0ad72a6` `那也行` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
- `3cecf5dbeb7a67b466388279d06c70d4bc6dabd5` `不可以` pending=`操作赔付-优惠券-xx元` debug=`['confirm_like']`
