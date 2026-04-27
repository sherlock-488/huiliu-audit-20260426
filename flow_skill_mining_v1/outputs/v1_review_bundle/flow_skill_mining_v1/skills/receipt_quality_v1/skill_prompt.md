# 收货场景-品质问题 流程 Skill v1

目的：只约束流程动作，不优化话术。进入条件：问题场景为 `收货场景-品质问题`。

必读信号：是否咨询高峰期, 用户分层标签, 是否会员, 订单状态, 订单类型, 配送类型, 商品数量, 订单来源, 是否为配送单, 是否为自提单, 是否外卖单, 门店名称, 城市名称, 订单是否超售后, 订单是否含追加单, 订单是否含加工品, 支付类型, 支付金额。

动作选择规则：
- 当状态满足 {'scene': '收货场景-品质问题', 'user_intent': 'confirm_compensation', 'order_status': '已完成', 'rider_status': '已送达', 'timeout_state': '否', 'can_cancel': False, 'already_compensated': False, 'refund_state': '订单无退款', 'selected_sku_state': 'selected', 'image_state': 'has_image', 'has_rider_phone': True, 'pending_confirmation_solution': '小象单商品退款-100%'} 时，优先考虑 `小象单商品退款-xx%`。
- 当状态满足 {'scene': '收货场景-品质问题', 'user_intent': 'confirm_compensation', 'order_status': '已完成', 'rider_status': '已送达', 'timeout_state': '否', 'can_cancel': False, 'already_compensated': False, 'refund_state': '未知状态', 'selected_sku_state': 'selected', 'image_state': 'has_image', 'has_rider_phone': True, 'pending_confirmation_solution': '小象单商品退款-100%'} 时，优先考虑 `小象单商品退款-xx%`。
- 当状态满足 {'scene': '收货场景-品质问题', 'user_intent': 'confirm_compensation', 'order_status': '已完成', 'rider_status': '已送达', 'timeout_state': '否', 'can_cancel': False, 'already_compensated': False, 'refund_state': '订单无退款', 'selected_sku_state': 'selected',
