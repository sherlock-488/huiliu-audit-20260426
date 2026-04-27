# Input Build Report

## Counts
- baseline_main_count: `121`
- skill_main_count: `121`
- gold_guided_main_count: `121`
- challenge_baseline_count: `45`
- challenge_skill_count: `45`
- challenge_gold_guided_count: `45`
- stable/action/challenge_distribution: `{'stable': 76, 'action': 45, 'challenge': 45}`

## ResponseSolution Distribution (main baseline)
- `无`: `64`
- `操作赔付-优惠券-10元`: `11`
- `智能跟单`: `7`
- `系统催单`: `7`
- `操作赔付-优惠券-8元`: `6`
- `外呼骑手-催促配送`: `6`
- `引导自助联系骑手`: `4`
- `再次外呼骑手-催促配送`: `3`
- `取消订单`: `2`
- `操作赔付-优惠券-15元`: `2`
- `外呼骑手-协商调换货品`: `2`
- `小象整单申请退款`: `2`
- `小象单商品退款-100%`: `2`
- `操作赔付-优惠券-15元;智能跟单`: `1`
- `再次外呼骑手-协商调换货品`: `1`
- `选择商品`: `1`

## DialogueAgreeSolution
- main_gold_dialogue_agree_non_empty: `12`
- main_oracle_dialogue_agree_non_empty: `6`

## Prompt Leakage
- baseline_prompt_has_gold_or_oracle: `0`
- skill_prompt_has_gold_or_oracle: `0`
- gold_guided_prompt_has_gold_or_oracle: `121`
- Note: gold-guided leaks are expected by design; baseline/skill should be 0.

## Prompt Length
- baseline_avg_prompt_len: `4576`
- skill_avg_prompt_len: `5261`
- gold_guided_avg_prompt_len: `5592`
- skill_prompt_inserted_success_count: `121`

## Gold-Guided Base Choice
- Gold-guided prompts use the skill-prompt variant as base, then append the reference-label block. They are upper-bound prompts, not formal effect metrics.
