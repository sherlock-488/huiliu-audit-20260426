【收货品质流程规则 v2】
适用：问题场景为“收货场景-品质问题”，仅用于离线 replay 校准，重点约束流程前置。
1. 先读信号：订单/商品是否超售后、已选择商品、商品退款状态、是否已收集图片凭证、退款原因、建议退款比例、实际退款数量、退款状态、是否可赔付、是否已赔付、赔付金额。
2. 超售后或商品不可退款时，不得选择小象单商品退款；ResponseSolution=无，解释不可退/政策原因，也不要错误引导重新选择商品。
3. 品质、日期、口感、实描等质量问题未选具体商品时，ResponseSolution=选择商品，DialogueAgreeSolution=无。
4. 已选商品但缺图片凭证时，ResponseSolution=无，no_action_reason=ask_upload_image；不得直接退款或赔付。
5. 已选商品且有图片，但缺退款原因，ResponseSolution=无，追问退款原因；缺建议退款比例时，ResponseSolution=无，追问/确认退款比例。
6. 多数量商品缺退款数量时，ResponseSolution=无，追问退款数量，不得默认数量。
7. 前置满足后，可提出小象单商品退款-xx%；用户尚未确认比例/金额时 DialogueAgreeSolution=无，用户明确同意后才填对应退款方案。
8. 退款进行中/审核中且用户问进度，首次可 ResponseSolution=催促退款审核;退审跟单，持续催促可用加急催促退款审核；不要求 DialogueAgreeSolution。
9. 已退款/退款完成时 ResponseSolution=无，只解释退款状态。
10. 用户要求赔付或强烈不满，且可赔、未赔、金额不超过上限时才可提出操作赔付-优惠券-xx元；用户明确同意后 DialogueAgreeSolution 才非空。已赔或不可赔禁止赔付。
