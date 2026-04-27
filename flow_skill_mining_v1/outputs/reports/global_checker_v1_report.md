# Global Flow Checker v1 报告

- 总样本数: `13524`
- v0 fail/warning: `98` / `509`
- v1 fail/warning: `24` / `355`
- R10 fail: `24`
- 履约配送 R12 候选: `158`
- 收货品质 R10/R11 候选: `30`

## 各规则命中
- `R10` `fail`: `24`
- `R11` `warning`: `11`
- `R12` `warning`: `159`
- `R4` `warning`: `185`

## 各 scene fail/warning 分布
- `履约场景-配送问题`: fail=`0`, warning=`171`
- `收货场景-品质问题`: fail=`19`, warning=`92`
- `履约场景-修改订单问题`: fail=`0`, warning=`18`
- `<MISSING>`: fail=`0`, warning=`12`
- `收货场景-错送问题`: fail=`0`, warning=`9`
- `收货场景-少送问题`: fail=`4`, warning=`5`
- `收货场景-实描不符问题`: fail=`0`, warning=`8`
- `会员场景-权益问题`: fail=`0`, warning=`5`
- `会员场景-退卡问题`: fail=`0`, warning=`5`
- `会员场景-续费问题`: fail=`0`, warning=`4`
- `收货场景-重量不足问题`: fail=`0`, warning=`4`
- `履约场景-履约中订单缺货`: fail=`0`, warning=`3`
- `会员场景-开通问题诉求`: fail=`0`, warning=`2`
- `未识别`: fail=`0`, warning=`2`
- `活动场景-省钱卡问题`: fail=`0`, warning=`2`
- `收货场景-催退款进度`: fail=`0`, warning=`2`
- `长尾场景-金融`: fail=`1`, warning=`1`
- `售前场景-业务咨询问题`: fail=`0`, warning=`1`
- `收货场景-退款问题`: fail=`0`, warning=`1`
- `会员场景-退款问题`: fail=`0`, warning=`1`
- `会员问题-退卡问题`: fail=`0`, warning=`1`
- `会员场景-开通问题`: fail=`0`, warning=`1`
- `收货场景-退款问题诉求`: fail=`0`, warning=`1`
- `收货场景-品质问题诉求`: fail=`0`, warning=`1`
- `售前场景-商品咨询问题`: fail=`0`, warning=`1`
- `其他场景`: fail=`0`, warning=`1`
- `会员场景-退卡问题诉求`: fail=`0`, warning=`1`

## 仍需训练师确认
- R11 图片前置目前只 warning，是否升级为 fail 需确认。
- user_request_is_enough 类外呼/催促方案是否允许 DialogueAgreeSolution 非空，需确认标注口径。
- R12 漏操作候选应由训练师抽样区分好 case 中合理无动作与真正漏动作。
