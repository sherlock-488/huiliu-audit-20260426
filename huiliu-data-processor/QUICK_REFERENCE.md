# 快速参考卡

## 🚀 一键处理

```bash
cd ~/.openclaw/workspace/.claude/skills/huiliu-data-processor

# 完整流程（三阶段）
python3 process.py input.txt output.jsonl && \
python3 scripts/analyze_tools.py output.jsonl
```

---

## 📋 常用命令

| 任务 | 命令 |
|------|------|
| **验证格式** | `python3 scripts/validate.py <文件>` |
| **分析原始数据** | `python3 scripts/analyze.py <文件>` |
| **抽取样本** | `python3 scripts/sample.py <输入> <输出> <数量>` |
| **处理数据** | `python3 process.py <输入> <输出>` |
| **分析工具分布** | `python3 scripts/analyze_tools.py <输出>` |

---

## 🔧 分步执行

```bash
# 阶段1：数据转换
python3 process.py input.txt intermediate.jsonl --stage 1

# 阶段2：数据过滤
python3 process.py intermediate.jsonl output.jsonl --stage 2

# 阶段3：工具统计
python3 scripts/analyze_tools.py output.jsonl
```

---

## 📊 17 个过滤规则速查

| # | 规则 | 检查对象 |
|---|------|---------|
| 1 | 用户认可度 ⭐ | user_reply |
| 2 | 用户负面反馈 | user_reply |
| 3 | 非法工具/方案 | ResponseSolution |
| 4 | 过度承诺 | Response |
| 5 | 过多口语词 | Response |
| 6 | 输出长度 | Response |
| 7 | 重复回复 | Response |
| 8 | 退货/取回 | Response |
| 9 | 其他业务名称 | Response |
| 10 | 转人工 | user_reply + Response |
| 11 | 信号逻辑 | input_prompt + ResponseSolution |
| 12 | 赔付冲突 | input_prompt + ResponseSolution |
| 13 | 退款越权 | Response + input_prompt |
| 14 | 声称真人 | Response + context |
| 15 | 打电话 | Response |
| 16 | 升级转接 | Response |
| 17 | 小象退款上下文 | ResponseSolution + context |

---

## 🎯 工具分布解读

### 正常范围

| 指标 | 正常范围 |
|------|---------|
| 赔付类工具 | 40-60% |
| 退款类工具 | 20-40% |
| 纯文本回复（"无"） | 30-50% |

### 异常信号

- ⚠️ 某个工具 > 80%：过滤过严
- ⚠️ "无" > 80%：大部分工具被过滤
- ⚠️ 出现白名单外工具：检查过滤规则

---

## 🔍 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 有效数据 = 0 | 格式错误 | 检查 TSV 格式 |
| 过滤率 > 80% | 规则过严 | 调整 config.json |
| 工具分布异常 | 数据质量问题 | 抽样检查被过滤数据 |
| 处理速度慢 | 文件过大 | 先抽样测试 |

---

## 📁 输出文件

```
output.jsonl                    # 训练数据（JSONL 格式）
output_intermediate.jsonl       # 中间文件（带 user_reply）
```

---

## 💡 最佳实践

1. ✅ 处理前先验证格式
2. ✅ 大文件先抽样测试
3. ✅ 关注工具分布是否合理
4. ✅ 保存统计信息到文件
5. ✅ 定期备份处理结果

---

## 📚 详细文档

- **SKILL.md** - 完整功能说明
- **README.md** - 快速开始
- **EXAMPLE_USAGE.md** - 使用示例
- **scripts/README.md** - 工具脚本说明
- **CHANGELOG.md** - 版本历史

---

## 🆘 需要帮助？

```bash
# 查看主脚本帮助
python3 process.py --help

# 查看工具脚本帮助
python3 scripts/analyze_tools.py
```

---

## 📌 版本信息

**当前版本**: V2.5 (2026-03-24)
**规则数量**: 17 个过滤规则
**新增功能**: 工具分布统计分析
**测试覆盖**: 31 个测试用例，100% 通过率
