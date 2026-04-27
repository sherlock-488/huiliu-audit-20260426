# V2 Conflicts Fixed By v21

训练师选项：A. gold 正确，oracle 过严；B. oracle 正确；C. 两者都可接受；D. 需要补充信号/流程。

## 1. 3a80545a1283ae7ce3f25aa9c196f214a8e86c21
- scene: `履约场景-配送问题`
- last_user_query: 没有了
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 2. 33a38408505c2baef03614920416d68a8e01be4d
- scene: `履约场景-配送问题`
- last_user_query: 你好，订单为啥要停止配送
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 3. 537740480fc0010058bbf92166e07e645befa6ac
- scene: `履约场景-配送问题`
- last_user_query: 没了，谢谢
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 4. 7ddac8a8439551926ee7df2026187cb03835bc61
- scene: `履约场景-配送问题`
- last_user_query: 好的
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-ACK`
- rationale: 当前只是弱确认/应答，且没有 pending strong solution，不触发动作。
- 训练师选择: A / B / C / D

## 5. 05dc899bee1a1341004062d11c651a6d43ff9f2a
- scene: `履约场景-配送问题`
- last_user_query: 那现在怎么办
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 6. 5d6060e50e8d3426252edd4cc5e8fb1e7fd40d91
- scene: `履约场景-配送问题`
- last_user_query: 我弄一下
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 7. 224a30964d3eeef2c2776cf287633ae5b69004a5
- scene: `履约场景-配送问题`
- last_user_query: 没有，就这样吧
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 8. ae0b1d9c65634dd465d30394a0ace5c1bda8e996
- scene: `履约场景-配送问题`
- last_user_query: 没了
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 9. b7d6bfcd79d2646f272d97b356b7022261e375ce
- scene: `履约场景-配送问题`
- last_user_query: 嗯嗯
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-ACK`
- rationale: 当前只是弱确认/应答，且没有 pending strong solution，不触发动作。
- 训练师选择: A / B / C / D

## 10. 1b3bc3f792b0e4ce9735d25e4298f207892e7618
- scene: `履约场景-配送问题`
- last_user_query: 我的订单什么情况
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 11. aba201bd7c059a6bb1787a19b37b43dfb2038b9d
- scene: `履约场景-配送问题`
- last_user_query: 希望以后不要这么慢了
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 12. 037cd0d5624882cde9ecb940a921a3f032b4bfe2
- scene: `履约场景-配送问题`
- last_user_query: OK
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-ACK`
- rationale: 当前只是弱确认/应答，且没有 pending strong solution，不触发动作。
- 训练师选择: A / B / C / D

## 13. 4340b4a84defb462766100b2e20ef399c7acb50b
- scene: `履约场景-配送问题`
- last_user_query: 没了吧
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 14. 6704ad57a2f78e05f033fba3827c906d569dfbc3
- scene: `履约场景-配送问题`
- last_user_query: 嗯
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-ACK`
- rationale: 当前只是弱确认/应答，且没有 pending strong solution，不触发动作。
- 训练师选择: A / B / C / D

## 15. 7c1f0ff0efe3e21a91e1e9bf7d7b375c521b1d51
- scene: `履约场景-配送问题`
- last_user_query: 没有
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 16. 25c44061874a2a2999766ec8b3f1a0cff2410774
- scene: `履约场景-配送问题`
- last_user_query: 你们这个骑手什么鬼  一直找不到地方
- current_turn_intent: `['select_product']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 17. 2343c3b371e7aeba92204c487de4b3ab894baddb
- scene: `履约场景-配送问题`
- last_user_query: 快啊快啊
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-OTHER`
- rationale: 未命中 v21 配送动作规则；当前轮 gating 阻止历史关键词误触发。
- 训练师选择: A / B / C / D

## 18. 43fed2f2ef4e39e731c3b1e44eb4a0ccc73b6594
- scene: `履约场景-配送问题`
- last_user_query: 人工客服
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLARIFY_OR_TRANSFER`
- rationale: 当前只请求人工/客服且无具体诉求，ResponseSolution=无。
- 训练师选择: A / B / C / D

## 19. 0dc7d5034ff214eaecc008fc8af623c652e99f4b
- scene: `履约场景-配送问题`
- last_user_query: 人工
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLARIFY_OR_TRANSFER`
- rationale: 当前只请求人工/客服且无具体诉求，ResponseSolution=无。
- 训练师选择: A / B / C / D

## 20. 928925781ec7bc08a7ef55dbb3924d5cec4ac873
- scene: `履约场景-配送问题`
- last_user_query: 没事了，我找骑手说就行
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 21. a8bf4ef94a426e262e93c2c7b370922ed1387d2e
- scene: `履约场景-配送问题`
- last_user_query: 他怎么这么慢，催促配送
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 22. 622b407c2ed5e6feec6c58a040a3b15fbb24ce1b
- scene: `履约场景-配送问题`
- last_user_query: 我的意思是能不能快点啊，等很久了啊
- current_turn_intent: `['delivery_urge']`
- gold ResponseSolution: `系统催单`
- oracle ResponseSolution: `系统催单`
- oracle rule: `FD-03`
- rationale: 当前催配送，或 ETA 咨询且有超时/风险，系统催单 eligible。
- 训练师选择: A / B / C / D

## 23. 77e3661b29b37844598c3cf7f44b23d8b96490ff
- scene: `履约场景-配送问题`
- last_user_query: 没了
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史触发新动作。
- 训练师选择: A / B / C / D

## 24. b893cf5771deb5c9e95f889cfca66af03ce8df78
- scene: `履约场景-配送问题`
- last_user_query: 嗯
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `FD-ACK`
- rationale: 当前只是弱确认/应答，且没有 pending strong solution，不触发动作。
- 训练师选择: A / B / C / D

## 25. a84ba555253ba5833ef7dc92e78d546c3aa57d52
- scene: `收货场景-品质问题`
- last_user_query: 谢谢
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史或状态触发新退款/赔付/催审。
- 训练师选择: A / B / C / D

## 26. 9802aa393ac53581df475e399e90bac207b11c3f
- scene: `收货场景-品质问题`
- last_user_query: 好的，知道了
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-OTHER`
- rationale: 未命中 v21 品质动作规则；current-turn gating 阻止状态或历史误触发。
- 训练师选择: A / B / C / D

## 27. 00f2860ed5674bd45a33fc01da3997f5da82d293
- scene: `收货场景-品质问题`
- last_user_query: 人工
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-CLARIFY_OR_TRANSFER`
- rationale: 当前只请求人工/客服且无具体诉求，ResponseSolution=无。
- 训练师选择: A / B / C / D

## 28. 6abb581729866370710397ec2ad603970953f433
- scene: `收货场景-品质问题`
- last_user_query: 人工
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-CLARIFY_OR_TRANSFER`
- rationale: 当前只请求人工/客服且无具体诉求，ResponseSolution=无。
- 训练师选择: A / B / C / D

## 29. 78dbe3e798b111da3c6f6bd3a6e073929524fd9e
- scene: `收货场景-品质问题`
- last_user_query: 商品有质量问题
- current_turn_intent: `['quality_issue']`
- gold ResponseSolution: `选择商品`
- oracle ResponseSolution: `选择商品`
- oracle rule: `RQ-02`
- rationale: 当前品质/退款诉求仍在推进且未选商品，先选择商品。
- 训练师选择: A / B / C / D

## 30. e63e27d9b2d2379000d58c3ca5c92709eb8d19d4
- scene: `收货场景-品质问题`
- last_user_query: 没有了，谢谢
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史或状态触发新退款/赔付/催审。
- 训练师选择: A / B / C / D

## 31. 6c5756ef558d7ec389403fe85365c8c9b0ad3a6b
- scene: `收货场景-品质问题`
- last_user_query: 没有了
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史或状态触发新退款/赔付/催审。
- 训练师选择: A / B / C / D

## 32. 81b943e614de1bb8f407229ceadcd2e090156684
- scene: `收货场景-品质问题`
- last_user_query: 没有了
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史或状态触发新退款/赔付/催审。
- 训练师选择: A / B / C / D

## 33. 69b92a405834cf3b9eb8149654a44aedd4a0456d
- scene: `收货场景-品质问题`
- last_user_query: 嗯嗯，谢谢
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史或状态触发新退款/赔付/催审。
- 训练师选择: A / B / C / D

## 34. 756fc5a447b8bc29dbf1f6c07edb4b8a18cee3c9
- scene: `收货场景-品质问题`
- last_user_query: 主要是这一批次都是软的呀
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-OTHER`
- rationale: 未命中 v21 品质动作规则；current-turn gating 阻止状态或历史误触发。
- 训练师选择: A / B / C / D

## 35. 5acee55c660d17570be9f5771eb05ea2dd89c7e9
- scene: `收货场景-品质问题`
- last_user_query: 没有
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-OTHER`
- rationale: 未命中 v21 品质动作规则；current-turn gating 阻止状态或历史误触发。
- 训练师选择: A / B / C / D

## 36. 211a06bc869d71128a43b79cb41ed591309699ac
- scene: `收货场景-品质问题`
- last_user_query: 没了，就这个问题
- current_turn_intent: `['select_product']`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-CLOSE`
- rationale: 当前最后一条用户消息是感谢/结束语，不从历史或状态触发新退款/赔付/催审。
- 训练师选择: A / B / C / D

## 37. 4f8dca6a83e9247abfda712f8db77ec40a0a8b63
- scene: `收货场景-品质问题`
- last_user_query: 行
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-ACK`
- rationale: 当前只是弱确认/应答，且没有 pending strong solution，不触发动作。
- 训练师选择: A / B / C / D

## 38. ec403eeaaf7165418ea83e9911b631727b41ef07
- scene: `收货场景-品质问题`
- last_user_query: 一定要这么抠吗
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-OTHER`
- rationale: 未命中 v21 品质动作规则；current-turn gating 阻止状态或历史误触发。
- 训练师选择: A / B / C / D

## 39. 3be9f9affd78ed9449e8bffc9e9cf1602791203b
- scene: `收货场景-品质问题`
- last_user_query: 钱什么时候能退啊
- current_turn_intent: `[]`
- gold ResponseSolution: `无`
- oracle ResponseSolution: `无`
- oracle rule: `RQ-OTHER`
- rationale: 未命中 v21 品质动作规则；current-turn gating 阻止状态或历史误触发。
- 训练师选择: A / B / C / D

## 40. 1073928bbf1daded4ab6784dac05238c09324d73
- scene: `收货场景-品质问题`
- last_user_query: 万一打开都坏了呢，给我都退了
- current_turn_intent: `['quality_issue']`
- gold ResponseSolution: `小象单商品退款-100%`
- oracle ResponseSolution: `小象单商品退款-100%`
- oracle rule: `RQ-08`
- rationale: 当前仍有退款/品质诉求且前置满足；提出退款，未确认前 DialogueAgreeSolution=无。
- 训练师选择: A / B / C / D
