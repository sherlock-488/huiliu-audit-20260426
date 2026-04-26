# Recommended Patches

本文件只给修改建议，不直接修改业务代码。优先级基于对 goodcase 回流、精标数据分析、后续 skill 自进化的影响。

## P0

### 1. 引入 row-level `sample_id`

- 风险描述：当前根目录业务数据是 turn-level 候选，`sessionId` 大量重复；现有 annotation/filter 结果链路没有稳定行级唯一键，容易把同一 session 内不同 turn 混淆。
- 证据文件和代码位置：
  - `analysis_outputs/data_audit.json`：根目录 JSONL 无精确 `session_id`，有 `sessionId`；唯一 session 2,384，重复 session 2,363，最大重复 24。
  - `huiliu-data-annotation/huiliu-data-annotation/filter_results.py:90-112`：三类结果 dict 均以 `session_id` 为 key。
- 建议改法：在 processor 输出、annotation 输出、infer result、filter output 全链路新增 `sample_id`。生成规则沿用本次草案：优先 `request_id/trace_id/turn_id`，否则 `sha1(source_file + source_line + session_id + user_query + response + response_solution)`。
- 是否需要产品/训练师确认：不需要确认技术必要性；需要确认是否有线上已有 request/trace/turn 唯一 ID 可直接使用。

### 2. `filter_results.py` 改为按 `sample_id` / `dedup_group_id` 对齐

- 风险描述：按 `session_id` 合并 result 会覆盖同 session 多条标注结果；按 `session_id` 回贴 original 会把同 session 的未标注行带回。
- 证据文件和代码位置：
  - `filter_results.py:90-112`：`profession_results[session_id] = predict` 等覆盖写入。
  - `filter_results.py:126-148`：三类结果取 session 交集。
  - `filter_results.py:172-182`：original 也是按 `session_id` 回贴。
- 建议改法：结果文件和 original 都使用 `sample_id` 对齐；如果去重后需要回灌 cleaned 原行，新增 `dedup_group_id`，并明确“标注样本”和“被代表的 cleaned 行集合”之间的一对多关系。
- 是否需要产品/训练师确认：需要确认 dedup 后是否要回灌同组所有样本，还是只保留代表样本。

### 3. annotation/result/filter 全链路保留 row-level lineage

- 风险描述：annotation 文件只保留 `session_id` 和 `annotation_type`，无法定位回原始行、去重组、source 文件。
- 证据文件和代码位置：
  - `annotate.py:269-275`、`285-291`、`301-305`：输出 `session_id`、`metadata.annotation_type`，无 source_line/sample_id。
  - `annotate.py:479-482`：infer 直接写回 annotation 样本加 `predict_content`。
- 建议改法：annotation 样本保留 `sample_id`、`source_file`、`source_line`、`dedup_group_id`、`original_session_id`、`original_row_hash`。infer 不改变这些字段。
- 是否需要产品/训练师确认：不需要确认字段技术含义；需要确认是否允许在训练文件中保留这些追溯 metadata。

### 4. 显式定义 cleaned_data 与 deduped_data 的回灌关系

- 风险描述：`pipeline.sh` 使用 deduped 做 annotation，却用 cleaned 做 filter original，当前没有 dedup lineage，可能造成未标注 cleaned 行被同 session 标注结果误放行。
- 证据文件和代码位置：
  - `pipeline.sh:496`：`dedup_and_quality.py "$CLEANED_DATA" "$DEDUPED_DATA"`。
  - `pipeline.sh:548`：`annotate.py "$DEDUPED_DATA"`。
  - `pipeline.sh:718`：`filter_results.py --original "$CLEANED_DATA"`。
- 建议改法：`dedup_and_quality.py` 输出 `dedup_group_id` 和代表样本标记；filter 阶段显式选择 `--original "$DEDUPED_DATA"` 或 `--original "$CLEANED_DATA" --lineage dedup_map.jsonl`。
- 是否需要产品/训练师确认：需要确认回灌策略，以免数据量和去重策略不符合训练目标。

## P1

### 1. 在 cleaned_data 中保留独立 `dialogue_history` / `context`

- 风险描述：当前 cleaned 输出只有完整 `input`，没有结构化 `context` 字段；后续如果 prompt 被裁剪或重写，会影响历史重复检测、对话质量分析和 skill evidence 抽取。
- 证据文件和代码位置：
  - `process.py:82-87`：中间态有 `context`。
  - `process.py:741-747`：最终输出未保留 `context`。
- 建议改法：在 `metadata` 或顶层新增 `dialogue_history`，保留原始 context；同时保留 prompt 原文 hash。
- 是否需要产品/训练师确认：需要确认是否允许在训练样本中保存完整历史及脱敏要求。

### 2. 将 `LEGAL_TOOLS` / 方案白名单中心化 registry

- 风险描述：代码中硬编码方案白名单，可能落后于 prompt 内线上方案列表。
- 证据文件和代码位置：
  - `process.py:201-215`：硬编码 `LEGAL_TOOLS`、赔付金额档位。
  - `analysis_outputs/data_audit_report.md` root 样例显示 prompt 方案列表含多个不在 `LEGAL_TOOLS` 中的方案。
- 建议改法：建立版本化 `tools_registry.json` 或从 AIDA 配置导出，processor 读取 registry；报告输出 registry 版本、缺失方案、未知方案。
- 是否需要产品/训练师确认：需要，方案有效性和赔付档位必须由产品/策略/训练师确认。

### 3. 修复 `collect_metrics.py` 字段名不一致

- 风险描述：报告里的工具分布和推理结果分布可能为空或错误。
- 证据文件和代码位置：
  - `collect_metrics.py:45` 读取 `target.get("response_solution", "")`。
  - `process.py` 输出 target 保留 `ResponseSolution`。
  - `collect_metrics.py:89` 读取 `data.get("result", {})`。
  - `annotate.py --infer` / `filter_results.py` 使用 `predict_content`。
- 建议改法：同时兼容 `ResponseSolution` / `response_solution`；推理统计解析 `predict_content` JSON 字符串；增加小样本 fixture 单测。
- 是否需要产品/训练师确认：不需要。

### 4. 拆分 goodcase 标签维度

- 风险描述：当前流程把“用户认可”“合规”“话术质量”“风险”和“skill evidence”混在过滤链路里，难以分析 goodcase 是因哪类信号成立。
- 证据文件和代码位置：
  - `process.py::apply_filters` 顺序过滤 17 条规则，只输出通过/失败原因。
  - `annotate.py` 三维标注为专业度、表达问题、风险问题。
- 建议改法：统一 CaseRecord 中新增多维标签：`user_acceptance`、`policy_compliance`、`response_quality`、`risk_safety`、`tool_grounding`、`skill_evidence`，并保留每个维度的证据字段。
- 是否需要产品/训练师确认：需要，尤其是 goodcase 的训练定义和 skill evidence 的可采纳标准。

### 5. 补齐或替换 `dedup_and_quality.py`

- 风险描述：当前主 pipeline 本地无法跑到 annotation 步骤。
- 证据文件和代码位置：
  - `pipeline.sh:496` 调用 `dedup_and_quality.py`。
  - `find . -name dedup_and_quality.py` 无结果；最小验证返回 `[Errno 2] No such file or directory`。
- 建议改法：补齐脚本，或把 `pipeline.sh` 改为调用当前存在的 `dedup_final.py` / 新增明确的 `dedup_and_quality.py`，并同步 README。
- 是否需要产品/训练师确认：不需要；如果去重策略变化，需要训练师确认。

## P2

### 1. 报告可视化

- 风险描述：当前 Markdown 报告能看，但对场景、方案、过滤原因、重复 session、字段缺失的趋势对比不够直观。
- 证据文件和代码位置：
  - `collect_metrics.py` 已生成 Markdown，但字段统计能力有限。
  - 本次新增 `analysis_outputs/data_audit.json` 已有机器可读统计。
- 建议改法：基于 `data_audit.json` 和 pipeline metrics 生成 HTML/CSV 图表：场景分布、方案分布、重复 session 分布、字段缺失热力表。
- 是否需要产品/训练师确认：可选；确认他们希望优先看的指标。

### 2. 命令行参数统一

- 风险描述：`query.sh`、`process.py`、`annotate.py`、`filter_results.py`、`pipeline.sh` 参数风格不完全统一，路径约定和 sample 行为分散。
- 证据文件和代码位置：
  - `pipeline.sh` 用固定 skill 路径 `$HOME/.openclaw/...`。
  - `process.py` stage 参数和 `annotate.py --sample` 各自实现。
- 建议改法：统一 `--input`、`--output`、`--sample`、`--seed`、`--lineage-output`、`--report-output`；pipeline 支持显式传入本地模块路径。
- 是否需要产品/训练师确认：不需要。

### 3. 单元测试和小样本 fixture

- 风险描述：现有 processor 有测试 fixture，但 pipeline/filter/metrics 的关键 lineage 风险缺少覆盖。
- 证据文件和代码位置：
  - `huiliu-data-processor/tests/*.jsonl` 存在多组规则测试。
  - `filter_results.py` 对重复 session 覆盖、`collect_metrics.py` 字段名兼容没有测试。
- 建议改法：新增 fixtures：
  - 同一 session 多 turn；
  - deduped 与 cleaned 一对多；
  - `predict_content` 解析；
  - `ResponseSolution` / `response_solution` 大小写兼容；
  - 空输入时不除零。
- 是否需要产品/训练师确认：不需要。

