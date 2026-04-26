# Repo Inventory

审计时间：2026-04-26。范围：当前工作目录 `/Users/sherlock/Desktop/01_项目代码/回流`。本报告只基于本地 README / SKILL / shell / Python 代码内容，不联网。

## Top Level

- `aida-workflow-query/` 与 `aida-workflow-query.zip`
- `huiliu-data-annotation/` 与 `huiliu-data-annotation.zip`
- `huiliu-data-processor/` 与 `huiliu-data-processor.zip`
- `huiliu-pipeline/` 与 `huiliu-pipeline.zip`
- `xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl`
- 本次审计新增：`tools/`、`analysis_outputs/`

## Module Summary

### aida-workflow-query/aida-workflow-query

主要文件：

- `README.md`
- `SKILL.md`
- `EXAMPLES.md`
- `query.sh`
- `bi_query.py`
- `convert_to_tsv.py`

作用推测：AIDA Workflow 日志拉数工具。README / SKILL 写明通过 `mtdata` / BI SDK 查询 `mart_aigc_prompt.aida_workflow_node_logs`，提取 `session_id`、`model_name`、`input_prompt`、`output`，可输出 TSV / CSV / JSONL / JSON。`query.sh` 负责参数解析、SQL 拼接、分片查询、格式转换；`bi_query.py` 调用内部 BI Python SDK；`convert_to_tsv.py` 将 BI JSONL 结果转为目标格式。

### huiliu-data-processor/huiliu-data-processor

主要文件：

- `README.md`
- `SKILL.md`
- `CHANGELOG.md`
- `process.py`
- `config.json`
- `scripts/analyze.py`
- `scripts/analyze_tools.py`
- `scripts/sample.py`
- `scripts/validate.py`
- `utils/parser.py`
- `utils/formatter.py`
- `utils/statistics.py`
- `utils/validator.py`
- `tests/*.jsonl`
- `archive/` 与 `docs/` 中的历史文档和归档代码

作用推测：回流训练数据清洗模块。README / SKILL 描述为三阶段或两阶段处理：原始 AIDA txt/TSV 转换为带 `user_reply` 的中间 JSONL，再执行 17 个过滤规则，最后可分析工具分布。`process.py` 是实际主入口，当前代码明确按 TSV 四列解析：`session_id\tmodel_name\tinput_prompt\toutput`。过滤逻辑覆盖用户认可、负面反馈、工具白名单、过度承诺、口语词、长度、重复、退货/取回、其他业务、转人工、信号一致性、赔付冲突、退款越权、声称真人、打电话、升级转接、小象单商品退款上下文等。

### huiliu-data-annotation/huiliu-data-annotation

主要文件：

- `README.md`
- `SKILL.md`
- `annotate.py`
- `filter_results.py`

作用推测：精标/自动标注数据构造与结果过滤模块。README / SKILL 写明从 processor 输出的 cleaned JSONL 中提取对话历史、客服回复、系统信号、工具方案，构造三类标注数据：专业度、表达问题、风险问题。`annotate.py` 同时支持构建模式和 `--infer` 推理模式；`filter_results.py` 合并三类推理结果并回贴原始训练数据。

### huiliu-pipeline/huiliu-pipeline

主要文件：

- `README.md`
- `SKILL.md`
- `CHANGELOG.md`
- `README_DEDUP.md`
- `DEDUP_FINAL.md`
- `QUICK_START.md`
- `EXAMPLES.md`
- `AUTO_MONITOR.md`
- `MONITOR_README.md`
- `pipeline.sh`
- `collect_metrics.py`
- `dedup_final.py`
- `monitor_server.py`
- `auto_monitor.sh`
- `notify_progress.sh`
- `start_monitor.sh`

作用推测：端到端流水线编排模块。README / SKILL 描述一键执行 AIDA 查询、数据清洗、去重质量检查、三维标注构建、可选推理、可选结果过滤，并生成报告和监控进度。实际 `pipeline.sh` 是入口，但它调用的 `dedup_and_quality.py` 在当前解压出的 `huiliu-data-processor/huiliu-data-processor/` 下不存在。

## Pipeline Entry Points

- 主流水线入口：`huiliu-pipeline/huiliu-pipeline/pipeline.sh`
- AIDA 拉数入口：`aida-workflow-query/aida-workflow-query/query.sh`
- AIDA BI SDK 执行：`aida-workflow-query/aida-workflow-query/bi_query.py`
- AIDA 输出转换：`aida-workflow-query/aida-workflow-query/convert_to_tsv.py`
- 数据清洗入口：`huiliu-data-processor/huiliu-data-processor/process.py`
- 标注构建/推理入口：`huiliu-data-annotation/huiliu-data-annotation/annotate.py`
- 标注结果过滤入口：`huiliu-data-annotation/huiliu-data-annotation/filter_results.py`
- 最终去重工具：`huiliu-pipeline/huiliu-pipeline/dedup_final.py`

## Requested File Paths

- `process.py`
  - `huiliu-data-processor/huiliu-data-processor/process.py`
  - `huiliu-data-processor/huiliu-data-processor/archive/process.py`
- `dedup_and_quality.py`
  - 未找到。`pipeline.sh` 引用了该文件，但当前目录不存在同名文件。
- `annotate.py`
  - `huiliu-data-annotation/huiliu-data-annotation/annotate.py`
- `filter_results.py`
  - `huiliu-data-annotation/huiliu-data-annotation/filter_results.py`
- `pipeline.sh`
  - `huiliu-pipeline/huiliu-pipeline/pipeline.sh`
  - `huiliu-pipeline/huiliu-pipeline/pipeline.sh.bak`
- `query.sh` 或其它 AIDA 拉数脚本
  - `aida-workflow-query/aida-workflow-query/query.sh`
  - `aida-workflow-query/aida-workflow-query/bi_query.py`
  - `aida-workflow-query/aida-workflow-query/convert_to_tsv.py`

## README / SKILL / CHANGELOG Summary

- `aida-workflow-query/aida-workflow-query/README.md`: AIDA Workflow 日志查询快速开始、前置条件、输出字段和故障排查。
- `aida-workflow-query/aida-workflow-query/SKILL.md`: 更完整的 skill 描述，支持日期、采样、格式、分片、appid/nodeid、processor 直连；强调不要直接用 `mtdata bi run`。
- `huiliu-data-annotation/huiliu-data-annotation/README.md`: 标注数据构建、模型推理、结果过滤三步说明，列出三类标注维度和输入输出格式。
- `huiliu-data-annotation/huiliu-data-annotation/SKILL.md`: 将 annotation 工具描述为三模式：构建、推理、过滤；说明 prompt 内信号提取逻辑和 result 格式。
- `huiliu-data-processor/huiliu-data-processor/README.md`: 回流数据处理 V2，两阶段处理、17 条过滤规则、输入 TSV/JSON 说明和工具统计。
- `huiliu-data-processor/huiliu-data-processor/SKILL.md`: V2.5 描述，强调三阶段处理、17 条规则、测试覆盖和工具分布分析。
- `huiliu-data-processor/huiliu-data-processor/CHANGELOG.md`: V1.0 到 V2.5 规则演进，当前写到 V2.5；包括工具分布、退款越权、转人工、能力边界等新增规则。
- `huiliu-data-processor/huiliu-data-processor/archive/README.md`: 归档版说明。
- `huiliu-data-processor/huiliu-data-processor/archive/CHANGELOG.md`: 归档版 changelog。
- `huiliu-data-processor/huiliu-data-processor/archive/CHANGELOG_V2.md`: 归档 V2 变更说明。
- `huiliu-data-processor/huiliu-data-processor/archive/CHANGELOG_V2.1.md`: V2.1 规则变更说明。
- `huiliu-data-processor/huiliu-data-processor/docs/README.md`: docs 目录说明。
- `huiliu-data-processor/huiliu-data-processor/docs/CHANGELOG_V2.2.md`: V2.2 规则变更说明。
- `huiliu-data-processor/huiliu-data-processor/docs/CHANGELOG_V2.3.md`: V2.3 规则变更说明。
- `huiliu-data-processor/huiliu-data-processor/docs/CHANGELOG_V2.4.md`: V2.4 规则变更说明。
- `huiliu-data-processor/huiliu-data-processor/scripts/README.md`: 脚本工具说明，包含分析、抽样、校验、工具分布等。
- `huiliu-data-processor/huiliu-data-processor/tests/README.md`: 测试数据说明。
- `huiliu-data-processor/huiliu-data-processor/utils/README.md`: utils 目录说明。
- `huiliu-pipeline/huiliu-pipeline/README.md`: 端到端 pipeline 使用方式、参数、输出文件、报告生成。
- `huiliu-pipeline/huiliu-pipeline/SKILL.md`: pipeline skill 描述，强调自动监控、查询、清洗、标注、推理、过滤五步。
- `huiliu-pipeline/huiliu-pipeline/CHANGELOG.md`: 2026-03-25 更新，自动监控、报告完整路径、CORS 修复、报告鲁棒性。
- `huiliu-pipeline/huiliu-pipeline/README_DEDUP.md`: 最终训练数据重复度筛选工具说明。

