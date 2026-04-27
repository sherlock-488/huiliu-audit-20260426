# Replay Run v1 - Fulfillment Delivery

本目录用于正式跑履约配送 `baseline prompt` vs `skill prompt` 离线 replay。它不训练模型，不接线上，也不伪造模型输出。

## 1. 生成输入

本轮已经从 v22 replay 输入合并生成：

```bash
replay_run_v1/inputs/FD_BASELINE_INPUTS.jsonl
replay_run_v1/inputs/FD_SKILL_INPUTS.jsonl
```

合并范围是 stable + action-focused，不包含 challenge。同一个 `sample_id` 去重，保留 `set_type=stable/action`。`prompt` 字符串中不包含 gold/oracle/target 标注；metadata 保留 gold/oracle 供评估使用。

## 2. 调用模型 replay

先 dry-run 检查路径：

```bash
python3 replay_run_v1/run_model_replay.py --dry-run
```

真实调用前配置以下任一方式：

```bash
export REPLAY_MODEL_NAME="your-model"
export REPLAY_INTERNAL_COMMAND="your_command_that_reads_prompt_from_stdin"
```

然后运行：

```bash
python3 replay_run_v1/run_model_replay.py
```

输出路径：

```bash
replay_run_v1/model_outputs/FD_BASELINE_OUTPUTS.jsonl
replay_run_v1/model_outputs/FD_SKILL_OUTPUTS.jsonl
```

## 3. 模型输出格式

支持格式 A：

```json
{"sample_id":"...","Response":"...","ResponseSolution":"...","DialogueAgreeSolution":"..."}
```

支持格式 B：

```json
{"sample_id":"...","output":"{\"Response\":\"...\",\"ResponseSolution\":\"...\",\"DialogueAgreeSolution\":\"...\"}"}
```

## 4. 评估 baseline

```bash
python3 replay_run_v1/evaluate_replay_outputs_v23.py \
  --stable-oracle flow_skill_policy_v22/replay/fulfillment_delivery_stable_replay.jsonl \
  --action-oracle flow_skill_policy_v22/replay/fulfillment_delivery_action_focused_replay.jsonl \
  --challenge-oracle flow_skill_policy_v22/replay/fulfillment_delivery_challenge_replay.jsonl \
  --model-outputs replay_run_v1/model_outputs/FD_BASELINE_OUTPUTS.jsonl \
  --output replay_run_v1/eval/FD_BASELINE_eval_result.jsonl \
  --report replay_run_v1/eval/FD_BASELINE_eval_report.md \
  --label baseline
```

## 5. 评估 skill

```bash
python3 replay_run_v1/evaluate_replay_outputs_v23.py \
  --stable-oracle flow_skill_policy_v22/replay/fulfillment_delivery_stable_replay.jsonl \
  --action-oracle flow_skill_policy_v22/replay/fulfillment_delivery_action_focused_replay.jsonl \
  --challenge-oracle flow_skill_policy_v22/replay/fulfillment_delivery_challenge_replay.jsonl \
  --model-outputs replay_run_v1/model_outputs/FD_SKILL_OUTPUTS.jsonl \
  --output replay_run_v1/eval/FD_SKILL_eval_result.jsonl \
  --report replay_run_v1/eval/FD_SKILL_eval_report.md \
  --label skill
```

## 6. 比较 baseline vs skill

```bash
python3 replay_run_v1/compare_baseline_skill.py \
  --baseline replay_run_v1/eval/FD_BASELINE_eval_result.jsonl \
  --skill replay_run_v1/eval/FD_SKILL_eval_result.jsonl \
  --output replay_run_v1/eval/FD_baseline_vs_skill_report.md
```

## 7. 硬 gate

- `close_ack_over_action_rate` 不得上升超过 1%。
- `strong_confirm_over_trigger_rate` 必须接近 0。
- `stable_over_action_rate` 不得明显上升。
- `action_gold_match_rate` 或 `action_oracle_match_rate` 至少一个提升。
- `action_wrong_rate` 不得明显上升。

## 8. 为什么 challenge 不进主指标

challenge 集是 gold/oracle 不一致样本，主要用于训练师校准。把它混入主指标会把“策略口径待确认”误当成模型对错，影响 baseline vs skill 的判断。
