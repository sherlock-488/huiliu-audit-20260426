# 履约配送 Policy 冲突样本

请对每条样本选择：A. gold 正确，oracle 过严/过度执行；B. oracle 正确，训练标注漏流程；C. 两者都可接受；D. 需要补充信号/流程。

## 1. 3a80545a1283ae7ce3f25aa9c196f214a8e86c21
- scene: `履约场景-配送问题`
- last_user_query: 没有了
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 2. 33a38408505c2baef03614920416d68a8e01be4d
- scene: `履约场景-配送问题`
- last_user_query: 你好，订单为啥要停止配送
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 3. 537740480fc0010058bbf92166e07e645befa6ac
- scene: `履约场景-配送问题`
- last_user_query: 没了，谢谢
- key_signals: 订单状态=取消; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `取消订单`
- oracle rule: `FD-08`
- 差异原因: 用户有取消诉求且订单可取消；只有明确确认取消时 DialogueAgreeSolution 才能非空。
- 训练师选择: A / B / C / D

## 4. 7ddac8a8439551926ee7df2026187cb03835bc61
- scene: `履约场景-配送问题`
- last_user_query: 好的
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=无骑手接单; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `加急调度`
- oracle rule: `FD-02`
- 差异原因: 骑手状态为无骑手接单/待接单，用户问送达或催促时优先加急调度。
- 训练师选择: A / B / C / D

## 5. 05dc899bee1a1341004062d11c651a6d43ff9f2a
- scene: `履约场景-配送问题`
- last_user_query: 那现在怎么办
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=已返回门店; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 6. 5d6060e50e8d3426252edd4cc5e8fb1e7fd40d91
- scene: `履约场景-配送问题`
- last_user_query: 我弄一下
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=已返回门店; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 7. 224a30964d3eeef2c2776cf287633ae5b69004a5
- scene: `履约场景-配送问题`
- last_user_query: 没有，就这样吧
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=已返回门店; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 8. ae0b1d9c65634dd465d30394a0ace5c1bda8e996
- scene: `履约场景-配送问题`
- last_user_query: 没了
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=无骑手接单; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `加急调度`
- oracle rule: `FD-04`
- 差异原因: 骑手状态为无骑手接单/待接单，用户问送达或催促时优先加急调度。
- 训练师选择: A / B / C / D

## 9. b7d6bfcd79d2646f272d97b356b7022261e375ce
- scene: `履约场景-配送问题`
- last_user_query: 嗯嗯
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 10. 1b3bc3f792b0e4ce9735d25e4298f207892e7618
- scene: `履约场景-配送问题`
- last_user_query: 我的订单什么情况
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 11. 8c78c13659a8d3e3799b4984fd48a0f4721a206c
- scene: `履约场景-配送问题`
- last_user_query: 给我催催
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=无骑手接单; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `加急调度`
- oracle rule: `FD-04`
- 差异原因: 骑手状态为无骑手接单/待接单，用户问送达或催促时优先加急调度。
- 训练师选择: A / B / C / D

## 12. 82fdbb9bca1a4c9d620837c1de8b0f9443baeeef
- scene: `履约场景-配送问题`
- last_user_query: 快点啊
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 13. 4e41965061e8c1a7c6bc720959e78d2d5a349484
- scene: `履约场景-配送问题`
- last_user_query: 赶紧的，我着急用呢
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 14. 1bb9818b912ef348bf3f1176aab81efed13fa77f
- scene: `履约场景-配送问题`
- last_user_query: 赶紧的，我着急用呢
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `再次外呼骑手-催促配送`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 15. e9b2c72b0ac342556761d1babbf8320b25beb462
- scene: `履约场景-配送问题`
- last_user_query: 嗯，别忘了赶紧送
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=是; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-11`
- 差异原因: 不可赔或已赔时禁止再次主动赔付，可改为催单、加急或解释。
- 训练师选择: A / B / C / D

## 16. d4839fe02480247015d34e1deaa6bee497a09422
- scene: `履约场景-配送问题`
- last_user_query: 好，快点
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `外呼骑手-催促配送`
- oracle rule: `FD-05B`
- 差异原因: 用户明确要求客服帮忙联系骑手，外呼类方案不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 17. 0032a280f3b0d0d62400f2ac042f75eb27011e12
- scene: `履约场景-配送问题`
- last_user_query: 好，快点
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `外呼骑手-催促配送`
- oracle rule: `FD-05B`
- 差异原因: 用户明确要求客服帮忙联系骑手，外呼类方案不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 18. aba201bd7c059a6bb1787a19b37b43dfb2038b9d
- scene: `履约场景-配送问题`
- last_user_query: 希望以后不要这么慢了
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 19. 037cd0d5624882cde9ecb940a921a3f032b4bfe2
- scene: `履约场景-配送问题`
- last_user_query: OK
- key_signals: 订单状态=取消; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `取消订单`
- oracle rule: `FD-08`
- 差异原因: 用户有取消诉求且订单可取消；只有明确确认取消时 DialogueAgreeSolution 才能非空。
- 训练师选择: A / B / C / D

## 20. 4340b4a84defb462766100b2e20ef399c7acb50b
- scene: `履约场景-配送问题`
- last_user_query: 没了吧
- key_signals: 订单状态=取消; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `取消订单`
- oracle rule: `FD-08`
- 差异原因: 用户有取消诉求且订单可取消；只有明确确认取消时 DialogueAgreeSolution 才能非空。
- 训练师选择: A / B / C / D

## 21. c29d5e0bae5ff002036ab7b77a90661a410b2d24
- scene: `履约场景-配送问题`
- last_user_query: 投诉骑手
- key_signals: 订单状态=取消; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `取消订单`
- oracle rule: `FD-08`
- 差异原因: 用户有取消诉求且订单可取消；只有明确确认取消时 DialogueAgreeSolution 才能非空。
- 训练师选择: A / B / C / D

## 22. 6704ad57a2f78e05f033fba3827c906d569dfbc3
- scene: `履约场景-配送问题`
- last_user_query: 嗯
- key_signals: 订单状态=取消; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `取消订单`
- oracle rule: `FD-08`
- 差异原因: 用户有取消诉求且订单可取消；只有明确确认取消时 DialogueAgreeSolution 才能非空。
- 训练师选择: A / B / C / D

## 23. 7c1f0ff0efe3e21a91e1e9bf7d7b375c521b1d51
- scene: `履约场景-配送问题`
- last_user_query: 没有
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=无骑手接单; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `加急调度`
- oracle rule: `FD-02`
- 差异原因: 骑手状态为无骑手接单/待接单，用户问送达或催促时优先加急调度。
- 训练师选择: A / B / C / D

## 24. 25c44061874a2a2999766ec8b3f1a0cff2410774
- scene: `履约场景-配送问题`
- last_user_query: 你们这个骑手什么鬼  一直找不到地方
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 25. 2343c3b371e7aeba92204c487de4b3ab894baddb
- scene: `履约场景-配送问题`
- last_user_query: 快啊快啊
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 26. 241281d8d123d42eea69b5f6b8dfbbec300e820f
- scene: `履约场景-配送问题`
- last_user_query: 快一点吧，都超时这么久了
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 27. 43fed2f2ef4e39e731c3b1e44eb4a0ccc73b6594
- scene: `履约场景-配送问题`
- last_user_query: 人工客服
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 28. 0dc7d5034ff214eaecc008fc8af623c652e99f4b
- scene: `履约场景-配送问题`
- last_user_query: 人工
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 29. 08242794886028870dc4d0510d1617bd8accc8bb
- scene: `履约场景-配送问题`
- last_user_query: 怎么联系骑手
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 30. 928925781ec7bc08a7ef55dbb3924d5cec4ac873
- scene: `履约场景-配送问题`
- last_user_query: 没事了，我找骑手说就行
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 31. bc5481e0516d2b3fafc2d82127915bf123362544
- scene: `履约场景-配送问题`
- last_user_query: 我的订单什么时候送到
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=无骑手接单; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `加急调度`
- oracle rule: `FD-02`
- 差异原因: 骑手状态为无骑手接单/待接单，用户问送达或催促时优先加急调度。
- 训练师选择: A / B / C / D

## 32. e8d87341580b9b96b3fc9d16b61306adc27ef851
- scene: `履约场景-配送问题`
- last_user_query: 我的订单什么时候送到
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=已返回门店; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 33. 70cd97341d0cea23e1e9b14f459fc98eb560418b
- scene: `履约场景-配送问题`
- last_user_query: 怎么还没送到
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 34. a5f5c0de514c53c7f5fef267a9bc084eda9dd36a
- scene: `履约场景-配送问题`
- last_user_query: 什么时候送到
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:10~15元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 35. 74ae95744463a60455da5edbf3acea1a2d08d203
- scene: `履约场景-配送问题`
- last_user_query: 啥时候送达啊，问骑手了吗
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 36. cf3e06fc48d0b33eeb84b7fab9224b0f90d0533d
- scene: `履约场景-配送问题`
- last_user_query: 怎么还没配送
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=无骑手接单; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `加急调度`
- oracle rule: `FD-04`
- 差异原因: 骑手状态为无骑手接单/待接单，用户问送达或催促时优先加急调度。
- 训练师选择: A / B / C / D

## 37. 857a5362c014b4d423f5fa2b8e64b92fe8b6373d
- scene: `履约场景-配送问题`
- last_user_query: 嗯
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 38. 8b5163a01f10d0977fd70ad284e4b494b60a9afc
- scene: `履约场景-配送问题`
- last_user_query: 好谢谢
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 39. f0861d2f68caaabb5f6f85e4b14157d91c0d6bd1
- scene: `履约场景-配送问题`
- last_user_query: 5分钟？
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=是; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~5元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `智能跟单`
- oracle ResponseSolution: `再次外呼骑手-催促配送`
- oracle rule: `FD-06`
- 差异原因: 最近外呼骑手未接通且用户持续追问，可再次外呼。
- 训练师选择: A / B / C / D

## 40. b5d5e6a9031133324000fda40035e84de40d5566
- scene: `履约场景-配送问题`
- last_user_query: 我知道是17:57到，问题是我要求加急并没有加急啊，我很着急啊
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `无`
- oracle rule: `FD-01`
- 差异原因: 普通 ETA 咨询可只告知预计送达时间，不承诺一定准时。
- 训练师选择: A / B / C / D

## 41. b2c8f10994db5b4d54fa8b6d47719cdfb213d306
- scene: `履约场景-配送问题`
- last_user_query: 急
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=否; 是否可取消订单=是; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 42. a8bf4ef94a426e262e93c2c7b370922ed1387d2e
- scene: `履约场景-配送问题`
- last_user_query: 他怎么这么慢，催促配送
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=骑手已接单; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 43. 622b407c2ed5e6feec6c58a040a3b15fbb24ce1b
- scene: `履约场景-配送问题`
- last_user_query: 我的意思是能不能快点啊，等很久了啊
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=是; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:5~8元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 44. e05d6cc1ad99f347ecb8867bc7f903bad5f11798
- scene: `履约场景-配送问题`
- last_user_query: 对啊，都超时了，半天看不到骑手
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=是; 是否赔付过=否
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 45. d0619574e60682aada7c63c37ea0812a9bd29b25
- scene: `履约场景-配送问题`
- last_user_query: 还得等到啥时候啊
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- 差异原因: 用户明确催配送且系统催单 eligible；智能跟单可作为后续跟进，不替代主动作。
- 训练师选择: A / B / C / D

## 46. abe5582af38752be7a2b74395f0b9a43c9d2259f
- scene: `履约场景-配送问题`
- last_user_query: 很着急
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 47. 0ae1c109b4634cb3b936b621525f27fdb166954d
- scene: `履约场景-配送问题`
- last_user_query: 你说催就催了啊，我不信，你们每次都这样
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=否; 履约中未超时订单是否有超时风险=是; 是否可取消订单=是; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~5元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `外呼骑手-催促配送`
- oracle ResponseSolution: `引导自助联系骑手`
- oracle rule: `FD-05A`
- 差异原因: 用户想联系骑手且骑手已接单/配送中，优先引导自助联系。
- 训练师选择: A / B / C / D

## 48. 7ac1e66186b245ddc59f9e16a58c5d5a1e6a6e9a
- scene: `履约场景-配送问题`
- last_user_query: 太少了吧
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=否; 订单退款状态=未知状态; 订单是否超售后=否
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `操作赔付-优惠券-10元`
- oracle rule: `FD-10`
- 差异原因: 用户因超时/配送慢要求赔付或强烈不满，且赔付信号允许；赔付执行需用户确认。
- 训练师选择: A / B / C / D

## 49. c73a49f1a92ce524fd19964a90ce88cf013e2205
- scene: `履约场景-配送问题`
- last_user_query: 太少了
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `操作赔付-优惠券-10元`
- oracle rule: `FD-10`
- 差异原因: 用户因超时/配送慢要求赔付或强烈不满，且赔付信号允许；赔付执行需用户确认。
- 训练师选择: A / B / C / D

## 50. 303597288bf4b9c9b4a458cda3e98a48ab7ce5f3
- scene: `履约场景-配送问题`
- last_user_query: 这么少？给我20元
- key_signals: 订单状态=履约中; 是否为配送单=是; 订单骑手状态=配送中; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是，赔付形式=优惠券，赔付金额=8~10元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `操作赔付-优惠券-10元`
- oracle ResponseSolution: `操作赔付-优惠券-10元`
- oracle rule: `FD-10`
- 差异原因: 用户因超时/配送慢要求赔付或强烈不满，且赔付信号允许；赔付执行需用户确认。
- 训练师选择: A / B / C / D
