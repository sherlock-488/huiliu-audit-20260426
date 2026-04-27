# 履约场景-配送问题 流程 Skill v1

目的：只约束流程动作，不优化话术。进入条件：问题场景为 `履约场景-配送问题`。

必读信号：是否咨询高峰期, 用户分层标签, 是否会员, 订单类型, 配送类型, 商品数量, 订单来源, 是否为配送单, 是否为自提单, 是否外卖单, 门店名称, 城市名称, 订单是否含追加单, 订单是否含加工品, 支付类型, 支付金额, 原价(促销价), 券减免金额。

动作选择规则：
- 当状态满足 {'scene': '履约场景-配送问题', 'user_intent': 'other', 'order_status': '已完成', 'rider_status': '已送达', 'timeout_state': '是', 'can_cancel': False, 'already_compensated': False, 'refund_state': '订单无退款', 'selected_sku_state': 'not_selected', 'image_state': 'unknown', 'has_rider_phone': True, 'pending_confirmation_solution': '操作赔付-优惠券-10元'} 时，优先考虑 `操作赔付-优惠券-xx元`。

确认规则：强确认方案包括 取消订单、小象单商品退款-xx%、小象整单申请退款、操作赔付-优惠券-xx元。这些方案只有在用户明确同意（可以、同意、行、好、确认、退吧、赔吧、取消吧、帮我处理等）后，DialogueAgreeSolution 才能非空。催促退款审核、再次外呼骑手-xx、外呼骑手-xx 属于用户诉求即授权，ResponseSolution 可以直接执行，DialogueAgreeSolution 可为空。

无需确认方案：加急调度、发送送达图片、引导自助修改订单、引导自助联系骑手、智能跟单、管理会员自动续费、系统催单、选择商品。

ResponseSolution=无 的合理原因：close_conversation(537)；explain_refund_status(332)；explain_status(143)；unknown(133)；ask_user_problem(102)；eta_answer_only(90)；after_action_followup(33)；unavailable_capability(16)。如果用户诉求明确且已有可执行方案，不要随意输出“无”。

守卫：不可赔付不得赔付；已赔付过不得再次主动赔；赔付金额不得超过信号上限；不可取消不得取消；未选商品不得单商品退款；质量类未有图片时优先引导上传；不得输出候选方案外的工具，除非命中 alias。

