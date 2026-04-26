# 回流数据处理工具 - 项目总览

## 🎯 快速开始

```bash
cd ~/.openclaw/workspace/.claude/skills/huiliu-data-processor
python3 process.py input.txt output.jsonl
```

## 📁 主要文件

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `process.py` | 主处理脚本（V2.4，~780行，17规则） | ⭐⭐⭐⭐⭐ |
| `README.md` | 使用指南 | ⭐⭐⭐⭐⭐ |
| `CHANGELOG.md` | 更新日志 | ⭐⭐⭐⭐ |
| `SKILL.md` | Skill 配置文件 | ⭐⭐⭐⭐ |
| `SUMMARY_FINAL_V2.4.md` | 完整项目总结 | ⭐⭐⭐ |

## 📋 版本信息

- **当前版本**: V2.4
- **发布日期**: 2026-03-24
- **规则数量**: 17 个
- **测试用例**: 31 个（100% 通过率）
- **代码行数**: ~780 行

## 🔧 核心功能

### 两阶段处理
1. **阶段1**: 数据转换 - 提取 user_reply
2. **阶段2**: 数据过滤 - 应用 17 个规则

### 17 个过滤规则

**用户侧（2个）**:
- 用户认可度检查 ⭐
- 用户负面反馈检查

**工具/方案侧（5个）**:
- 非法工具/方案检查
- 信号逻辑校验
- 不可赔付但操作赔付
- 小象单商品退款上下文

**输出质量侧（5个）**:
- 过度承诺检查
- 过多口语词检查
- 输出长度检查
- 重复回复检查
- 退款越权检查

**能力边界侧（5个）**:
- 退货/取回关键词
- 其他业务名称
- 转人工关键词
- 客服声称自己是真人
- 说要给用户打电话
- 升级/转接其他客服

## 📊 使用示例

### 完整流程
```bash
python3 process.py input.txt output.jsonl
```

### 分步执行
```bash
# 阶段1: 数据转换
python3 process.py input.txt intermediate.jsonl --stage 1

# 阶段2: 数据过滤
python3 process.py intermediate.jsonl output.jsonl --stage 2
```

### 输出示例
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
  ...

📁 输出文件: output.jsonl
============================================================
```

## 📚 详细文档

- **使用指南**: `README.md`
- **更新日志**: `CHANGELOG.md`
- **详细规则**: `docs/CHANGELOG_V2.2.md`, `docs/CHANGELOG_V2.3.md`, `docs/CHANGELOG_V2.4.md`
- **项目总结**: `docs/SUMMARY_FINAL_V2.4.md`
- **Skill 配置**: `SKILL.md`

## 🧪 测试文件

测试文件位于 `tests/` 目录：
- `tests/test_new_rules.jsonl` - 规则 10-12 测试
- `tests/test_refund_overpromise.jsonl` - 规则 13 测试
- `tests/test_claim_human.jsonl` - 规则 14 测试
- `tests/test_call_escalate.jsonl` - 规则 15-16 测试
- `tests/test_xiaoxiang_refund.jsonl` - 规则 17 测试

## 📦 归档文件

旧版本文件已移至 `archive/` 目录。

## 🚀 版本演进

```
V1.0 (7 规则)
  ↓
V2.0 (9 规则) + 退货/取回、其他业务名称
  ↓
V2.1 (12 规则) + 转人工、信号逻辑、赔付冲突
  ↓
V2.2 (14 规则) + 退款越权、客服声称真人
  ↓
V2.3 (16 规则) + 打电话、升级转接
  ↓
V2.4 (17 规则) + 小象单商品退款上下文
```

---

**项目路径**: `~/.openclaw/workspace/.claude/skills/huiliu-data-processor/`
**最后更新**: 2026-03-24
**作者**: Claude
**用户**: liliz (zhaolili08)
