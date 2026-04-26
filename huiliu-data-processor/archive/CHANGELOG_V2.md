# 更新日志 V2

## 2026-03-24 - 新增 4 个过滤规则

### 新增功能

#### 1. 退货/取回关键词过滤
- **检查对象**: `target["Response"]`
- **说明**: 智能客服没有退货取回能力
- **关键词**: 退货、退回、取回、保留商品、上门取件、取件、自行处理、丢弃、扔掉、寄回、退还、商品处理、物品处理、货物退回

#### 2. 其他业务名称过滤
- **检查对象**: `target["Response"]`
- **说明**: 避免混淆其他业务线
- **关键词**: 拼好饭、放心吃、美团买菜、美团优选、美团闪购、象大厨、象会员、象超市

#### 3. 转人工关键词过滤 🆕
- **检查对象**: `user_reply` + `target["Response"]`
- **说明**: 过滤用户要求转人工或客服回复包含转人工意图的对话
- **user_reply 关键词**: 转人工、人工、转人工服务、人工服务、转人工客服、人工客服、客服电话
- **response 关键词**: 帮您申诉、帮您提交、智能、匹配、反馈专员、升级专员、转接、转交、回访

#### 4. 信号逻辑校验 🆕
- **检查对象**: `input_prompt` + `target["ResponseSolution"]`
- **说明**: 检查工具方案与信号是否一致
- **规则**:
  - **加急调度**: 需要 `{订单骑手状态:无骑手接单}` 或 `{订单门店状态:等待骑手接单}`
  - **取消订单**: 需要 `{是否可取消订单:是}`
  - **催促退款审核**: 需要商品退款状态为 `不可退款 退款进行中`

#### 5. 不可赔付但操作赔付冲突检查 🆕
- **检查对象**: `input_prompt` + `target["ResponseSolution"]`
- **说明**: 当 `{订单是否可赔付:否}` 且工具中有 `操作赔付` 时，过滤
- **规则**: 订单明确不可赔付时，不应该执行赔付操作

---

## 📊 过滤规则总览

现在一共有 **12 个过滤规则**：

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
| 10 | 转人工关键词 🆕 | `user_reply` + `Response` | 过滤转人工意图 |
| 11 | 信号逻辑校验 🆕 | `input_prompt` + `ResponseSolution` | 方案与信号一致性 |
| 12 | 不可赔付但操作赔付 🆕 | `input_prompt` + `ResponseSolution` | 赔付权限冲突 |

---

## 🔄 处理流程

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
10. 转人工关键词检查 (user_reply + Response) 🆕
  ↓
11. 信号逻辑校验 (input_prompt + ResponseSolution) 🆕
  ↓
12. 不可赔付但操作赔付检查 (input_prompt + ResponseSolution) 🆕
  ↓
通过所有检查 → 输出训练数据
```

---

## 📈 测试结果

**测试数据**: 8 条

**预期过滤**: 5 条
- test_manual_1: 包含转人工关键词（user_reply 包含"转人工"）
- test_manual_2: 包含转人工关键词（response 包含"帮您申诉"）
- test_signal_1: 信号逻辑不一致（加急调度但骑手状态是"配送中"）
- test_compensation_1: 不可赔付但操作赔付
- test_cancel_1: 信号逻辑不一致（取消订单但是否可取消为"否"）

**预期通过**: 3 条
- test_signal_2: 加急调度且骑手状态是"无骑手接单" ✅
- test_compensation_2: 订单可赔付且有操作赔付 ✅
- test_cancel_2: 取消订单且是否可取消为"是" ✅

**实际结果**: 与预期完全一致 ✅

---

## 🚀 使用方法

### 完整流程（推荐）
```bash
cd ~/.openclaw/workspace/.claude/skills/huiliu-data-processor
python3 process_v2.py input.txt output.jsonl
```

### 分步执行
```bash
# 阶段1: 转换
python3 process_v2.py input.txt intermediate.jsonl --stage 1

# 阶段2: 过滤
python3 process_v2.py intermediate.jsonl output.jsonl --stage 2
```

---

## 📝 修改文件

- `process_v2.py` - 新增 3 个过滤函数和相关关键词列表
- `FILTER_RULES_V2.md` - 需要更新（添加新规则说明）
- `README_V2.md` - 需要更新（更新规则总数）

---

**更新时间**: 2026-03-24
**版本**: V2.1
**状态**: ✅ 已完成并测试通过
**新增规则**: 3 个（转人工关键词、信号逻辑校验、不可赔付但操作赔付）
**总规则数**: 12 个
