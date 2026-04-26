---
name: huiliu-data-processor
description: "智能客服回流数据处理工具 V2.5。三阶段处理（数据转换→过滤→工具统计），17个过滤规则+工具分布分析，覆盖用户认可度、工具合规、输出质量、场景逻辑、能力边界等维度。输入原始txt对话数据，输出干净的JSONL训练数据+工具使用统计。触发词：处理回流数据、清洗客服数据、过滤bad case、生成训练数据、工具分布统计。"
---

# 回流数据处理工具 V2.5

将美团智能客服的原始对话数据（txt 格式）处理成干净的训练数据（JSONL 格式）。

## 🎯 核心特性

**当前版本**: V2.6 (2026-04-21)
**规则数量**: 23 个过滤规则
**测试覆盖**: 31 个测试用例，100% 通过率
**新增功能**: 工具分布统计分析

### 主要功能

- ✅ **三阶段处理**: 数据转换（提取 user_reply）→ 数据过滤（24 个规则）→ 工具统计分析
- ✅ **用户认可度筛选**: 必须包含正面反馈关键词
- ✅ **工具合规性检查**: 工具白名单、赔付金额档位、信号逻辑一致性
- ✅ **输出质量检查**: 长度、重复、口语词、过度承诺、退款越权
- ✅ **能力边界检查**: 退货/取回、打电话、转人工、升级客服、声称真人
- ✅ **业务逻辑检查**: 小象单商品退款上下文、赔付冲突、其他业务名称
- ✅ **智能参数传递**: 每个规则使用正确的检查对象

---

## 使用方式

### 完整流程（推荐）

```bash
# 进入 skill 目录
cd ~/.openclaw/workspace/.claude/skills/huiliu-data-processor

# 一键处理（两阶段自动执行）
python3 process.py input.txt output.jsonl

# 分析工具分布（新增步骤）
python3 scripts/analyze_tools.py output.jsonl
```

### 分步执行

```bash
# 阶段1: 数据转换（提取 user_reply）
python3 process.py input.txt intermediate.jsonl --stage 1

# 阶段2: 数据过滤（应用 17 个规则）
python3 process.py intermediate.jsonl output.jsonl --stage 2
```

### 示例

```bash
# 处理昨天导出的数据
python3 process.py ~/Downloads/aida_workflow_20260324.txt output_20260324.jsonl
python3 scripts/sample.py large_data.txt sample_1000.txt 1000
```

**3. 统计分析（了解数据分布）**
```bash
# 分析原始数据的基本统计信息
python3 scripts/analyze.py <输入文件>
# 输出：模型分布、输入/输出长度统计

# 分析过滤后数据的工具分布（新增）
python3 scripts/analyze_tools.py <输出文件.jsonl>
# 输出：ResponseSolution、DialogueAgreeSolution 工具分布、Top 20 高频工具
```

### 高级用法

```bash
# 指定配置文件
python3 process.py input.txt output.jsonl --config config.json

# 导出统计信息
python3 process.py input.txt output.jsonl --stats stats.json

# 批量处理
for file in data/*.txt; do
  python3 process.py "$file" "output/$(basename $file .txt).jsonl"
done
```

---

## 输入格式

**输入文件**：txt 格式，支持两种格式

**格式 1：TSV（推荐）**
```
session_id	model_name	input_prompt	output
xxx	model_a	...	...
yyy	model_b	...	...
```

**格式 2：JSON（每行一条）**
```
{"session_id": "xxx", "model_name": "xxx", "input_prompt": "...", "output": "..."}
{"session_id": "yyy", "model_name": "yyy", "input_prompt": "...", "output": "..."}
```

**字段说明**：
- `session_id` - 会话 ID
- `model_name` - 模型名称
- `input_prompt` - 输入 prompt（包含方案列表、系统信号、对话历史）
- `output` - 模型输出（JSON 格式，包含 Response、ResponseSolution 等）

---

## 输出格式

**输出文件**：JSONL 格式，每行一条训练样本

```jsonl
{"input": "格式化后的输入", "target": "格式化后的输出", "session_id": "xxx", "metadata": {...}}
{"input": "格式化后的输入", "target": "格式化后的输出", "session_id": "yyy", "metadata": {...}}
```

**字段说明**：
- `input` - 训练输入（格式化后的 prompt）
- `target` - 训练目标（格式化后的 response）
- `session_id` - 会话 ID（用于追溯）
- `metadata` - 元数据（模型名称、过滤标记等）

---

## 📋 17 个过滤规则

| # | 规则名称 | 检查对象 | 说明 |
|---|---------|---------|------|
| 1 | 用户负面反馈检查 | `user_reply` | 过滤负面关键词 |
| 3 | 非法工具/方案检查 | `ResponseSolution` | 检查工具和赔付金额 |
| 4 | 过度承诺检查 | `Response` | 过滤"一定"、"保证"等 |
| 5 | 过多口语词检查 | `Response` | 限制口语词数量（≤5个） |
| 6 | 输出长度检查 | `Response` | 长度范围 10-2000 字符 |
| 7 | 重复回复检查 | `Response` | 检测重复内容 |
| 8 | 退货/取回关键词 | `Response` | 智能客服无此能力 |
| 9 | 其他业务名称 | `Response` | 避免混淆其他业务 |
| 10 | 转人工关键词 | `user_reply` + `Response` | 过滤转人工相关对话 |
| 11 | 信号逻辑校验 | `input_prompt` + `ResponseSolution` | 方案与信号一致性 |
| 12 | 不可赔付但操作赔付 | `input_prompt` + `ResponseSolution` | 赔付权限检查 |
| 13 | 退款越权检查 | `Response` + `input_prompt` | 不能说"已退款" |
| 14 | 客服声称自己是真人 | `Response` + `context` | 不能说自己是人工 |
| 15 | 说要给用户打电话 | `Response` | 不能说要给用户打电话 |
| 16 | 升级/转接其他客服 | `Response` | 不能说要转接专员 |
| 17 | 小象单商品退款上下文 | `ResponseSolution` + `context` | 需要图片或选择 |
| 18 | 话术信号：超售后状态 | `input_prompt` + `Response` | 订单未超售后时不能提及超售后 |
| 19 | 话术信号：骑手接单状态 | `input_prompt` + `Response` | 骑手状态不一致时不能说已有骑手接单 |
| 20 | 帮您操作退款 | `Response` | 不能说"帮您操作退款"（越权承诺） |
| 21 | 承诺代办发票 | `Response` | 不能承诺帮用户开具/申请发票 |
| 22 | 告知已关闭月付 | `Response` | 不能说已帮用户关闭月付（越权操作） |
| 23 | 低质话术（我无法） | `Response` | 包含"我无法"的无效回复 |
| 24 | 提及发票作废 | `Response` | 不能说"作废发票"或"发票作废"（越权操作） |

### 规则分类

**用户侧（1个）**: 用户负面反馈

**工具/方案侧（5个）**: 非法工具、信号逻辑、赔付冲突、小象退款上下文

**输出质量侧（5个）**: 过度承诺、口语词、长度、重复、退款越权

**能力边界侧（5个）**: 退货/取回、其他业务、转人工、声称真人、打电话、升级转接

### 6. 能力边界检查
**规则**：过滤超出智能客服能力范围的回复
- ❌ 退货/取回关键词：退货、退回、取回、保留商品、上门取件、取件、自行处理、丢弃、扔掉、寄回、退还、商品处理、物品处理、货物退回
- ❌ 其他业务名称：拼好饭、放心吃、美团买菜、美团优选、美团闪购、象大厨、象会员、象超市

---

## 处理流程

```
输入 txt 文件
    ↓
1. 解析 JSON 数据
    ↓
2. 提取字段（session_id, model_name, input_prompt, output）
    ↓
3. 用户认可度筛选
    ↓
4. Bad Case 过滤（多维度检查）
    ↓
5. 工具合规性验证
    ↓
6. 赔付合规性检查
    ↓
7. 输出质量检查
    ↓
8. 能力边界检查（退货/取回、其他业务）
    ↓
9. 格式化为训练格式
    ↓
10. 写入 JSONL 文件
    ↓
输出干净的训练数据
    ↓
11. 工具分布统计（新增）
    ↓
生成工具使用分析报告
```

---

## 统计信息

处理完成后会显示：
- 📊 输入总行数
- ✅ 通过过滤的行数
- ❌ 被过滤的行数
- 📈 通过率
- 📁 输出文件路径

**示例输出**：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 处理统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输入总行数: 70,359
✅ 通过过滤: 45,230 (64.3%)
❌ 被过滤: 25,129 (35.7%)

过滤原因分布：
  - 用户负面反馈: 8,520
  - 非法工具: 3,240
  - 赔付不合规: 1,850
  - 输出质量差: 6,789
  - 场景逻辑错误: 2,130
  - 其他: 2,600

📁 输出文件: output_train.jsonl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## AI 使用指南

### 典型对话流程

**用户**："帮我处理这个回流数据文件，过滤 bad case"

**AI 执行步骤**：
1. 确认输入文件路径
2. 确认输出文件路径（默认：同目录 + `_processed.jsonl`）
3. 执行处理脚本：
   ```bash
   cd ~/.openclaw/workspace/.claude/skills/huiliu-data-processor
   python3 process.py <input_file> <output_file>
   ```
4. 等待处理完成（通常 1-5 分钟，取决于数据量）
5. 展示统计信息
6. **自动执行工具分布分析（新增）**：
   ```bash
   python3 scripts/analyze_tools.py <output_file>
   ```
7. 展示工具使用分布（ResponseSolution、DialogueAgreeSolution、Top 20 高频工具）
8. 告知输出文件路径

### 常见场景

**场景 1：处理昨天导出的数据**
```bash
python3 process.py ~/Downloads/aida_workflow_exports/aida_workflow_20260320_20260320_*.txt output_20260320.jsonl
```

**场景 2：处理前先验证和抽样**
```bash
# 第一步：快速验证格式
python3 scripts/validate.py large_data.txt

# 第二步：抽取样本测试
python3 scripts/sample.py large_data.txt sample_1000.txt 1000

# 第三步：分析样本
python3 scripts/analyze.py sample_1000.txt

# 第四步：处理完整数据
python3 process.py large_data.txt output.jsonl

# 第五步：分析工具分布（新增）
python3 scripts/analyze_tools.py output.jsonl
```

**场景 3：批量处理多个文件**
```bash
for file in ~/Downloads/aida_workflow_exports/*.txt; do
  python3 process.py "$file" "processed/$(basename $file .txt).jsonl"
done
```

---

## 配置选项

可以通过编辑 `config.json` 自定义过滤规则：

```json
{
  "filter_negative": true,
  "check_compliance": true,
  "check_quality": true,
  "max_output_length": 2000,
  "min_output_length": 10,
  "allowed_compensation": [3, 5, 8, 10, 15, 20],
  "allowed_delivery_fee": [3],
  "max_modal_particles": 5,
  "max_repetitions": 3
}
```

---

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| `FileNotFoundError` | 检查输入文件路径是否正确 |
| `JSONDecodeError` | 检查输入文件格式是否为有效 JSON |
| `处理速度慢` | 数据量大时正常，可以分批处理 |
| `过滤率过高` | 调整 `config.json` 中的过滤规则 |
| `输出文件为空` | 检查是否所有数据都被过滤了 |

---

## 注意事项

- 输入文件必须是 txt 格式，每行一条 JSON
- 输出文件会覆盖已存在的同名文件
- 大文件（>1GB）建议分批处理
- 过滤规则基于美团小象超市客服场景，其他场景需调整
- 处理过程会在内存中完成，确保内存足够

---

## 文件结构

```
huiliu-data-processor/
├── SKILL.md                          # 本文档
├── README.md                         # 使用指南
├── CHANGELOG.md                      # 更新日志
├── PROJECT_OVERVIEW.md               # 项目总览
├── process.py                        # 主处理脚本（V2.4，~780行，17规则）
├── config.json                       # 配置文件
├── docs/                             # 详细文档目录
│   ├── CHANGELOG_V2.2.md             # V2.2 详细更新日志
│   ├── CHANGELOG_V2.3.md             # V2.3 详细更新日志
│   ├── CHANGELOG_V2.4.md             # V2.4 详细更新日志
│   └── SUMMARY_FINAL_V2.4.md         # 最终总结文档
├── tests/                            # 测试文件目录
│   ├── test_new_rules.jsonl          # 规则 10-12 测试数据
│   ├── test_refund_overpromise.jsonl # 规则 13 测试数据
│   ├── test_claim_human.jsonl        # 规则 14 测试数据
│   ├── test_call_escalate.jsonl      # 规则 15-16 测试数据
│   └── test_xiaoxiang_refund.jsonl   # 规则 17 测试数据
├── archive/                          # 归档目录（旧版本文件）
│   ├── process.py                    # V1 旧脚本
│   ├── filters.py                    # V1 过滤规则
│   └── README.md                     # V1 文档
├── scripts/                          # 工具脚本
├── utils/                            # 工具模块
└── examples/                         # 示例文件
```
