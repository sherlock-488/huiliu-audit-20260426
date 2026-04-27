# Current Turn Intent v22 Report

## Dry Run
- `怎么还没配送` -> `['eta_question']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:eta_question']`
- `急` -> `['delivery_urge']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:delivery_urge']`
- `还得等到啥时候啊` -> `['eta_question']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:eta_question']`
- `我要求加急并没有加急啊，我很着急啊` -> `['delivery_urge']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:delivery_urge']`
- `5分钟？` -> `['eta_question']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:eta_question']`
- `好，快点` -> `['delivery_urge']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:delivery_urge']`
- `洗衣液今天打开看都是漏的` -> `['quality_issue']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:quality_issue']`
- `芹菜空心的` -> `['quality_issue']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:quality_issue']`
- `这个蛋送来打开后是碎的` -> `['quality_issue', 'select_product']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:quality_issue', 'intent:select_product']`
- `坏得有一半了` -> `['quality_issue']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:quality_issue']`
- `都不能吃了就给这么少吗` -> `['compensation_request', 'quality_issue']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:compensation_request', 'intent:quality_issue']`
- `臭的` -> `['quality_issue']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:quality_issue']`
- `干瘪` -> `['quality_issue']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:quality_issue']`
- `嗯，什么时候退完给我啊` -> `['refund_progress']` pure_confirm=`False` maybe_accept=`False` debug=`['intent:refund_progress']`
- `行吧，那就这样吧` -> `[]` pure_confirm=`True` maybe_accept=`True` debug=`['confirm_like', 'pure_confirm']`
- `好谢谢` -> `[]` pure_confirm=`False` maybe_accept=`False` debug=`['close_or_thanks']`
- `可以，那退吧` -> `['confirm_refund']` pure_confirm=`True` maybe_accept=`False` debug=`['confirm_like', 'pure_confirm']`

## v21/v22 Intent Changed On v21 Challenge
- `fulfillment_delivery_challenge_replay`: `13`
- `receipt_quality_challenge_replay`: `17`

## Examples
- `投诉骑手`: `['compensation_request']` -> `['rider_complaint']` debug=`['intent:rider_complaint', 'rider_complaint_not_compensation']`
- `怎么还没送到`: `['delivery_urge']` -> `['eta_question', 'delivery_urge']` debug=`['intent:eta_question', 'intent:delivery_urge']`
- `啥时候送达啊，问骑手了吗`: `['contact_rider']` -> `['eta_question', 'contact_rider']` debug=`['intent:eta_question', 'intent:contact_rider']`
- `怎么还没配送`: `[]` -> `['eta_question']` debug=`['intent:eta_question']`
- `5分钟？`: `[]` -> `['eta_question']` debug=`['intent:eta_question']`
- `我知道是17:57到，问题是我要求加急并没有加急啊，我很着急啊`: `[]` -> `['delivery_urge']` debug=`['intent:delivery_urge']`
- `急`: `[]` -> `['delivery_urge']` debug=`['intent:delivery_urge']`
- `还得等到啥时候啊`: `[]` -> `['eta_question']` debug=`['intent:eta_question']`
- `很着急`: `[]` -> `['delivery_urge']` debug=`['intent:delivery_urge']`
- `太少了吧`: `[]` -> `['compensation_request']` debug=`['intent:compensation_request']`
- `太少了`: `[]` -> `['compensation_request']` debug=`['intent:compensation_request']`
- `怎么还要这么久，给我退了吧，我有事出门`: `['confirm_refund']` -> `['refund_request', 'confirm_refund']` debug=`['intent:refund_request', 'confirm_like', 'confirm_blocked_by_question_or_reject']`
- `已经好几个小时了，退款吧`: `['refund_request', 'confirm_refund']` -> `['refund_request']` debug=`['intent:refund_request']`
- `洗衣液今天打开看都是漏的`: `[]` -> `['quality_issue']` debug=`['intent:quality_issue']`
- `这个蛋送来打开后是碎的`: `['select_product']` -> `['quality_issue', 'select_product']` debug=`['intent:quality_issue', 'intent:select_product']`
- `芹菜空心的`: `[]` -> `['quality_issue']` debug=`['intent:quality_issue']`
- `等等，不是，你这个是品质问题，坏得有一半了，至少要退50%`: `['select_product']` -> `['refund_request', 'quality_issue', 'select_product']` debug=`['intent:refund_request', 'intent:quality_issue', 'intent:select_product']`
- `嗯，什么时候退完给我啊`: `['refund_progress', 'confirm_refund']` -> `['refund_progress']` debug=`['intent:refund_progress']`
- `都不能吃了就给这么少吗`: `[]` -> `['compensation_request', 'quality_issue']` debug=`['intent:compensation_request', 'intent:quality_issue']`
- `我还用调料腌过 还是臭的，我要退款`: `['refund_request']` -> `['refund_request', 'quality_issue']` debug=`['intent:refund_request', 'intent:quality_issue']`
- `【图片】 ->系统识别图片结果:车厘子柄发黑，部分柄已经散落在袋子里`: `['upload_image']` -> `['quality_issue', 'upload_image']` debug=`['intent:quality_issue', 'intent:upload_image']`
- `【图片】 ->系统识别图片结果:用户发了车厘子的图片，部分存在颜色发深发软的情况，与用户反馈的水分不足、发软相符`: `['upload_image']` -> `['quality_issue', 'upload_image']` debug=`['intent:quality_issue', 'intent:upload_image']`
- `【图片】 ->系统识别图片结果:用户上传的图片显示螃蟹无活力，疑似死亡`: `['upload_image']` -> `['quality_issue', 'upload_image']` debug=`['intent:quality_issue', 'intent:upload_image']`
- `这个都没法吃啊，你退我一半钱`: `['select_product']` -> `['quality_issue', 'select_product']` debug=`['intent:quality_issue', 'intent:select_product']`
- `这也太少了吧`: `[]` -> `['compensation_request']` debug=`['intent:compensation_request']`
- `要这么久吗`: `[]` -> `['refund_progress']` debug=`['intent:refund_progress']`
- `退款呢？多久到，能不能快点`: `['eta_question', 'delivery_urge', 'refund_request']` -> `['eta_question', 'delivery_urge', 'refund_progress', 'refund_request']` debug=`['intent:eta_question', 'intent:delivery_urge', 'intent:refund_progress', 'intent:refund_request']`
- `10%太少了点`: `[]` -> `['compensation_request']` debug=`['intent:compensation_request']`
- `太少了吧`: `[]` -> `['compensation_request']` debug=`['intent:compensation_request']`
- `不是还没送到吗`: `['delivery_urge']` -> `['eta_question', 'delivery_urge']` debug=`['intent:eta_question', 'intent:delivery_urge']`
