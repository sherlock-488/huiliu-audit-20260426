# Replay Run Effect v1

本轮实验只验证履约配送流程 skill 对 `ResponseSolution` / `DialogueAgreeSolution` 的影响，不训练模型、不接线上，不把收货品质纳入正式结论。

## 三组输入

- `baseline`: 使用原始 prompt，不插入流程 skill。用于衡量主模型原始能力。
- `skill`: 在原始 prompt 中插入 `fulfillment_delivery_policy_v22/skill_prompt.md`。用于衡量流程 skill 是否提升动作选择。
- `gold-guided upper-bound`: 在 skill prompt 基础上追加“流程参考标签”，把 gold/oracle 方案放进 prompt。它不是正式效果指标，只用于判断“答案已知时模型是否能稳定输出方案字段”。

challenge 集单独保留，只做训练师校准，不混入主指标。

## 生成输入

```bash
python3 replay_run_effect_v1/scripts/build_fd_replay_inputs.py
```

输出：

```text
replay_run_effect_v1/inputs/FD_BASELINE_INPUTS.jsonl
replay_run_effect_v1/inputs/FD_SKILL_INPUTS.jsonl
replay_run_effect_v1/inputs/FD_GOLD_GUIDED_INPUTS.jsonl
replay_run_effect_v1/inputs/FD_CHALLENGE_BASELINE_INPUTS.jsonl
replay_run_effect_v1/inputs/FD_CHALLENGE_SKILL_INPUTS.jsonl
replay_run_effect_v1/inputs/FD_CHALLENGE_GOLD_GUIDED_INPUTS.jsonl
```

baseline / skill 的 prompt 字符串不包含 gold/oracle/target 标注。gold-guided 的 prompt 会包含参考标签，这是 upper-bound 设计。

## Dry-Run

```bash
python3 replay_run_effect_v1/scripts/run_fd_model_replay.py \
  --input replay_run_effect_v1/inputs/FD_BASELINE_INPUTS.jsonl \
  --output replay_run_effect_v1/model_outputs/FD_BASELINE_OUTPUTS.jsonl \
  --mode baseline \
  --dry-run
```

## Smoke Test

配置内部模型命令后，先跑 5 条：

```bash
export REPLAY_INTERNAL_COMMAND='your command reading prompt from stdin'

python3 replay_run_effect_v1/scripts/run_fd_model_replay.py \
  --input replay_run_effect_v1/inputs/FD_SKILL_INPUTS.jsonl \
  --output replay_run_effect_v1/model_outputs/FD_SKILL_OUTPUTS.jsonl \
  --mode skill \
  --limit 5
```

## 全量运行

```bash
python3 replay_run_effect_v1/scripts/run_fd_model_replay.py \
  --input replay_run_effect_v1/inputs/FD_BASELINE_INPUTS.jsonl \
  --output replay_run_effect_v1/model_outputs/FD_BASELINE_OUTPUTS.jsonl \
  --mode baseline

python3 replay_run_effect_v1/scripts/run_fd_model_replay.py \
  --input replay_run_effect_v1/inputs/FD_SKILL_INPUTS.jsonl \
  --output replay_run_effect_v1/model_outputs/FD_SKILL_OUTPUTS.jsonl \
  --mode skill

python3 replay_run_effect_v1/scripts/run_fd_model_replay.py \
  --input replay_run_effect_v1/inputs/FD_GOLD_GUIDED_INPUTS.jsonl \
  --output replay_run_effect_v1/model_outputs/FD_GOLD_GUIDED_OUTPUTS.jsonl \
  --mode gold_guided
```

## 评估单组

```bash
python3 replay_run_effect_v1/scripts/evaluate_fd_replay.py \
  --model-outputs replay_run_effect_v1/model_outputs/FD_SKILL_OUTPUTS.jsonl \
  --output replay_run_effect_v1/eval/FD_SKILL_eval_result.jsonl \
  --report replay_run_effect_v1/eval/FD_SKILL_eval_report.md \
  --label skill
```

## 对比三组

```bash
python3 replay_run_effect_v1/scripts/compare_fd_replay.py \
  --baseline-result replay_run_effect_v1/eval/FD_BASELINE_eval_result.jsonl \
  --skill-result replay_run_effect_v1/eval/FD_SKILL_eval_result.jsonl \
  --gold-guided-result replay_run_effect_v1/eval/FD_GOLD_GUIDED_eval_result.jsonl \
  --output replay_run_effect_v1/eval/FD_compare_report.md
```

## 判断 Skill 是否有效

重点看：

- `stable_no_action_precision` 是否下降。
- `stable_over_action_rate` 是否上升。
- `action_gold_canonical_match_rate` 是否上升。
- `action_oracle_canonical_match_rate` 是否上升。
- `action_missing_gold_rate` 是否下降。
- `action_wrong_rate` 是否上升。
- `global_strong_confirm_over_trigger_rate` 是否上升。
- `close_ack_over_action_rate` 是否上升。

## Gold-Guided 解释

如果 gold-guided 仍无法匹配 gold，说明主模型格式遵循或方案字段输出能力有问题。如果 gold-guided 很高而 skill 不高，说明 skill policy 信息不足或模型没有从 skill 中推断动作。如果 skill 接近 gold-guided，说明 skill prompt 对流程动作有效。

## 为什么只跑履约配送

履约配送 v22 已通过 current-turn gating 审阅，close/ack/transfer 误触发为 0，并且 action-focused replay 已准备好。收货品质仍需训练师校准前置 guard 和退款比例/图片证据口径，所以本轮不作为正式实验结论。
