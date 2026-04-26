# Pipeline Lineage Audit

审计范围：`aida-workflow-query`、`huiliu-data-processor`、`huiliu-data-annotation`、`huiliu-pipeline` 本地代码。未修改业务代码。

## Goodcase Pipeline Step Order

基于 `huiliu-pipeline/huiliu-pipeline/pipeline.sh` 和 README，主流程为：

1. AIDA Workflow 拉数：`query.sh` 生成 `raw_data.txt`。
2. 数据清洗：`process.py raw_data.txt cleaned_data.jsonl`。
3. 去重和质量检查：`dedup_and_quality.py cleaned_data.jsonl deduped_data.jsonl`。
4. 标注数据构建：`annotate.py deduped_data.jsonl annotation`。
5. 可选模型推理：`annotate.py --infer annotation_{type}.jsonl result_{type}.jsonl`。
6. 可选结果过滤：`filter_results.py --profession ... --original cleaned_data.jsonl --output filtered_final.jsonl`。
7. 可选最终去重：README 提到可再跑 `dedup_final.py filtered_final.jsonl final_training_data.jsonl`，但 `pipeline.sh` 只打印提示，不自动执行。

注意：当前目录没有 `dedup_and_quality.py`，因此步骤 3 在本地无法执行。

## Inputs, Outputs, Core Logic

| Step | Script | Input | Output | Core logic |
|---|---|---|---|---|
| 1 | `aida-workflow-query/aida-workflow-query/query.sh` | date range, appid, nodeid | `raw_data.txt` or formatted export | SQL 查询 AIDA node logs，提取 `session_id`, `model_name`, `input_prompt`, `output`；可采样、分片、格式转换。 |
| 2a | `huiliu-data-processor/huiliu-data-processor/process.py::collect_data_from_txt` | TSV: `session_id\tmodel_name\tinput_prompt\toutput` | intermediate JSONL | 解析四列 TSV，提取 `context`，按 session 内最长 history 推导用户后续认可回复。 |
| 2b | `huiliu-data-processor/huiliu-data-processor/process.py::filter_data` | intermediate JSONL | `cleaned_data.jsonl` | 执行 17 条过滤规则，输出训练格式：`input`, `target`, `session_id`, `metadata`。 |
| 3 | `dedup_and_quality.py` | `cleaned_data.jsonl` | `deduped_data.jsonl` | pipeline 预期存在，但当前仓库未找到，无法确认实际逻辑。 |
| 4 | `huiliu-data-annotation/huiliu-data-annotation/annotate.py::build_annotation_data` | `deduped_data.jsonl` | `annotation_profession.jsonl`, `annotation_exaggeration.jsonl`, `annotation_risk.jsonl` | 从 `input` / `target` 提取 context、signals、Response、ResponseSolution，构造三类标注 prompt。 |
| 5 | `huiliu-data-annotation/huiliu-data-annotation/annotate.py::infer_annotations` | `annotation_*.jsonl` | `result_*.jsonl` | 调 OpenAI-compatible API，将模型输出写入 `predict_content`。 |
| 6 | `huiliu-data-annotation/huiliu-data-annotation/filter_results.py::merge_and_filter_results` | 三类 `result_*.jsonl` + original | `filtered_final.jsonl` | 解析 `predict_content`，过滤不专业、有表达问题、有风险问题的样本，再按 `session_id` 回贴原始数据。 |
| 7 | `huiliu-pipeline/huiliu-pipeline/dedup_final.py` | final JSONL | deduped JSONL | 独立最终去重工具，支持完全相同/相似度去重，不在主 pipeline 自动执行。 |

## Annotation Outputs

`annotate.py` 构建模式固定生成三份文件：

- `{output_prefix}_profession.jsonl`
- `{output_prefix}_exaggeration.jsonl`
- `{output_prefix}_risk.jsonl`

代码证据：

```python
# huiliu-data-annotation/huiliu-data-annotation/annotate.py:210-213
output_profession = f"{output_prefix}_profession.jsonl"
output_exaggeration = f"{output_prefix}_exaggeration.jsonl"
output_risk = f"{output_prefix}_risk.jsonl"
```

每条 annotation 输出字段包括 `input`、`session_id`、`metadata.annotation_type`。专业度样本包含 signals、context、reply、tools；表达问题和风险样本包含 context、reply。

## Infer Result Outputs

`pipeline.sh` 对 `profession` / `exaggeration` / `risk` 三类逐个推理，输出：

- `result_profession.jsonl`
- `result_exaggeration.jsonl`
- `result_risk.jsonl`

`annotate.py --infer` 将模型结果写入 `predict_content`：

```python
# huiliu-data-annotation/huiliu-data-annotation/annotate.py:479-482
with open(output_file, 'w', encoding='utf-8') as g:
    for complet in rec_data:
        g.write(json.dumps(complet, ensure_ascii=False) + '\n')
```

推理依赖内部兼容 OpenAI API：

```python
# huiliu-data-annotation/huiliu-data-annotation/annotate.py:512-514
parser.add_argument('--model', type=str, default='DeepSeek-R1', help='模型名称（默认：DeepSeek-R1）')
parser.add_argument('--api-base', type=str, default='https://aigc.sankuai.com/v1/openai/native', help='API 地址')
parser.add_argument('--api-keys', type=str, nargs='+', default=['1853267739235090515'], help='API keys')
```

## filter_results.py Merge Logic

`filter_results.py` 读取三类 result 后，分别用 `session_id` 建 dict：

```python
# huiliu-data-annotation/huiliu-data-annotation/filter_results.py:89-112
data = json.loads(line)
session_id = data.get('session_id')
predict = parse_predict_content(data.get('predict_content', '{}'))
profession_results[session_id] = predict
...
exaggeration_results[session_id] = predict
...
risk_results[session_id] = predict
```

它取三个 dict 的 `session_id` 交集，逐个判断是否过滤：

```python
# huiliu-data-annotation/huiliu-data-annotation/filter_results.py:126-148
all_session_ids = set(profession_results.keys()) & \
                  set(exaggeration_results.keys()) & \
                  set(risk_results.keys())
...
if should_remove:
    ...
else:
    valid_session_ids.add(session_id)
```

最后按 `session_id` 在 original 中回贴：

```python
# huiliu-data-annotation/huiliu-data-annotation/filter_results.py:172-182
with open(original_file, 'r', encoding='utf-8') as f_in, \
     open(output_file, 'w', encoding='utf-8') as f_out:
    for line in f_in:
        ...
        session_id = data.get('session_id')
        if session_id in valid_session_ids:
            f_out.write(line)
```

## Cleaned vs Deduped Relationship

`pipeline.sh` 明确定义了两个文件：

```bash
# huiliu-pipeline/huiliu-pipeline/pipeline.sh:258-262
RAW_DATA="$OUTPUT_DIR/raw_data.txt"
CLEANED_DATA="$OUTPUT_DIR/cleaned_data.jsonl"
DEDUPED_DATA="$OUTPUT_DIR/deduped_data.jsonl"
ANNOTATION_PREFIX="$OUTPUT_DIR/annotation"
```

`annotate.py` 的输入是 `DEDUPED_DATA`：

```bash
# huiliu-pipeline/huiliu-pipeline/pipeline.sh:547-548
ANNOTATE_CMD="python3 annotate.py \"$DEDUPED_DATA\" \"$ANNOTATION_PREFIX\""
```

`filter_results.py --original` 传入的是 `CLEANED_DATA`：

```bash
# huiliu-pipeline/huiliu-pipeline/pipeline.sh:714-719
if python3 filter_results.py \
    --profession "$RESULT_PROFESSION" \
    --exaggeration "$RESULT_EXAGGERATION" \
    --risk "$RESULT_RISK" \
    --original "$CLEANED_DATA" \
    --output "$FILTERED_OUTPUT"; then
```

结论：annotation 使用 deduped，filter 回贴 cleaned。

## Risks Found

### 疑似风险：`session_id` 被当作唯一 key

证据：`filter_results.py::merge_and_filter_results` 用 `session_id` 作为三类结果 dict key 和 original 回贴 key。

```python
# filter_results.py:90-92
session_id = data.get('session_id')
predict = parse_predict_content(data.get('predict_content', '{}'))
profession_results[session_id] = predict
```

根目录数据审计显示没有精确 `session_id` 字段，但有 `sessionId`；`sessionId` 共有 2,384 个唯一值、2,363 个有重复、最大重复 24 次。因此如果后续标准化成 `session_id` 后仍只按 session 对齐，会把 turn-level 样本混在同一 key 下。

### 疑似风险：同一个 session 多条样本可能覆盖

证据：三类 result 被写入 dict，重复 `session_id` 会覆盖前值。

```python
# filter_results.py:90-112
profession_results[session_id] = predict
exaggeration_results[session_id] = predict
risk_results[session_id] = predict
```

如果同一 session 内存在多轮样本，不同 turn 的推理结果无法保留 row-level 区分。

### 疑似风险：annotation 用 deduped_data，filter 回贴 cleaned_data

证据见上节。`pipeline.sh` 先调用 `dedup_and_quality.py "$CLEANED_DATA" "$DEDUPED_DATA"`，随后 `annotate.py "$DEDUPED_DATA"`，但 `filter_results.py --original "$CLEANED_DATA"`。如果 dedup 删除了 session 内某些行，而 filter 只用 session_id 回贴，可能把同 session 的未标注 cleaned 行带回来。

### 疑似风险：统计脚本读取字段名和真实字段名不一致

证据 1：`collect_metrics.py::analyze_cleaned_data` 读取小写 `response_solution`。

```python
# huiliu-pipeline/huiliu-pipeline/collect_metrics.py:41-46
target = data.get("target", {})
if isinstance(target, str):
    target = json.loads(target)
solution = target.get("response_solution", "")
```

但 `process.py::filter_data` 输出的 target 来自原始 target，并保留大驼峰 `ResponseSolution`。

```python
# huiliu-data-processor/huiliu-data-processor/process.py:740-744
target = json.loads(data["target"])
results.append({
    "input": data["input"],
    "target": target,
    "session_id": data["session_id"],
```

证据 2：`collect_metrics.py::analyze_inference_results` 读取 `result` 字段。

```python
# huiliu-pipeline/huiliu-pipeline/collect_metrics.py:87-90
data = json.loads(line.strip())
result = data.get("result", {})
```

但 `annotate.py --infer` 生成的是 `predict_content`，`filter_results.py` 也是解析 `predict_content`。

### 疑似风险：`LEGAL_TOOLS` / 方案白名单与线上可用方案可能不同步

证据：`process.py` 内硬编码 `LEGAL_TOOLS` 和赔付金额档位。

```python
# huiliu-data-processor/huiliu-data-processor/process.py:201-215
LEGAL_TOOLS = [
    "加急调度", "系统催单", "智能跟单", "取消订单",
    ...
]
LEGAL_COMPENSATION = [3, 5, 8, 10, 15, 20]
LEGAL_DELIVERY_FEE = [3]
```

根目录 prompt 中的方案列表包含更多方案名，例如 `发送送达图片`、`加急催促退款审核`、`无骑手接单跟单`、`引导自助管理地址`、`引导自助开通会员`、`引导自助查看-xx` 等。是否线上可用需要产品/训练师确认。

### 疑似风险：清洗后丢失独立 `context` 字段，影响后续行级历史检查

证据：`process.py::collect_data_from_txt` 中间态保留 `context`，但 `filter_data` 输出只保留 `input`、`target`、`session_id`、`metadata.model_name`、`metadata.user_reply`。

```python
# process.py:82-87
origin_datas.append({
    'session_id': session_id,
    'model_name': model_name,
    'context': message_history_str,
    "input": input_prompt,
    "target": target
})
```

```python
# process.py:741-747
results.append({
    "input": data["input"],
    "target": target,
    "session_id": data["session_id"],
    "metadata": {
        "model_name": data["model_name"],
        "user_reply": data["user_reply"]
    }
})
```

`input` 当前仍包含 prompt/context，但没有独立结构化 `dialogue_history` / `context` 字段；如果后续流程截断或改写 `input`，会削弱历史重复和 row-level lineage 检查。

### 阻塞风险：`pipeline.sh` 引用的 `dedup_and_quality.py` 缺失

证据：`pipeline.sh` 第 496 行执行 `python3 dedup_and_quality.py "$CLEANED_DATA" "$DEDUPED_DATA"`；当前 `find . -name dedup_and_quality.py` 无结果。实际本地运行该命令返回 `[Errno 2] No such file or directory`。

