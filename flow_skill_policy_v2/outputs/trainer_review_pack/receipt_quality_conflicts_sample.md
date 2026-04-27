# 收货品质 Policy 冲突样本

请对每条样本选择：A. gold 正确，oracle 过严/过度执行；B. oracle 正确，训练标注漏流程；C. 两者都可接受；D. 需要补充信号/流程。

## 1. a84ba555253ba5833ef7dc92e78d546c3aa57d52
- scene: `收货场景-品质问题`
- last_user_query: 谢谢
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `小象单商品退款-xx%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 2. 9802aa393ac53581df475e399e90bac207b11c3f
- scene: `收货场景-品质问题`
- last_user_query: 好的，知道了
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `操作赔付-优惠券-xx元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 3. 00f2860ed5674bd45a33fc01da3997f5da82d293
- scene: `收货场景-品质问题`
- last_user_query: 人工
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `选择商品`
- oracle rule: `RQ-02`
- 差异原因: 品质/日期/口感等质量问题缺具体商品，先选择商品。
- 训练师选择: A / B / C / D

## 4. 6abb581729866370710397ec2ad603970953f433
- scene: `收货场景-品质问题`
- last_user_query: 人工
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:5~8元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `选择商品`
- oracle rule: `RQ-02`
- 差异原因: 品质/日期/口感等质量问题缺具体商品，先选择商品。
- 训练师选择: A / B / C / D

## 5. c2d240318f71ca0a4a94f6dec832dfcfdc73379f
- scene: `收货场景-品质问题`
- last_user_query: 洗衣液今天打开看都是漏的
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `选择商品`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-01`
- 差异原因: 超售后或商品不可退款时，不得选择单商品退款，也不要错误引导选择商品。
- 训练师选择: A / B / C / D

## 6. 78dbe3e798b111da3c6f6bd3a6e073929524fd9e
- scene: `收货场景-品质问题`
- last_user_query: 商品有质量问题
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单部分退款; 订单是否超售后=否
- gold ResponseSolution: `选择商品`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-01`
- 差异原因: 超售后或商品不可退款时，不得选择单商品退款，也不要错误引导选择商品。
- 训练师选择: A / B / C / D

## 7. a3733183e0267960405e91765b5cab995398536d
- scene: `收货场景-品质问题`
- last_user_query: 芹菜空心的
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=未知状态; 订单是否超售后=否
- gold ResponseSolution: `选择商品`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-01`
- 差异原因: 超售后或商品不可退款时，不得选择单商品退款，也不要错误引导选择商品。
- 训练师选择: A / B / C / D

## 8. e63e27d9b2d2379000d58c3ca5c92709eb8d19d4
- scene: `收货场景-品质问题`
- last_user_query: 没有了，谢谢
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `小象单商品退款-xx%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 9. 6c5756ef558d7ec389403fe85365c8c9b0ad3a6b
- scene: `收货场景-品质问题`
- last_user_query: 没有了
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `小象单商品退款-xx%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 10. 81b943e614de1bb8f407229ceadcd2e090156684
- scene: `收货场景-品质问题`
- last_user_query: 没有了
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 11. 69b92a405834cf3b9eb8149654a44aedd4a0456d
- scene: `收货场景-品质问题`
- last_user_query: 嗯嗯，谢谢
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `加急催促退款审核`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 12. c237e8c4736b089925080cf51aedabe1c91fa9bd
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:商品有质量问题，牛奶外表很脏
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-40%`
- oracle ResponseSolution: `小象单商品退款-40%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 13. 756fc5a447b8bc29dbf1f6c07edb4b8a18cee3c9
- scene: `收货场景-品质问题`
- last_user_query: 主要是这一批次都是软的呀
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 14. 5acee55c660d17570be9f5771eb05ea2dd89c7e9
- scene: `收货场景-品质问题`
- last_user_query: 没有
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 15. 211a06bc869d71128a43b79cb41ed591309699ac
- scene: `收货场景-品质问题`
- last_user_query: 没了，就这个问题
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 16. 4f8dca6a83e9247abfda712f8db77ec40a0a8b63
- scene: `收货场景-品质问题`
- last_user_query: 行
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `操作赔付-优惠券-xx元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 17. ec403eeaaf7165418ea83e9911b631727b41ef07
- scene: `收货场景-品质问题`
- last_user_query: 一定要这么抠吗
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `小象单商品退款-xx%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 18. 994351143d324a08db9fd3a4de0d5ac3c0716293
- scene: `收货场景-品质问题`
- last_user_query: 行
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `操作赔付-优惠券-xx元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 19. 3be9f9affd78ed9449e8bffc9e9cf1602791203b
- scene: `收货场景-品质问题`
- last_user_query: 钱什么时候能退啊
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:5~8元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 20. 44ecf0d5f0fe67859cd7dfc888b03a9b9d0fae64
- scene: `收货场景-品质问题`
- last_user_query: 嗯，什么时候退完给我啊
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:5~8元; 是否赔付过=否; 订单退款状态=订单部分退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 21. 1073928bbf1daded4ab6784dac05238c09324d73
- scene: `收货场景-品质问题`
- last_user_query: 万一打开都坏了呢，给我都退了
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `加急催促退款审核`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 22. e65b130198799507ec2343737db8211f2cf772f4
- scene: `收货场景-品质问题`
- last_user_query: 我要求整单全退
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~8元; 是否赔付过=否; 订单退款状态=订单部分退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `操作赔付-优惠券-8元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 23. ea2db98cfa2b91c3c0ca20f7923049809c0d2657
- scene: `收货场景-品质问题`
- last_user_query: 行吧
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:5~8元; 是否赔付过=否; 订单退款状态=订单部分退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 24. 1b32b76646b2df127183aae2af4f50c9bc1b30fe
- scene: `收货场景-品质问题`
- last_user_query: 我要全退，根本没法吃了，我就吃了一个，味道不对我没再拆开，我可以把其他的退回去
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~8元; 是否赔付过=否; 订单退款状态=订单部分退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 25. a4539d9f5b090c3b2110d8b0fb6167a972b37a1d
- scene: `收货场景-品质问题`
- last_user_query: 可以
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~8元; 是否赔付过=否; 订单退款状态=未知状态; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `操作赔付-优惠券-8元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 26. ec033929845ec5f02ebbcdb896f0957f375ae12e
- scene: `收货场景-品质问题`
- last_user_query: 可以
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `选择商品`
- oracle rule: `RQ-02`
- 差异原因: 品质/日期/口感等质量问题缺具体商品，先选择商品。
- 训练师选择: A / B / C / D

## 27. 0821516f08453ae02456bec8c15c8c0896e463b4
- scene: `收货场景-品质问题`
- last_user_query: 好的
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 28. 36d9708ff80f1481354c661658305334cbdadd1a
- scene: `收货场景-品质问题`
- last_user_query: 不行
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `操作赔付-优惠券-xx元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 29. 4d4c8a208d43c05ae47456231bc6ec9da4dc1af8
- scene: `收货场景-品质问题`
- last_user_query: 都不能吃了就给这么少吗
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 30. f9ae9f2bcf32de71ff38544b64070941e2ef17cb
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:鸡蛋出现裂缝，有的鸡蛋上有异物
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `加急催促退款审核`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 31. fd70a77fb45385ac911e2c0513878fffdafd96c6
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:用户上传的图片显示车厘子外部有一些凹陷，存在不新鲜情况，无法判断是否有口感问题
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:5~8元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `小象单商品退款-50%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 32. 490a19e4808d2813d992b5d0883142b11e765d0b
- scene: `收货场景-品质问题`
- last_user_query: 因为泥是压在一起的，很像人为的，不像是拔出来就这样
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~8元; 是否赔付过=否; 订单退款状态=未知状态; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `小象单商品退款-50%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 33. 8505a5e90eed60e5386ba4ba007b4effbc2f81b3
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:这是一张蓝莓的图片，图中显示部分存在干瘪的情况，大小不均匀，与用户描述的质量问题一致
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `选择商品`
- oracle rule: `RQ-02`
- 差异原因: 品质/日期/口感等质量问题缺具体商品，先选择商品。
- 训练师选择: A / B / C / D

## 34. 3e84a41329516471a2c709934f520e00be773424
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:这是一个牛油果商品的图片，可以看出来商品表面发青，与用户反馈的商品太生符合一致
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 35. a75be3fe304589c569d83b0de279cabbca631a2b
- scene: `收货场景-品质问题`
- last_user_query: 商品不新鲜，临期商品，退款
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `选择商品`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-01`
- 差异原因: 超售后或商品不可退款时，不得选择单商品退款，也不要错误引导选择商品。
- 训练师选择: A / B / C / D

## 36. bd1a3b383d0ccc92dae928f59e0541726f48ed50
- scene: `收货场景-品质问题`
- last_user_query: 碎了三个吧，盒子都搞脏了
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-30%`
- oracle ResponseSolution: `小象单商品退款-30%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 37. a062994ecafd9bc5db4512c8df40a2701a38cc35
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:面包蟹看起来不新鲜
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-30%`
- oracle ResponseSolution: `小象单商品退款-30%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 38. b342ebc0d34907d0b76511518dda2389f04053f4
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:车厘子柄发黑，部分柄已经散落在袋子里
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:5~8元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-30%`
- oracle ResponseSolution: `小象单商品退款-30%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 39. a4901634d699ab42c24cd546d30c5bdcff08a3a7
- scene: `收货场景-品质问题`
- last_user_query: 不可以，少称你光补上就算了？
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~8元; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-30%`
- oracle ResponseSolution: `操作赔付-优惠券-8元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 40. f512976fdab75bfb7c14b27c40d3935f6ca0c1cb
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:茴香有很多泥，与用户反馈的重量都在泥上相符
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~8元; 是否赔付过=否; 订单退款状态=未知状态; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-30%`
- oracle ResponseSolution: `小象单商品退款-30%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 41. abe4352d45f7b40b9ac43d491a95ed4fc75c6896
- scene: `收货场景-品质问题`
- last_user_query: 行吧
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `操作赔付-优惠券-xx元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 42. ec270a35cd25f82227299740b3db61b590de5d68
- scene: `收货场景-品质问题`
- last_user_query: 那行吧
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 43. 786b0a669b41b3a7cd13228dcceb18deacd7b82b
- scene: `收货场景-品质问题`
- last_user_query: 就按你说的50%退吧，毕竟菜是好的
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~8元; 是否赔付过=否; 订单退款状态=未知状态; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-50%`
- oracle ResponseSolution: `操作赔付-优惠券-8元`
- oracle rule: `RQ-11`
- 差异原因: 用户要求赔付/强烈不满且赔付信号允许；执行赔付需用户确认，金额不得超过上限。
- 训练师选择: A / B / C / D

## 44. 54c05833e252c9d1fd3c36dd67a243c25ffdc7d8
- scene: `收货场景-品质问题`
- last_user_query: 鲜活小红扇贝500g（10-20只）
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 45. af9a146b9e9038c5c3c18ad15be994e85b51c6ad
- scene: `收货场景-品质问题`
- last_user_query: 【平价】土鸡蛋8枚400g
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `加急催促退款审核`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 46. 7c4b285d5111eca69f2f15b1edf7c193dd0963ce
- scene: `收货场景-品质问题`
- last_user_query: 一个鸡蛋臭了，还有一个有裂缝
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `加急催促退款审核`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 47. 677722d3d4d0d6ae2c106283df3d2470872320ab
- scene: `收货场景-品质问题`
- last_user_query: 象大厨鲜食米饭210g
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=是; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:5~8元; 是否赔付过=否; 订单退款状态=订单部分退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 48. e0fe50e32ff9be2e16fcad126bac5ae771310e94
- scene: `收货场景-品质问题`
- last_user_query: 周黑鸭趣享卤鸭锁骨120g
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 订单是否可赔付=是, 赔付形式:优惠券, 赔付金额:3~8元; 是否赔付过=否; 订单退款状态=订单部分退款; 订单是否超售后=否
- gold ResponseSolution: `无`
- oracle ResponseSolution: `催促退款审核;退审跟单`
- oracle rule: `RQ-09`
- 差异原因: 退款进行中且用户咨询/催促进度，使用催审/跟单类方案，不要求 DialogueAgreeSolution。
- 训练师选择: A / B / C / D

## 49. 0e135a62e902ff0b8eec23514c725a4fe92e990f
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:用户发了车厘子的图片，部分存在颜色发深发软的情况，与用户反馈的水分不足、发软相符
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-10%`
- oracle ResponseSolution: `小象单商品退款-10%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D

## 50. b7f2bef9a2bc25dc70d4837981e66ebc3cb8e76f
- scene: `收货场景-品质问题`
- last_user_query: 【图片】 ->系统识别图片结果:车厘子个头大小不一，与用户反馈的个头差距不小相符
- key_signals: 订单状态=已完成; 是否为配送单=是; 订单骑手状态=已送达; 订单是否超时=否; 是否可取消订单=否; 是否赔付过=否; 订单退款状态=订单无退款; 订单是否超售后=否
- gold ResponseSolution: `小象单商品退款-10%`
- oracle ResponseSolution: `小象单商品退款-10%`
- oracle rule: `RQ-07`
- 差异原因: 商品、图片、原因、比例/数量等前置满足后，可提出或执行单商品退款；用户确认后 DialogueAgreeSolution 才非空。
- 训练师选择: A / B / C / D
