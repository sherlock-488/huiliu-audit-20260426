# Run Log

审计目标：只做最小可运行验证，不跑全量 infer，不联网，不修改业务代码。

## Environment Notes

- 当前目录：`/Users/sherlock/Desktop/01_项目代码/回流`
- Python：系统 `python3`
- `openai` / `tqdm` 本地包存在，但 `annotate.py --infer` 默认访问内部地址 `https://aigc.sankuai.com/v1/openai/native`，本轮按要求不联网，因此跳过 infer。
- `dedup_and_quality.py` 在当前目录不存在。

## Commands Executed

### 1. 创建输出目录

```bash
mkdir -p analysis_outputs tools
mkdir -p analysis_outputs/sample_raw_input analysis_outputs/pipeline_sample_outputs analysis_outputs/run_logs
```

结果：成功。

### 2. 查看 `process.py` 参数

```bash
python3 huiliu-data-processor/huiliu-data-processor/process.py --help
```

结果：成功。`process.py` 参数为 `input_file output_file [--stage {1,2}]`。

### 3. 查看 `pipeline.sh` 参数

```bash
bash huiliu-pipeline/huiliu-pipeline/pipeline.sh
```

结果：返回码 1，符合预期，因为未传必需参数。usage 显示：

- 必需：`<开始日期> <结束日期> <输出目录>`
- 可选：`--infer`、`--filter`、`--model`、`--num-procs`、`--batch-size`、`--sample`、`--skip-query`、`--skip-clean`、`--skip-annotation`、`--no-monitor`

### 4. 复制根目录 JSONL 前 100 条

```bash
head -n 100 xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl > analysis_outputs/sample_raw_input/root_jsonl_first100.jsonl
```

结果：成功，生成 100 行样本。

### 5. 用根目录 JSONL 尝试 `process.py --stage 1`

```bash
python3 huiliu-data-processor/huiliu-data-processor/process.py \
  --stage 1 \
  analysis_outputs/sample_raw_input/root_jsonl_first100.jsonl \
  analysis_outputs/pipeline_sample_outputs/root_stage1_intermediate.jsonl \
  > analysis_outputs/run_logs/process_stage1_root_sample.log 2>&1
```

结果：命令成功退出，但产物 0 行。日志摘要：

- 输入总行数：100
- 有效会话数：0
- 有效数据条数：0
- 匹配完成：0 条数据

解释：`process.py` 阶段 1 代码要求每行是 4 列 TSV 且第三列以 `User` 开头；根目录文件是 JSONL，字段为 `sessionId`、`问题场景`、`source`、`input`、`target`。

### 6. 用根目录 JSONL 尝试完整 `process.py`

```bash
python3 huiliu-data-processor/huiliu-data-processor/process.py \
  xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl \
  analysis_outputs/pipeline_sample_outputs/root_full_attempt_cleaned.jsonl \
  > analysis_outputs/run_logs/process_full_root_jsonl.log 2>&1
```

结果：返回码 1。产物：

- `root_full_attempt_cleaned_intermediate.jsonl`：0 行
- `root_full_attempt_cleaned.jsonl`：0 行

stderr/stdout 摘要：

- 阶段 1 读取 13,524 行，但有效数据条数为 0。
- 阶段 2 输入总行数为 0，统计打印时触发 `ZeroDivisionError: division by zero`。

结论：当前根目录 JSONL 不能直接作为 `process.py` raw 输入。

### 7. 用仓库 fixture 尝试 `process.py --stage 2`

```bash
python3 huiliu-data-processor/huiliu-data-processor/process.py \
  --stage 2 \
  huiliu-data-processor/huiliu-data-processor/tests/test_data_with_user_reply.jsonl \
  analysis_outputs/pipeline_sample_outputs/fixture_cleaned_data.jsonl \
  > analysis_outputs/run_logs/process_stage2_fixture.log 2>&1
```

结果：成功，生成 `fixture_cleaned_data.jsonl`，2 行。

日志摘要：

- 输入总行数：7
- 通过过滤：2
- 被过滤：5
- 过滤原因：用户负面反馈、包含退货/取回关键词、包含其他业务名称、过度承诺、过多口语词。

### 8. 尝试 `dedup_and_quality.py`

```bash
python3 huiliu-data-processor/huiliu-data-processor/dedup_and_quality.py \
  analysis_outputs/pipeline_sample_outputs/fixture_cleaned_data.jsonl \
  analysis_outputs/pipeline_sample_outputs/fixture_deduped_data.jsonl \
  > analysis_outputs/run_logs/dedup_and_quality_missing.log 2>&1
```

结果：返回码 2。错误摘要：

```text
can't open file '.../huiliu-data-processor/huiliu-data-processor/dedup_and_quality.py': [Errno 2] No such file or directory
```

结论：pipeline 的去重质量检查步骤在当前本地文件中缺脚本，无法跑通。

### 9. 用 fixture cleaned_data 尝试 `annotate.py`

```bash
python3 huiliu-data-annotation/huiliu-data-annotation/annotate.py \
  analysis_outputs/pipeline_sample_outputs/fixture_cleaned_data.jsonl \
  analysis_outputs/pipeline_sample_outputs/annotation \
  > analysis_outputs/run_logs/annotate_fixture.log 2>&1
```

结果：成功。生成：

- `analysis_outputs/pipeline_sample_outputs/annotation_profession.jsonl`：2 行
- `analysis_outputs/pipeline_sample_outputs/annotation_exaggeration.jsonl`：2 行
- `analysis_outputs/pipeline_sample_outputs/annotation_risk.jsonl`：2 行

### 10. 生成数据审计报告

```bash
python3 tools/audit_jsonl_schema.py . \
  --json-output analysis_outputs/data_audit.json \
  --md-output analysis_outputs/data_audit_report.md
```

结果：成功。扫描 15 个 JSONL，总行数 13,584，成功解析 13,582，失败 2。失败文件来自 `__MACOSX` AppleDouble 元数据文件。

### 11. 生成 CaseRecord 样例

```bash
python3 tools/normalize_cases.py \
  --root-jsonl xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl \
  --pipeline-dir analysis_outputs/pipeline_sample_outputs \
  --output analysis_outputs/normalized_cases_sample.jsonl \
  --report analysis_outputs/normalized_schema_report.md
```

结果：成功，写入 58 条 normalized sample。报告说明：

- `sample_id` 全部由 SHA1 生成。
- `turn_index` 0/58 有显式字段，均未凭空推断。
- prompt 内系统信号和方案列表未强行结构化。
- 输出样例中的文本和 `raw` 均做 PII mask。

## Generated Files

`analysis_outputs/pipeline_sample_outputs/`：

- `fixture_cleaned_data.jsonl`：2 行
- `annotation_profession.jsonl`：2 行
- `annotation_exaggeration.jsonl`：2 行
- `annotation_risk.jsonl`：2 行
- `root_stage1_intermediate.jsonl`：0 行
- `root_full_attempt_cleaned_intermediate.jsonl`：0 行
- `root_full_attempt_cleaned.jsonl`：0 行

`analysis_outputs/run_logs/`：

- `process_stage1_root_sample.log`
- `process_full_root_jsonl.log`
- `process_stage2_fixture.log`
- `dedup_and_quality_missing.log`
- `annotate_fixture.log`

## Required Internal Environment / Permissions

- AIDA 拉数需要 `mtdata` / 内部 BI SDK、SSO、表权限。
- `annotate.py --infer` 需要内部兼容 OpenAI API 访问权限和有效 app_id/API key。
- 学城上传报告需要 `km` CLI 和权限。
- 当前本地缺 `dedup_and_quality.py`，不是权限问题，是文件缺失。

## Next Step Recommendation

优先向上游确认并补齐三件事：

1. `process.py` raw 输入样例：四列 TSV `session_id / model_name / input_prompt / output`。
2. `dedup_and_quality.py` 的实际代码或替代脚本路径。
3. 用于行级对齐的唯一键设计：建议马上引入 `sample_id`，不要只依赖 `session_id`。

