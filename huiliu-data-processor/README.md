# 回流数据处理工具 V2

快速将原始对话数据处理成干净的训练数据（两阶段处理）。

## 🚀 快速开始

```bash
# 进入 skill 目录
cd ~/.openclaw/workspace/.claude/skills/huiliu-data-processor

# 完整流程（推荐）
python3 process.py input.txt output.jsonl

# 分析工具分布（新增）
python3 scripts/analyze_tools.py output.jsonl
```

## 📋 V2 新特性

### ✨ 两阶段处理

1. **阶段1: 数据转换** - 提取用户回复 (user_reply)
2. **阶段2: 数据过滤** - 应用 9 个过滤规则

### 🎯 关键改进

- ✅ **用户认可度优先**: 第一步检查 `user_reply`，必须包含认可关键词
- ✅ **明确检查对象**:
  - `user_reply` → 用户认可度、负面反馈
  - `Response` → 过度承诺、口语词、长度、重复、退货、业务名称
  - `ResponseSolution` → 非法工具/方案
- ✅ **新增 2 个规则**: 退货/取回关键词、其他业务名称

## 📊 使用示例

### 完整流程
```bash
# 处理数据
python3 process.py ~/Downloads/aida_workflow_20260324.txt output_20260324.jsonl

# 分析工具分布
python3 scripts/analyze_tools.py output_20260324.jsonl
```

### 分步执行
```bash
# 阶段1: 转换（提取 user_reply）
python3 process.py input.txt intermediate.jsonl --stage 1

# 阶段2: 过滤（应用规则）
python3 process.py intermediate.jsonl output.jsonl --stage 2

# 阶段3: 分析工具分布（新增）
python3 scripts/analyze_tools.py output.jsonl
```

## 🔧 17 个过滤规则

| # | 规则名称 | 检查对象 | 说明 |
|---|---------|---------|------|
| 1 | 用户认可度检查 ⭐ | `user_reply` | 必须包含认可关键词（第一步） |
| 2 | 用户负面反馈检查 | `user_reply` | 过滤负面关键词 |
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
| 17 | 小象单商品退款上下文 🆕 | `ResponseSolution` + `context` | 需要图片或选择 |

## 📈 输入输出格式

### 输入 (txt, TSV)
```
session_id	model_name	input_prompt	output
xxx	model_a	User: ...	{"Response": "...", "ResponseSolution": "..."}
```

### 中间格式 (jsonl with user_reply)
```json
{
  "session_id": "xxx",
  "user_reply": "用户：好的，谢谢",
  "input": "User: ...",
  "target": "{...}"
}
```

### 输出 (jsonl, 训练格式)
```json
{
  "input": "User: ...",
  "target": {"Response": "...", "ResponseSolution": "..."},
  "session_id": "xxx",
  "metadata": {"model_name": "...", "user_reply": "..."}
}
```

## 📊 处理统计示例

```
============================================================
📊 处理统计
============================================================
输入总行数: 70,359
✅ 通过过滤: 45,230 (64.3%)
❌ 被过滤: 25,129 (35.7%)

过滤原因分布:
  - 用户未认可: 8,520
  - 用户负面反馈: 3,240
  - 非法工具/方案: 1,850
  - 过度承诺: 2,456
  - 过多口语词: 3,789
  - 输出长度不合理: 2,134
  - 重复回复: 1,340
  - 包含退货/取回关键词: 1,200 🆕
  - 包含其他业务名称: 600 🆕

📁 输出文件: output.jsonl
============================================================
```

## 📝 文件说明

| 文件 | 说明 |
|------|------|
| `process_v2.py` | V2 主脚本（推荐使用） |
| `process.py` | V1 旧脚本（已过时） |
| `FILTER_RULES_V2.md` | 详细规则说明 |
| `CHANGELOG.md` | 更新日志 |

## 🆚 V1 vs V2 vs V2.4

| 特性 | V1 | V2.0 | V2.4 |
|------|----|----|------|
| 数据转换 | ❌ | ✅ 提取 user_reply | ✅ |
| 用户认可度检查 | ❌ | ✅ 第一步必须通过 | ✅ |
| 检查对象明确 | ❌ 混乱 | ✅ 清晰分类 | ✅ |
| 退货/取回过滤 | ❌ | ✅ | ✅ |
| 其他业务名称过滤 | ❌ | ✅ | ✅ |
| 转人工关键词过滤 | ❌ | ❌ | ✅ |
| 信号逻辑校验 | ❌ | ❌ | ✅ |
| 赔付冲突检查 | ❌ | ❌ | ✅ |
| 退款越权检查 | ❌ | ❌ | ✅ |
| 客服声称真人检查 | ❌ | ❌ | ✅ |
| 打电话关键词过滤 | ❌ | ❌ | ✅ |
| 升级转接过滤 | ❌ | ❌ | ✅ |
| 小象单商品退款上下文 | ❌ | ❌ | ✅ |
| 总规则数 | 7 个 | 9 个 | 17 个 |

## ⚡ 性能

- 处理速度: ~10,000 条/分钟
- 内存占用: ~500MB（10万条数据）
- 推荐批次: 单文件不超过 100 万条

---

**创建时间**: 2026-03-24
**版本**: V2
**作者**: Claude
