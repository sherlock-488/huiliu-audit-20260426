# case_2026-04-20 goodcase 前半段验证报告

## 1. Raw 文件路径和格式判断
- raw 文件: `/Users/sherlock/Desktop/01_项目代码/回流/case_2026-04-20.txt`
- 文件大小: `996264686` bytes
- 前 200 bytes 安全预览: `session_id	model_name	input_prompt	output\n2046164****90089268	xx-solution-kefuronghe18b-13k7-sample-x	User:\n你的名字叫团团，你是美团的智能客服助理。用户现在向你反馈美团�`
- raw_format: `tsv_txt`
- 前 5 行 tab 列数: `[4, 4, 4, 4, 4]`
- 前 5 行第 3 列是否以 User 开头: `[False, True, True, True, True]`
- process.py 输入要求判断: 满足 TSV 输入要求；第 1 行是表头，会被 process.py 跳过，数据行第 3 列以 User 开头。

## 2. process.py stage1
- 命令: `python3 huiliu-data-processor/process.py runs/case_2026-04-20/raw_sample_2000.txt runs/case_2026-04-20/stage1_user_reply_sample.jsonl --stage 1`
- 状态: `success`
- 输出行数: `81`
- 日志: `runs/case_2026-04-20/logs/stage1_sample.log`
- 日志摘要: 读取 2000 行，有效会话数 1822，有效数据条数 1995，匹配完成 81 条。

## 3. process.py stage2
- 命令: `python3 huiliu-data-processor/process.py runs/case_2026-04-20/stage1_user_reply_sample.jsonl runs/case_2026-04-20/cleaned_data_sample.jsonl --stage 2`
- 状态: `success`
- 输出行数: `44`
- 日志: `runs/case_2026-04-20/logs/stage2_sample.log`
- 日志摘要: 输入 81 条，通过 44 条，过滤 37 条。

## 4. dedup_and_quality.py
- 命令: `python3 huiliu-data-processor/dedup_and_quality.py runs/case_2026-04-20/cleaned_data_sample.jsonl runs/case_2026-04-20/deduped_data_sample.jsonl`
- 状态: `success`
- cleaned_data_sample 行数: `44`
- deduped_data_sample 行数: `44`
- dedup 保留率: `100.00%`
- 日志: `runs/case_2026-04-20/logs/dedup_sample.log`

## 5. 各步骤输入输出行数
| step | input | output | input_lines | output_lines |
|---|---|---|---:|---:|
| sample | raw | raw_sample_2000.txt | - | 2000 |
| stage1 | raw_sample_2000.txt | stage1_user_reply_sample.jsonl | 2000 | 81 |
| stage2 | stage1_user_reply_sample.jsonl | cleaned_data_sample.jsonl | 81 | 44 |
| dedup | cleaned_data_sample.jsonl | deduped_data_sample.jsonl | 44 | 44 |

## 6. 过滤原因分布摘要
- - 用户负面反馈: 19
- - 过度承诺: 11
- - 包含退货/取回关键词: 3
- - 退款越权（已退款表述）: 1
- - 小象单商品退款缺少图片或选择: 1
- - 包含转人工关键词: 1
- - 升级/转接其他客服: 1

## 7. ijson
- ijson 状态: `not_checked_not_needed_for_tsv`
- 本次 raw 为 TSV，不需要 JSON array stdin 路径，因此未依赖 ijson。

## 8. context 检查
- cleaned 前 20 条是否有 context 字段: `False`
- deduped 前 20 条是否有 context 字段: `False`
- cleaned 顶层字段: `['input', 'metadata', 'session_id', 'target']`
- deduped 顶层字段: `['input', 'metadata', 'session_id', 'target']`
- 风险: cleaned/deduped 不含 `context`，`dedup_and_quality.py` 中“与历史对话重复”的检查依赖 `data.get("context", "")`，因此在当前两阶段产物上可能无法真正检查历史重复。

## 9. sample_id / turn 粒度检查
- `sample_id` 非空条数: `0`
- `turn_id` 非空条数: `0`
- `turn_index` 非空条数: `0`
- `request_id` 非空条数: `0`
- `trace_id` 非空条数: `0`
- cleaned session_id 唯一数: `41`
- cleaned session_id 重复 session 数: `3`
- cleaned session_id 最大重复次数: `2`
- 结论: 当前 cleaned 输出没有 `sample_id`，也没有 `turn_id` / `turn_index` / `request_id` / `trace_id`。下一步建议引入 row-level `sample_id`，不要只用 `session_id` 对齐后续 annotation/result。

## 10. dedup 输出样例 3 条（已脱敏）
```json
[
  {
    "session_id": "204620198****182916",
    "metadata": {
      "model_name": "<MASKED>",
      "user_reply": "用户:给我看下你提交的截图"
    },
    "target": {
      "Response": "客服:请问还有其他问题可以帮您吗",
      "ResponseSolution": "无",
      "DialogueAgreeSolution": "无"
    },
    "input_preview": "User:\n你的名字叫团团，你是美团的智能客服助理。用户现在向你反馈美团业务的相关问题，你将收到方案列表、系统信号、对话历史等作为输入。\n请你根据提供的所有信息，按步骤执行以下任务：\n1. 输出客服在下一轮的最佳回复，要求输出格式为“客服:xxx”。\n2. 分析上述最佳回复中是否包含“方案列表”中的方案，输出方案名称或“无”。\n3. 查看对话历史的结尾部分，分析用户和客服是否就某个待执行方案达成一致，输出方案名称或“无”。\n4. 将以上信息整合成JSON格式输出：{\"Response\":\"[最佳回复]\", \"ResponseSolution\":\"[方案名..."
  },
  {
    "session_id": "204606***2588",
    "metadata": {
      "model_name": "<MASKED>",
      "user_reply": "用户:这是刚买的"
    },
    "target": {
      "Response": "客服:您好，非常抱歉给您带来不好的购物体验了，您反馈的问题我们非常重视，我已经记录下来，后续会透传至监管部门加强品控，但是您的订单已经超售后时效了，确实无法帮您申请退款了，建议您下次在售后期内联系我们，我们会及时为您处理",
      "ResponseSolution": "无",
      "DialogueAgreeSolution": "无"
    },
    "input_preview": "User:\n你的名字叫团团，你是美团的智能客服助理。用户现在向你反馈美团业务的相关问题，你将收到方案列表、系统信号、对话历史等作为输入。\n请你根据提供的所有信息，按步骤执行以下任务：\n1. 输出客服在下一轮的最佳回复，要求输出格式为“客服:xxx”。\n2. 分析上述最佳回复中是否包含“方案列表”中的方案，输出方案名称或“无”。\n3. 查看对话历史的结尾部分，分析用户和客服是否就某个待执行方案达成一致，输出方案名称或“无”。\n4. 将以上信息整合成JSON格式输出：{\"Response\":\"[最佳回复]\", \"ResponseSolution\":\"[方案名..."
  },
  {
    "session_id": "204622***4911",
    "metadata": {
      "model_name": "<MASKED>",
      "user_reply": "用户:嗯嗯"
    },
    "target": {
      "Response": "客服:您放心，您反馈的问题我已经记录下来，后续会透传至监管部门加强品控，争取给您带来更好的购物体验",
      "ResponseSolution": "无",
      "DialogueAgreeSolution": "无"
    },
    "input_preview": "User:\n你的名字叫团团，你是美团的智能客服助理。用户现在向你反馈美团业务的相关问题，你将收到方案列表、系统信号、对话历史等作为输入。\n请你根据提供的所有信息，按步骤执行以下任务：\n1. 输出客服在下一轮的最佳回复，要求输出格式为“客服:xxx”。\n2. 分析上述最佳回复中是否包含“方案列表”中的方案，输出方案名称或“无”。\n3. 查看对话历史的结尾部分，分析用户和客服是否就某个待执行方案达成一致，输出方案名称或“无”。\n4. 将以上信息整合成JSON格式输出：{\"Response\":\"[最佳回复]\", \"ResponseSolution\":\"[方案名..."
  }
]
```

## 11. ResponseSolution 分布摘要
### cleaned
- `无`: `40`
- `再次外呼门店-修改订单`: `1`
- `选择商品`: `1`
- `外呼骑手-协商调换货品`: `1`
- `取消订单`: `1`
### deduped
- `无`: `40`
- `再次外呼门店-修改订单`: `1`
- `选择商品`: `1`
- `外呼骑手-协商调换货品`: `1`
- `取消订单`: `1`

## 12. 是否可以进入 annotation 阶段
- can_continue_to_annotation: `true`
- 说明: 小样本前半段链路 raw -> stage1 -> stage2 -> dedup 已跑通，可以用该小样本继续验证 annotation；但在进入正式回流前，建议先处理 `context` 丢失和 `sample_id` 缺失两个 lineage 风险。

## 13. 下一步建议
- P0: 在 stage1/stage2/dedup 输出中保留稳定 `sample_id`，并保留 `source_line` 或等价 row-level lineage。
- P0: 明确 `context` 是否必须随 cleaned/deduped 传递；如果 dedup 质量检查要检查历史重复，当前两阶段产物需要保留 `context`。
- P1: 用同一个 2000 行样本继续跑 annotation dry-run，不跑 infer，先检查 annotation 文件结构和 key 对齐。
- P1: 后续全量跑前，先确认 TSV 表头处理、字符编码、以及第一行 header 是否固定存在。

