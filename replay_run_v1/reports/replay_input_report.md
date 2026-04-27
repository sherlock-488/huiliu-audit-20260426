# Replay Input Report

## Required Files
- `flow_skill_policy_v22/replay/fulfillment_delivery_stable_baseline_inputs.jsonl`: exists
- `flow_skill_policy_v22/replay/fulfillment_delivery_stable_skill_inputs.jsonl`: exists
- `flow_skill_policy_v22/replay/fulfillment_delivery_action_baseline_inputs.jsonl`: exists
- `flow_skill_policy_v22/replay/fulfillment_delivery_action_skill_inputs.jsonl`: exists

## Counts
- baseline_input_count: `121`
- skill_input_count: `121`
- baseline_stable/action: `76` / `45`
- skill_stable/action: `76` / `45`
- baseline_prompt_avg_len: `4576`
- skill_prompt_avg_len: `5261`
- skill_prompt_inserted_rows: `121`

## Prompt Leakage Check
- baseline_leak_rows: `0`
- skill_leak_rows: `0`
- Note: ResponseSolution / DialogueAgreeSolution in output-format instructions is expected and not counted as leakage.
- No prompt leakage markers found.
