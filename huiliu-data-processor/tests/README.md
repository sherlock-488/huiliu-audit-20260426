# 测试文件说明

本目录包含所有过滤规则的测试文件。

## 测试文件列表

| 文件 | 测试规则 | 用例数 | 通过率 |
|------|---------|--------|--------|
| `test_new_rules.jsonl` | 规则 10-12 | 8 | 100% |
| `test_refund_overpromise.jsonl` | 规则 13 | 6 | 100% |
| `test_claim_human.jsonl` | 规则 14 | 6 | 100% |
| `test_call_escalate.jsonl` | 规则 15-16 | 10 | 100% |
| `test_xiaoxiang_refund.jsonl` | 规则 17 | 7 | 100% |

**总计**: 31 个测试用例，100% 通过率 ✅

## 测试规则说明

### 规则 10-12: 转人工、信号逻辑、赔付冲突
- **测试文件**: `test_new_rules.jsonl`
- **规则 10**: 转人工关键词检查
- **规则 11**: 信号逻辑校验（加急调度、取消订单、催促退款）
- **规则 12**: 不可赔付但操作赔付检查

### 规则 13: 退款越权
- **测试文件**: `test_refund_overpromise.jsonl`
- **规则**: 不能说"已退款"（除非已全部退款）

### 规则 14: 客服声称自己是真人
- **测试文件**: `test_claim_human.jsonl`
- **规则**: 不能说"我是人工"、"我是真人"

### 规则 15-16: 打电话、升级转接
- **测试文件**: `test_call_escalate.jsonl`
- **规则 15**: 说要给用户打电话检查
- **规则 16**: 升级/转接其他客服检查

### 规则 17: 小象单商品退款上下文
- **测试文件**: `test_xiaoxiang_refund.jsonl`
- **规则**: 单商品退款需要"图片"或"选择"

## 运行测试

```bash
cd ~/.openclaw/workspace/.claude/skills/huiliu-data-processor

# 测试规则 10-12
python3 process.py tests/test_new_rules.jsonl tests/test_new_rules_output.jsonl --stage 2

# 测试规则 13
python3 process.py tests/test_refund_overpromise.jsonl tests/test_refund_output.jsonl --stage 2

# 测试规则 14
python3 process.py tests/test_claim_human.jsonl tests/test_claim_human_output.jsonl --stage 2

# 测试规则 15-16
python3 process.py tests/test_call_escalate.jsonl tests/test_call_escalate_output.jsonl --stage 2

# 测试规则 17
python3 process.py tests/test_xiaoxiang_refund.jsonl tests/test_xiaoxiang_refund_output.jsonl --stage 2
```

---

**创建时间**: 2026-03-24
**版本**: V2.4
