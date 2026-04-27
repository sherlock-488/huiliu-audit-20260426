# Fulfillment Delivery v21 Remaining Conflicts

训练师选项：A. gold 正确，oracle 过严；B. oracle 正确；C. 两者都可接受；D. 需要补充信号/流程。

## 1. 8c78c13659a8d3e3799b4984fd48a0f4721a206c
- scene: `履约场景-配送问题`
- last_user_query: 给我催催
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `加急调度`
- oracle rule: `FD-04`
- rationale: 当前询问 ETA/催接单/催配送且骑手无接单，优先加急调度。
- 训练师选择: A / B / C / D

## 2. 82fdbb9bca1a4c9d620837c1de8b0f9443baeeef
- scene: `履约场景-配送问题`
- last_user_query: 快点啊
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 3. 4e41965061e8c1a7c6bc720959e78d2d5a349484
- scene: `履约场景-配送问题`
- last_user_query: 赶紧的，我着急用呢
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 4. 1bb9818b912ef348bf3f1176aab81efed13fa77f
- scene: `履约场景-配送问题`
- last_user_query: 赶紧的，我着急用呢
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `再次外呼骑手-催促配送`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 5. e9b2c72b0ac342556761d1babbf8320b25beb462
- scene: `履约场景-配送问题`
- last_user_query: 嗯，别忘了赶紧送
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-11`
- rationale: 用户确认赔付但订单不可赔/已赔，禁止填赔付。
- 训练师选择: A / B / C / D

## 6. d4839fe02480247015d34e1deaa6bee497a09422
- scene: `履约场景-配送问题`
- last_user_query: 好，快点
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 7. 0032a280f3b0d0d62400f2ac042f75eb27011e12
- scene: `履约场景-配送问题`
- last_user_query: 好，快点
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 8. c29d5e0bae5ff002036ab7b77a90661a410b2d24
- scene: `履约场景-配送问题`
- last_user_query: 投诉骑手
- current_turn_intent: `['compensation_request']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `操作赔付-优惠券-xx元`
- oracle rule: `FD-10`
- rationale: 当前用户要求赔付/强烈不满且可赔未赔；first_offer 取赔付区间下限。
- 训练师选择: A / B / C / D

## 9. 241281d8d123d42eea69b5f6b8dfbbec300e820f
- scene: `履约场景-配送问题`
- last_user_query: 快一点吧，都超时这么久了
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 10. 08242794886028870dc4d0510d1617bd8accc8bb
- scene: `履约场景-配送问题`
- last_user_query: 怎么联系骑手
- current_turn_intent: `['contact_rider']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- rationale: 当前想联系骑手但未明确要求客服外呼，优先自助联系。
- 训练师选择: A / B / C / D

## 11. bc5481e0516d2b3fafc2d82127915bf123362544
- scene: `履约场景-配送问题`
- last_user_query: 我的订单什么时候送到
- current_turn_intent: `['eta_question']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `加急调度`
- oracle rule: `FD-02`
- rationale: 当前询问 ETA/催接单/催配送且骑手无接单，优先加急调度。
- 训练师选择: A / B / C / D

## 12. e8d87341580b9b96b3fc9d16b61306adc27ef851
- scene: `履约场景-配送问题`
- last_user_query: 我的订单什么时候送到
- current_turn_intent: `['eta_question']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 13. 70cd97341d0cea23e1e9b14f459fc98eb560418b
- scene: `履约场景-配送问题`
- last_user_query: 怎么还没送到
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 14. a5f5c0de514c53c7f5fef267a9bc084eda9dd36a
- scene: `履约场景-配送问题`
- last_user_query: 什么时候送到
- current_turn_intent: `['eta_question']`
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 15. 74ae95744463a60455da5edbf3acea1a2d08d203
- scene: `履约场景-配送问题`
- last_user_query: 啥时候送达啊，问骑手了吗
- current_turn_intent: `['contact_rider']`
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- rationale: 当前想联系骑手但未明确要求客服外呼，优先自助联系。
- 训练师选择: A / B / C / D

## 16. cf3e06fc48d0b33eeb84b7fab9224b0f90d0533d
- scene: `履约场景-配送问题`
- last_user_query: 怎么还没配送
- current_turn_intent: `[]`
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 17. 857a5362c014b4d423f5fa2b8e64b92fe8b6373d
- scene: `履约场景-配送问题`
- last_user_query: 嗯
- current_turn_intent: `[]`
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-ACK`
- rationale: 当前只是弱确认/应答，且没有 pending strong solution，不触发动作。
- 训练师选择: A / B / C / D

## 18. 8b5163a01f10d0977fd70ad284e4b494b60a9afc
- scene: `履约场景-配送问题`
- last_user_query: 好谢谢
- current_turn_intent: `[]`
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 19. f0861d2f68caaabb5f6f85e4b14157d91c0d6bd1
- scene: `履约场景-配送问题`
- last_user_query: 5分钟？
- current_turn_intent: `[]`
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 20. b5d5e6a9031133324000fda40035e84de40d5566
- scene: `履约场景-配送问题`
- last_user_query: 我知道是17:57到，问题是我要求加急并没有加急啊，我很着急啊
- current_turn_intent: `[]`
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 21. b2c8f10994db5b4d54fa8b6d47719cdfb213d306
- scene: `履约场景-配送问题`
- last_user_query: 急
- current_turn_intent: `[]`
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 22. e05d6cc1ad99f347ecb8867bc7f903bad5f11798
- scene: `履约场景-配送问题`
- last_user_query: 对啊，都超时了，半天看不到骑手
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 23. d0619574e60682aada7c63c37ea0812a9bd29b25
- scene: `履约场景-配送问题`
- last_user_query: 还得等到啥时候啊
- current_turn_intent: `[]`
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 24. e103ba15640a2ad48aa5ce6051eb1059b140089f
- scene: `履约场景-配送问题`
- last_user_query: 原地呆了那么久
- current_turn_intent: `[]`
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 25. abe5582af38752be7a2b74395f0b9a43c9d2259f
- scene: `履约场景-配送问题`
- last_user_query: 很着急
- current_turn_intent: `[]`
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 26. 0ae1c109b4634cb3b936b621525f27fdb166954d
- scene: `履约场景-配送问题`
- last_user_query: 你说催就催了啊，我不信，你们每次都这样
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 27. 7ac1e66186b245ddc59f9e16a58c5d5a1e6a6e9a
- scene: `履约场景-配送问题`
- last_user_query: 太少了吧
- current_turn_intent: `[]`
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 28. c73a49f1a92ce524fd19964a90ce88cf013e2205
- scene: `履约场景-配送问题`
- last_user_query: 太少了
- current_turn_intent: `[]`
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 29. 303597288bf4b9c9b4a458cda3e98a48ab7ce5f3
- scene: `履约场景-配送问题`
- last_user_query: 这么少？给我20元
- current_turn_intent: `[]`
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 30. ad8ab66b7025b58ae444e088a8a8129c99599f49
- scene: `履约场景-配送问题`
- last_user_query: 不能再多了吗？
- current_turn_intent: `[]`
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 31. 5b6be016fa966aea31d35fb68b687722afdaaefb
- scene: `履约场景-配送问题`
- last_user_query: 超时太严重
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 32. bb762f06ae73e4d2db113d75a12817ef50b7128d
- scene: `履约场景-配送问题`
- last_user_query: 都超时了
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `操作赔付-优惠券-8元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 33. 1a7562f40ab7f16b92f45435f388e86dc2db34f1
- scene: `履约场景-配送问题`
- last_user_query: 怎么样了
- current_turn_intent: `[]`
- gold ResponseSolution: `操作赔付-优惠券-8元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 34. aceb625dc8aa2dc945cce84a3d5684648af6252e
- scene: `履约场景-配送问题`
- last_user_query: 超时严重
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `操作赔付-优惠券-8元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 35. d83efd872362a5407f340f10b4c26b57d23e56ab
- scene: `履约场景-配送问题`
- last_user_query: 算了，那就这样吧
- current_turn_intent: `[]`
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 36. 4aa4bb60646b77a10b0b616243dfa2c33947609e
- scene: `履约场景-配送问题`
- last_user_query: 对啊，都超时了，半天看不到骑手
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `再次外呼骑手-催促配送`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 37. 82b14eb90948dd5fbdcf684e2abe7f9e684c4690
- scene: `履约场景-配送问题`
- last_user_query: 好了吗
- current_turn_intent: `[]`
- gold ResponseSolution: `再次外呼骑手-催促配送`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 38. 90cfc432bf0e0e53230cba8582de35e05f96989b
- scene: `履约场景-配送问题`
- last_user_query: 怎么还要这么久，给我退了吧，我有事出门
- current_turn_intent: `['confirm_refund']`
- gold ResponseSolution: `取消订单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 39. 481aa21421e0e41e2775fac63e5d99608a66f7c7
- scene: `履约场景-配送问题`
- last_user_query: 退了
- current_turn_intent: `[]`
- gold ResponseSolution: `取消订单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 40. 88899aa2fe6b77518220a581f385a55ee8e6a027
- scene: `履约场景-配送问题`
- last_user_query: 这么久10块钱？
- current_turn_intent: `[]`
- gold ResponseSolution: `操作赔付-优惠券-15元`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 41. 6aabf79171691f4079b688ca95354f50f1a5b634
- scene: `履约场景-配送问题`
- last_user_query: 为什么配送超时了，一直迟迟没到？
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `操作赔付-优惠券-15元`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 42. 9b3450280f9e6b11cbba13ec7e0cbf779464a88b
- scene: `履约场景-配送问题`
- last_user_query: 嗯
- current_turn_intent: `[]`
- gold ResponseSolution: `操作赔付-优惠券-15元;智能跟单`
- oracle ResponseSolution: `操作赔付-优惠券-xx元`
- oracle rule: `FD-CONFIRM`
- rationale: 当前弱确认结合 pending strong solution，允许 DialogueAgreeSolution 非空。
- 训练师选择: A / B / C / D

## 43. 35866c47e5239ba653566850cd9bbbdd420ab2dc
- scene: `履约场景-配送问题`
- last_user_query: 我门口没有
- current_turn_intent: `[]`
- gold ResponseSolution: `外呼骑手-协商调换货品`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 44. 4350aba07a26c1b3cb9b38a6f1829ece17b83c5d
- scene: `履约场景-配送问题`
- last_user_query: 快点吧
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `外呼骑手-协商调换货品`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 45. 6eef31c5de5393b6ba2ef1000159a485052593b0
- scene: `履约场景-配送问题`
- last_user_query: 好了吗
- current_turn_intent: `[]`
- gold ResponseSolution: `再次外呼骑手-协商调换货品`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 46. e6f762d0619de5d6f4a6356766526c54ebcd10af
- scene: `履约场景-配送问题`
- last_user_query: 快点吧
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `小象整单申请退款`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 47. e5cd7b89492457341a06ba0b14dff12a4a25c349
- scene: `履约场景-配送问题`
- last_user_query: 已经好几个小时了，退款吧
- current_turn_intent: `['refund_request', 'confirm_refund']`
- gold ResponseSolution: `小象整单申请退款`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 48. e8ff8ef696b263186756430edada746a6f06c12c
- scene: `履约场景-配送问题`
- last_user_query: 我买错商品，不要小米
- current_turn_intent: `[]`
- gold ResponseSolution: `选择商品`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 49. 0f018801436d4ed947584327271cb53fd8dfa45b
- scene: `履约场景-配送问题`
- last_user_query: 【图片】->系统识别图片结果:小米包装袋没有破损，品相完好。
- current_turn_intent: `['upload_image']`
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 50. 55cd31647b4451c4d60476f6b5ac1ee988fcdbfd
- scene: `履约场景-配送问题`
- last_user_query: 可以
- current_turn_intent: `[]`
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D
