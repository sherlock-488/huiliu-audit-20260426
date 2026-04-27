# Checker Rules

- strong confirmation 方案在 DialogueAgreeSolution 非空时必须有用户明确确认。
- 不可取消/不可赔/已赔付/金额超上限直接拦截。
- 品质场景未选商品、缺图片、缺原因、缺比例、缺数量时不得直接退款。
- 配送场景 ETA 普通咨询不得被误判为必须催单；无骑手接单场景优先加急调度。
