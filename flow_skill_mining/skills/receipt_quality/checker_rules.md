# 收货场景-品质问题 checker rules

- 检查 ResponseSolution 是否属于该场景候选方案或 available_solutions。
- DialogueAgreeSolution 非无时，必须是确认型方案，且 last_user_query 应有明确同意表达。
- signals['订单是否可赔付']='否' 时，不允许操作赔付。
- signals['是否可取消订单']='否' 时，不允许取消订单。
- 收货类单商品退款前必须有 selected_item_info；品质/实描/日期问题建议要求图片凭证。
- ResponseSolution=无 时必须能归入 no_action_reason，否则标记为漏操作候选。
