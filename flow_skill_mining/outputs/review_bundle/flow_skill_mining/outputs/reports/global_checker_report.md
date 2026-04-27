# Global Flow Checker v0 报告

- 总样本数: `13524`
- fail 数: `98`
- warning 数: `509`

注意：这批数据是训练师 goodcase；大量 fail/warning 不应直接判定数据错，可能是 checker 规则过严、工具名兼容或 DialogueAgreeSolution 语义需确认。

## 各规则命中数
- `R1` `warning`: `40`
- `R10` `fail`: `98`
- `R11` `warning`: `51`
- `R12` `warning`: `80`
- `R2` `warning`: `88`
- `R4` `warning`: `250`

## 各 scene fail/warning 分布
- `收货场景-品质问题`: fail=`88`, warning=`137`
- `履约场景-配送问题`: fail=`0`, warning=`100`
- `收货场景-错送问题`: fail=`4`, warning=`59`
- `履约场景-修改订单问题`: fail=`0`, warning=`61`
- `<MISSING>`: fail=`0`, warning=`27`
- `会员场景-权益问题`: fail=`0`, warning=`18`
- `收货场景-少送问题`: fail=`4`, warning=`13`
- `收货场景-退款问题`: fail=`2`, warning=`14`
- `收货场景-实描不符问题`: fail=`0`, warning=`13`
- `其他场景-投诉问题`: fail=`0`, warning=`6`
- `会员场景-退卡问题`: fail=`0`, warning=`5`
- `收货场景-重量不足问题`: fail=`0`, warning=`5`
- `其他场景`: fail=`0`, warning=`5`
- `其他场景-账号问题`: fail=`0`, warning=`5`
- `会员场景-开通问题`: fail=`0`, warning=`4`
- `收货场景-退款问题诉求`: fail=`0`, warning=`3`
- `发票场景`: fail=`0`, warning=`3`
- `会员场景-续费问题`: fail=`0`, warning=`3`
- `履约场景-履约中订单缺货`: fail=`0`, warning=`3`
- `会员场景-退卡问题诉求`: fail=`0`, warning=`3`
- `会员场景-开通问题诉求`: fail=`0`, warning=`2`
- `金融场景-支付问题`: fail=`0`, warning=`2`
- `未识别`: fail=`0`, warning=`2`
- `活动场景-省钱卡问题`: fail=`0`, warning=`2`
- `收货场景-催退款进度`: fail=`0`, warning=`2`
- `活动场景-常规活动问题`: fail=`0`, warning=`2`
- `售前场景-业务咨询问题`: fail=`0`, warning=`1`
- `会员场景-退款问题`: fail=`0`, warning=`1`
- `会员问题-退卡问题`: fail=`0`, warning=`1`
- `长尾场景-金融`: fail=`0`, warning=`1`
- `收货场景-品质问题诉求`: fail=`0`, warning=`1`
- `售前场景-商品咨询问题`: fail=`0`, warning=`1`
- `其他场景-其他问题`: fail=`0`, warning=`1`
- `其他场景-其他问题诉求`: fail=`0`, warning=`1`
- `售前场景-下单问题`: fail=`0`, warning=`1`
- `会员问题-权益问题`: fail=`0`, warning=`1`

## TOP 问题样本
- `0e42491d7ae92f672c887ac98f635c10bd19920d` scene=`收货场景-退款问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `催促退款审核` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `b80305aad2cca4e21070b5d4851e1d4f4bf70ea0` scene=`收货场景-退款问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `催促退款审核` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `2ba867c287e25f9111d898bd14688ed8f671a5ff` scene=`收货场景-错送问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `dfa4317991fdc463c39697fd1d6ffecbd6b0bc17` scene=`收货场景-错送问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `99023b42ab7c93133d76a61f4e63cb5e4e732e61` scene=`收货场景-错送问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `7f705b9ef55344077cc1058ecbeb50fd28bd2644` scene=`收货场景-错送问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `52f3c5bc8345761acbdb2b20fbb6982e82ab87f1` scene=`履约场景-配送问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `4350aba07a26c1b3cb9b38a6f1829ece17b83c5d` scene=`履约场景-配送问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `67e530ee4b94160fee14778a0cf72a5ad8d86886` scene=`收货场景-退款问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `催促退款审核` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `db85174657fc59dc88e10cf54bd84ad42906a1a3` scene=`收货场景-退款问题` fail=0 warning=2 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `催促退款审核` is usually no-confirmation action'}, {'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `1a684a703b22831654d46cc6611945f29812cb9a` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `1991a915a1f930ef2277889a2612d3dfd0ad429c` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]
- `7ad982ba5f5d88a7a7c6e4605a2d3a2df22a3533` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]
- `3844c667c4f5002a549ce44773cbb2db3f2f349c` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]
- `e23b0658ef0da744678e436e75074aa8f232f770` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]
- `c36e7403243efdab050f990708deba8ef75b13ea` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]
- `24af6734016686306b294ec2b3ed6f17494d4b98` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]
- `7389506117b831032f890b56bf24d2f67ec2320a` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]
- `3fda30726dc18867f24e399bce4bac6a11fc4324` scene=`收货场景-退款问题诉求` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `催促退款审核` is usually no-confirmation action'}]
- `7caab61119d3cde93233f772e59e3f134d5641f1` scene=`收货场景-退款问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `催促退款审核` is usually no-confirmation action'}]
- `c896adecdc18cfe86520d8b6d62cd6f5deedb0cd` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `911acef1389ed325adfa16b213078510234ae4ba` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `5955b26dda852730f654cd39f94ac2a63111dc72` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `651ca40a2aa18487a3e8eaf8fbf7683b06afe21c` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `5dfb5f553f1397695d615f281e74a273dc7508a6` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `76ed9558419d898354861151ac6c6f877f0864ab` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `e88011e55166d0bdef64cea0d01d59eb022ed0ad` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `9a7edca07bee72f8de0fbeb7b6a6dd1aee3952cf` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `c6e9832c800d69191f4795401c5bed049a715f3a` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `846b5c2fbc2e480185c6bc5fcc33849a7edfb2ec` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `6179551a7ad7feecc9e14b538636af3a4e70b154` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `3780072e9352a349fbd652474bf3080705624752` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `996f61b532ff864b0fb4057bef5ea47c9a90bfd1` scene=`收货场景-错送问题` fail=0 warning=1 issues=[{'rule': 'R2', 'level': 'warning', 'message': 'DialogueAgreeSolution `外呼骑手-协商调换货品` is usually no-confirmation action'}]
- `721209b72f31893e3563385e6e731511b5f1318e` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]
- `5a006c4625bf489b979621bb895ad5904b0dab72` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R1', 'level': 'warning', 'message': 'ResponseSolution `操作赔付-优惠券-8元:智能跟单` not found in available_solutions'}]
- `69f68726ed67510dcf0e4bdae8f06343e5b4a623` scene=`收货场景-品质问题` fail=0 warning=1 issues=[{'rule': 'R11', 'level': 'warning', 'message': 'refund/compensation in quality-like scene before image evidence'}]
- `d4aa19359b1486749c8c9f533f08a7e44a7a9176` scene=`售前场景-业务咨询问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `2559bca1351488b706613922cab56de62daca196` scene=`发票场景` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `637a504022772e1e57d999bfc88868b8f461e21b` scene=`收货场景-品质问题` fail=0 warning=1 issues=[{'rule': 'R11', 'level': 'warning', 'message': 'refund/compensation in quality-like scene before image evidence'}]
- `ca03d2beb2e1bae58fba7bf8cc066100313dfa4d` scene=`收货场景-品质问题` fail=0 warning=1 issues=[{'rule': 'R11', 'level': 'warning', 'message': 'refund/compensation in quality-like scene before image evidence'}]
- `e4aa610310ff836327e7e0435b5f74296d3c4db0` scene=`收货场景-实描不符问题` fail=0 warning=1 issues=[{'rule': 'R11', 'level': 'warning', 'message': 'refund/compensation in quality-like scene before image evidence'}]
- `862e59b55d9c4934d3e33139f50340153699981a` scene=`收货场景-实描不符问题` fail=0 warning=1 issues=[{'rule': 'R11', 'level': 'warning', 'message': 'refund/compensation in quality-like scene before image evidence'}]
- `f64ad6ec692b39db546043da17f0c828d794247f` scene=`会员场景-开通问题诉求` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `16ea507a6bd384e7524b9bbc328cdd9fc8d425c1` scene=`会员场景-续费问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `0eaa738e194e9a1c63b234cc38c4dbaceb9a6c8c` scene=`会员场景-权益问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `83a061df10349367046b710cc67e908c48f15b0a` scene=`会员场景-权益问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `46fde1a66601945cd95b644d46537ba0bb4e5380` scene=`收货场景-退款问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `ba4f9044425493f14e2e9f70f0c045bb2ce460ac` scene=`会员场景-退款问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `435872fce83350bf949608ce0085c26344b58eed` scene=`会员问题-退卡问题` fail=0 warning=1 issues=[{'rule': 'R4', 'level': 'warning', 'message': 'DialogueAgreeSolution non-empty but last_user_query lacks explicit confirmation expression'}]
- `3ad4fbd71225a27dff0f3527e903dac99ec7bf5a` scene=`履约场景-配送问题` fail=0 warning=1 issues=[{'rule': 'R12', 'level': 'warning', 'message': 'ResponseSolution=无 possible missing action, reason=eta_answer_only'}]

## 可能过严、需训练师确认
- R1 工具名兼容问题可能导致 available_solutions 未命中。
- R4 用户确认表达非常口语化，不能作为 fail。
- R11 图片前置是否强制，需要按品质/日期/实描等子流程确认。
