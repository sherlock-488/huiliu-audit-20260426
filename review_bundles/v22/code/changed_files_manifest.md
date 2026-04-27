# Changed Files Manifest

| file | purpose | parser | eligibility | checker | replay | skill_prompt |
|---|---|---:|---:|---:|---:|---:|
| `flow_skill_policy_v22/README_REPORT.md` | v22 audit/report output | False | False | False | False | False |
| `flow_skill_policy_v22/__init__.py` | v22 support script | False | False | False | False | False |
| `flow_skill_policy_v22/build_readme_report.py` | v22 support script | False | False | False | False | False |
| `flow_skill_policy_v22/common.py` | v22 support script | False | False | False | False | False |
| `flow_skill_policy_v22/generate_skill_packs.py` | v22 support script | False | False | False | False | False |
| `flow_skill_policy_v22/outputs/eligibility_results_v22.jsonl` | large eligibility result output | False | True | False | False | False |
| `flow_skill_policy_v22/outputs/reports/confirmation_resolver_v22_report.md` | v22 audit/report output | False | False | False | False | False |
| `flow_skill_policy_v22/outputs/reports/current_turn_intent_v22_report.md` | v22 audit/report output | True | False | False | False | False |
| `flow_skill_policy_v22/outputs/reports/eligibility_engine_v22_report.md` | v22 audit/report output | False | True | False | False | False |
| `flow_skill_policy_v22/outputs/reports/fulfillment_delivery_policy_v22_report.md` | v22 audit/report output | False | False | False | False | False |
| `flow_skill_policy_v22/outputs/reports/policy_oracle_v22_report.md` | v22 audit/report output | False | False | False | True | False |
| `flow_skill_policy_v22/outputs/reports/receipt_quality_policy_v22_report.md` | v22 audit/report output | False | False | False | False | False |
| `flow_skill_policy_v22/outputs/reports/replay_prompt_v22_report.md` | v22 audit/report output | False | False | False | False | False |
| `flow_skill_policy_v22/outputs/reports/replay_sets_v22_report.md` | v22 audit/report output | False | False | False | False | False |
| `flow_skill_policy_v22/policies/__init__.py` | v22 policy logic | False | False | False | False | False |
| `flow_skill_policy_v22/policies/confirmation_resolver.py` | v22 policy logic | False | False | False | False | False |
| `flow_skill_policy_v22/policies/current_turn_intent.py` | v22 policy logic | True | False | False | False | False |
| `flow_skill_policy_v22/policies/fulfillment_delivery_policy.py` | v22 policy logic | False | False | False | False | False |
| `flow_skill_policy_v22/policies/receipt_quality_policy.py` | v22 policy logic | False | False | False | False | False |
| `flow_skill_policy_v22/policies/safe_context_bridge.py` | v22 policy logic | False | False | False | False | False |
| `flow_skill_policy_v22/policies/signal_normalizer.py` | v22 policy logic | True | False | False | False | False |
| `flow_skill_policy_v22/policies/solution_eligibility.py` | v22 policy logic | False | True | False | False | False |
| `flow_skill_policy_v22/replay/__init__.py` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/build_policy_oracle_labels.py` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/build_replay_prompts_v22.py` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/build_replay_sets.py` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/evaluate_replay_outputs_v22.py` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_action_baseline_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_action_focused_replay.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_action_skill_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_challenge_baseline_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_challenge_replay.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_challenge_skill_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_oracle_v22.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_stable_baseline_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_stable_replay.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/fulfillment_delivery_stable_skill_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_action_baseline_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_action_focused_replay.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_action_skill_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_challenge_baseline_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_challenge_replay.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_challenge_skill_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_oracle_v22.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_stable_baseline_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_stable_replay.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/receipt_quality_stable_skill_inputs.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/replay_eval_report_v22.md` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/replay/replay_eval_result_v22.jsonl` | v22 oracle/replay/evaluator artifact | False | False | False | True | False |
| `flow_skill_policy_v22/skills/fulfillment_delivery_policy_v22/README.md` | v22 replay-ready skill pack | False | False | False | False | True |
| `flow_skill_policy_v22/skills/fulfillment_delivery_policy_v22/checker_rules.md` | v22 replay-ready skill pack | False | False | True | False | True |
| `flow_skill_policy_v22/skills/fulfillment_delivery_policy_v22/eval_cases.jsonl` | v22 replay-ready skill pack | False | False | False | False | True |
| `flow_skill_policy_v22/skills/fulfillment_delivery_policy_v22/skill.json` | v22 replay-ready skill pack | False | False | False | False | True |
| `flow_skill_policy_v22/skills/fulfillment_delivery_policy_v22/skill_prompt.md` | v22 replay-ready skill pack | False | False | False | False | True |
| `flow_skill_policy_v22/skills/receipt_quality_policy_v22/README.md` | v22 replay-ready skill pack | False | False | False | False | True |
| `flow_skill_policy_v22/skills/receipt_quality_policy_v22/checker_rules.md` | v22 replay-ready skill pack | False | False | True | False | True |
| `flow_skill_policy_v22/skills/receipt_quality_policy_v22/eval_cases.jsonl` | v22 replay-ready skill pack | False | False | False | False | True |
| `flow_skill_policy_v22/skills/receipt_quality_policy_v22/skill.json` | v22 replay-ready skill pack | False | False | False | False | True |
| `flow_skill_policy_v22/skills/receipt_quality_policy_v22/skill_prompt.md` | v22 replay-ready skill pack | False | False | False | False | True |
