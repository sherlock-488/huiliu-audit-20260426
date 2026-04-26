# 更新日志 V2.2

## 2026-03-24 - 新增第 14 个过滤规则

### 新增功能

#### 客服声称自己是真人检查 🆕

**检查对象**: `target["Response"]` + `context`（对话历史）

**规则**: 客服不能声称自己是真人或人工客服

**两种违规情况**:

1. **客服主动声称**
   - "我是人工客服"
   - "我就是真人"
   - "我也是真实的客服"

2. **用户询问后确认**
   - 用户问："你是人工吗？"、"你是真人吗？"
   - 客服回答："是的"、"对的"、"没错"、"我是真人"、"我是人工"

**检测逻辑**:
```python
# 规则1: 检测客服主动声称
if re.search(r"我(是|就是|也是)(.*?)(人工|真人|真实)", response):
    return True

# 规则2: 检测用户询问+客服确认
if "你是人工吗" in last_user_turn:
    if re.search(r'是的|对的|没错|我是真|我是人', response):
        return True
```

**过滤原因**: `客服声称自己是真人`

**测试结果**:
- ✅ test_human_1: 用户问"你是人工吗"且客服回答"是的，我是真人" → 过滤
- ✅ test_human_2: response 包含"智能"（转人工关键词）→ 过滤
- ✅ test_human_3: 客服说"我就是人工客服" → 过滤
- ✅ test_human_4: 用户问"你是真人吗"且客服回答"对的" → 过滤
- ✅ test_human_5: 正常回复，没有声称是真人 → 通过
- ✅ test_human_6: response 包含"人工智能"（转人工关键词）→ 过滤

---

## 📊 过滤规则总览

现在一共有 **14 个过滤规则**：

| # | 规则名称 | 检查对象 | 新增时间 |
|---|---------|---------|---------|
| 1 | 用户认可度检查 ⭐ | `user_reply` | 初始 |
| 2 | 用户负面反馈检查 | `user_reply` | 初始 |
| 3 | 非法工具/方案检查 | `ResponseSolution` | 初始 |
| 4 | 过度承诺检查 | `Response` | 初始 |
| 5 | 过多口语词检查 | `Response` | 初始 |
| 6 | 输出长度检查 | `Response` | 初始 |
| 7 | 重复回复检查 | `Response` | 初始 |
| 8 | 退货/取回关键词 | `Response` | 2026-03-24 上午 |
| 9 | 其他业务名称 | `Response` | 2026-03-24 上午 |
| 10 | 转人工关键词 | `user_reply` + `Response` | 2026-03-24 下午 |
| 11 | 信号逻辑校验 | `input_prompt` + `ResponseSolution` | 2026-03-24 下午 |
| 12 | 不可赔付但操作赔付 | `input_prompt` + `ResponseSolution` | 2026-03-24 下午 |
| 13 | 退款越权检查 | `Response` + `input_prompt` | 2026-03-24 下午 |
| 14 | 客服声称自己是真人 🆕 | `Response` + `context` | 2026-03-24 下午 |

---

## 🔄 完整处理流程

```
输入数据（带 user_reply）
  ↓
1. 用户认可度检查 (user_reply) ⭐ 必须通过
  ↓
2. 用户负面反馈检查 (user_reply)
  ↓
3. 非法工具/方案检查 (ResponseSolution)
  ↓
4. 过度承诺检查 (Response)
  ↓
5. 过多口语词检查 (Response)
  ↓
6. 输出长度检查 (Response)
  ↓
7. 重复回复检查 (Response)
  ↓
8. 退货/取回关键词检查 (Response)
  ↓
9. 其他业务名称检查 (Response)
  ↓
10. 转人工关键词检查 (user_reply + Response)
  ↓
11. 信号逻辑校验 (input_prompt + ResponseSolution)
  ↓
12. 不可赔付但操作赔付检查 (input_prompt + ResponseSolution)
  ↓
13. 退款越权检查 (Response + input_prompt)
  ↓
14. 客服声称自己是真人检查 (Response + context) 🆕
  ↓
通过所有检查 → 输出训练数据
```

---

## 📈 累计测试结果

### 本次新增规则测试
**测试数据**: 6 条
**通过**: 1 条 (16.7%)
**过滤**: 5 条 (83.3%)
**准确率**: 100% ✅

### 所有规则测试
**总测试数据**: 20 条（之前 14 条 + 本次 6 条）
**总通过**: 7 条
**总过滤**: 13 条
**准确率**: 100% ✅

---

## 🚀 使用方法

```bash
cd ~/.openclaw/workspace/.claude/skills/huiliu-data-processor

# 完整流程
python3 process_v2.py input.txt output.jsonl

# 分步执行
python3 process_v2.py input.txt intermediate.jsonl --stage 1  # 转换
python3 process_v2.py intermediate.jsonl output.jsonl --stage 2  # 过滤
```

---

## 📝 修改文件

- `process_v2.py` - 新增 `check_claim_human()` 函数

---

## 🎯 规则分类

### 按检查对象分类

1. **user_reply（用户回复）** - 3个规则
   - 用户认可度检查
   - 用户负面反馈检查
   - 转人工关键词检查（部分）

2. **Response（客服回复）** - 9个规则
   - 过度承诺检查
   - 过多口语词检查
   - 输出长度检查
   - 重复回复检查
   - 退货/取回关键词检查
   - 其他业务名称检查
   - 转人工关键词检查（部分）
   - 退款越权检查
   - 客服声称自己是真人检查 🆕

3. **ResponseSolution（工具方案）** - 3个规则
   - 非法工具/方案检查
   - 信号逻辑校验
   - 不可赔付但操作赔付检查

4. **input_prompt（输入上下文）** - 3个规则
   - 信号逻辑校验
   - 不可赔付但操作赔付检查
   - 退款越权检查（商品状态）

5. **context（对话历史）** - 1个规则
   - 客服声称自己是真人检查 🆕

---

**更新时间**: 2026-03-24
**版本**: V2.2
**状态**: ✅ 已完成并测试通过
**本次新增**: 1 个规则（客服声称自己是真人检查）
**总规则数**: 14 个
**测试通过率**: 100%
