# README_FOR_GPT - replay_run_v1

## Git Context
- branch: `main`
- latest pushed commit before this bundle: `be131e2a65db613454a0609b62c0ba2d8c55d94e`

## 本轮目标
专注履约配送正式模型 replay：准备 baseline/skill 输入、修正 replay evaluator 指标、提供模型调用 dry-run 脚本，并生成可审阅 bundle。

## 关键判断
- fulfillment_delivery_policy_v22 可以进入正式模型 replay。
- receipt_quality_policy_v22 不作为本轮正式实验结论。
- 本轮没有模型 API / internal command 配置，因此没有伪造模型输出，也没有 baseline vs skill 指标。

## 已完成
- replay-only current-turn patch：`怎么还没配送/还没送到` 等同时识别为 `eta_question + delivery_urge`。
- 生成 FD baseline/skill 合并输入，各 121 条，stable/action 为 76/45。
- prompt 泄漏检查：0 行命中 gold/oracle/target 标注泄漏。
- 新增 v23 evaluator：action recall 不再以“非无”为准，改为 gold/oracle canonical match、missing/wrong/ineligible 分开统计。
- 新增 baseline vs skill 对比脚本和模型 replay dry-run runner。

## 请 GPT 重点审阅
1. `evaluate_replay_outputs_v23.py` 的 action-focused 指标是否足够严格。
2. `ineligible_action_rate` 使用 eligibility_results + forbidden_solutions 的逻辑是否合理。
3. `compare_baseline_skill.py` 的 gate 是否适合做小流量前置判断。
4. `FD_BASELINE_INPUTS.sample.jsonl` / `FD_SKILL_INPUTS.sample.jsonl` 是否适合直接交给模型 replay。
5. current-turn patch 是否应回灌到后续 policy v23，而不是只留在 replay_run_v1。
