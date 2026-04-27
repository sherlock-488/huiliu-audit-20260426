# receipt_quality_v1 checker rules

- ResponseSolution 必须命中 available_solutions 或 registry alias。
- strong_confirmation_required 方案的 DialogueAgreeSolution 必须有用户确认表达，并匹配近 3 轮 ResponseSolution。
- user_request_is_enough 方案不要求 DialogueAgreeSolution 非空。
- 不可赔付/不可取消/已赔付过等 guard 失败时标 fail 或 warning。
- 单商品退款必须先识别有效商品选择。
- 品质类退款/赔付缺图片时先 warning，待训练师确认是否升级为 fail。
- ResponseSolution=无 必须能落到 no_action_reason，否则进入漏操作候选。
