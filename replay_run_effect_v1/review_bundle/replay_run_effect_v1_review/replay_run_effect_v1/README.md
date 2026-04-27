# Replay Run Effect v1

本目录只服务履约配送正式 replay。正式效果看 baseline vs skill；gold-guided 只做 upper-bound，不计入正式提升结论。

## 输入

```bash
python3 replay_run_effect_v1/scripts/build_fd_replay_inputs.py
```

生成：

- `inputs/FD_BASELINE_INPUTS.jsonl`
- `inputs/FD_SKILL_INPUTS.jsonl`
- `inputs/FD_GOLD_GUIDED_INPUTS.jsonl`
- `inputs/FD_CHALLENGE_BASELINE_INPUTS.jsonl`
- `inputs/FD_CHALLENGE_SKILL_INPUTS.jsonl`
- `inputs/FD_CHALLENGE_GOLD_GUIDED_INPUTS.jsonl`

baseline/skill 的 prompt 不含 gold/oracle/target 标注泄漏；gold-guided 的 prompt 会追加“流程参考标签”。

## 模型调用

先 dry-run：

```bash
python3 replay_run_effect_v1/scripts/run_model_replay.py --dry-run
```

真实运行前配置：

```bash
export REPLAY_MODEL_NAME="your-model"
export REPLAY_INTERNAL_COMMAND="your command reading prompt from stdin"
python3 replay_run_effect_v1/scripts/run_model_replay.py
```

输出：

- `model_outputs/FD_BASELINE_OUTPUTS.jsonl`
- `model_outputs/FD_SKILL_OUTPUTS.jsonl`
- `model_outputs/FD_GOLD_GUIDED_OUTPUTS.jsonl`

## 评估

```bash
python3 replay_run_effect_v1/scripts/evaluate_fd_effect.py
```

如果没有模型输出，评估报告会明确写空结果，不会伪造指标。

## 输出解析

`scripts/output_parser.py` 支持纯 JSON、markdown code fence、前后带解释文本的 JSON、wrapper `output` 字段和 Python-literal dict。
