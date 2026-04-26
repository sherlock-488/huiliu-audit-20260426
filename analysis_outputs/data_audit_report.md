# JSONL Schema Audit

- Root: `/Users/sherlock/Desktop/01_项目代码/回流`
- Files scanned: 15
- Total lines: 13584
- Parsed lines: 13582
- Failed lines: 2

## huiliu-data-processor/__MACOSX/huiliu-data-processor/tests/._test_call_escalate.jsonl

- Total lines: 1
- Parsed lines: 0
- Failed lines: 1
- Parse errors: `{"JSONDecodeError": 1}`
- Top-level fields: ``
- Exact `session_id` exists: False
- Session field used for stats: `None`

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|

### Signal Structure Assessment

- Summary: `{}`

### Masked Samples


## huiliu-data-processor/__MACOSX/huiliu-data-processor/tests/._test_call_escalate_output.jsonl

- Total lines: 1
- Parsed lines: 0
- Failed lines: 1
- Parse errors: `{"JSONDecodeError": 1}`
- Top-level fields: ``
- Exact `session_id` exists: False
- Session field used for stats: `None`

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|

### Signal Structure Assessment

- Summary: `{}`

### Masked Samples


## huiliu-data-processor/huiliu-data-processor/tests/test_call_escalate.jsonl

- Total lines: 10
- Parsed lines: 10
- Failed lines: 0
- Top-level fields: `input, model_name, session_id, target, user_reply`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 10
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_call_01(1), test_call_02(1), test_call_03(1), test_call_04(1), test_escalate_01(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 10 | 0.00% | `{"str": 10}` |
| `model_name` | 10 | 0.00% | `{"str": 10}` |
| `session_id` | 10 | 0.00% | `{"str": 10}` |
| `target` | 10 | 0.00% | `{"str": 10}` |
| `user_reply` | 10 | 0.00% | `{"str": 10}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `无` | 7 |
| `外呼骑手-核实情况` | 2 |
| `加急调度` | 1 |

### Model Name Top 30

| Value | Count |
|---|---:|
| `test` | 10 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 10}`
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "session_id": "test_call_01",
  "model_name": "test",
  "user_reply": "用户：好的，谢谢",
  "input": "User: 我的订单还没到\nSystem signals: {订单配送状态: 配送中}",
  "target": "{\"Response\": \"您好，我马上给您打电话核实情况，请注意接听。\", \"ResponseSolution\": \"无\"}"
}
```
Line 2:
```json
{
  "session_id": "test_call_02",
  "model_name": "test",
  "user_reply": "用户：好的",
  "input": "User: 骑手没联系我\nSystem signals: {订单配送状态: 配送中}",
  "target": "{\"Response\": \"好的，我为您联系骑手，稍后会给您回电。\", \"ResponseSolution\": \"外呼骑手-核实情况\"}"
}
```
Line 3:
```json
{
  "session_id": "test_call_03",
  "model_name": "test",
  "user_reply": "用户：行",
  "input": "User: 商品有问题\nSystem signals: {订单配送状态: 已完成}",
  "target": "{\"Response\": \"我这边会致电您了解详细情况。\", \"ResponseSolution\": \"无\"}"
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_call_escalate_output.jsonl

- Total lines: 1
- Parsed lines: 1
- Failed lines: 0
- Top-level fields: `input, metadata, session_id, target`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 1
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_pass_01(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 1 | 0.00% | `{"str": 1}` |
| `metadata` | 1 | 0.00% | `{"dict": 1}` |
| `session_id` | 1 | 0.00% | `{"str": 1}` |
| `target` | 1 | 0.00% | `{"dict": 1}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `无` | 1 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 1}`
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "input": "User: 订单什么时候到\nSystem signals: {订单配送状态: 配送中}",
  "target": {
    "Response": "您的订单预计30分钟内送达，请耐心等待。",
    "ResponseSolution": "无"
  },
  "session_id": "test_pass_01",
  "metadata": {
    "model_name": "test",
    "user_reply": "用户：好的，谢谢"
  }
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_claim_human.jsonl

- Total lines: 6
- Parsed lines: 6
- Failed lines: 0
- Top-level fields: `context, input, model_name, session_id, target, user_reply`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 6
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_human_1(1), test_human_2(1), test_human_3(1), test_human_4(1), test_human_5(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `context` | 6 | 0.00% | `{"str": 6}` |
| `input` | 6 | 0.00% | `{"str": 6}` |
| `model_name` | 6 | 0.00% | `{"str": 6}` |
| `session_id` | 6 | 0.00% | `{"str": 6}` |
| `target` | 6 | 0.00% | `{"str": 6}` |
| `user_reply` | 6 | 0.00% | `{"str": 6}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `无` | 5 |
| `小象整单申请退款` | 1 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `是` | 6 |

### Model Name Top 30

| Value | Count |
|---|---:|
| `model_a` | 6 |

### Signal Structure Assessment

- Summary: `{"no signal marker found in text": 6}`
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text

### Masked Samples

Line 1:
```json
{
  "session_id": "test_human_1",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...",
  "context": "客服：您好，有什么可以帮您的？\n用户：你是人工吗？",
  "target": "{\"Response\": \"是的，我是真人客服，很高兴为您服务\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"是\"}"
}
```
Line 2:
```json
{
  "session_id": "test_human_2",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...",
  "context": "客服：您好，有什么可以帮您的？\n用户：你是人工吗？",
  "target": "{\"Response\": \"我是智能客服，很高兴为您服务\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"是\"}"
}
```
Line 3:
```json
{
  "session_id": "test_human_3",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...",
  "context": "客服：您好，有什么可以帮您的？",
  "target": "{\"Response\": \"我就是人工客服，可以帮您处理\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"是\"}"
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_claim_human_output.jsonl

- Total lines: 1
- Parsed lines: 1
- Failed lines: 0
- Top-level fields: `input, metadata, session_id, target`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 1
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_human_5(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 1 | 0.00% | `{"str": 1}` |
| `metadata` | 1 | 0.00% | `{"dict": 1}` |
| `session_id` | 1 | 0.00% | `{"str": 1}` |
| `target` | 1 | 0.00% | `{"dict": 1}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `小象整单申请退款` | 1 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `是` | 1 |

### Signal Structure Assessment

- Summary: `{"no signal marker found in text": 1}`
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text

### Masked Samples

Line 1:
```json
{
  "input": "User: ...",
  "target": {
    "Response": "好的，我会帮您处理退款申请",
    "ResponseSolution": "小象整单申请退款",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test_human_5",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的"
  }
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_data_with_user_reply.jsonl

- Total lines: 7
- Parsed lines: 7
- Failed lines: 0
- Top-level fields: `input, model_name, session_id, target, user_reply`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 7
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test001(1), test002(1), test003(1), test004(1), test005(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 7 | 0.00% | `{"str": 7}` |
| `model_name` | 7 | 0.00% | `{"str": 7}` |
| `session_id` | 7 | 0.00% | `{"str": 7}` |
| `target` | 7 | 0.00% | `{"str": 7}` |
| `user_reply` | 7 | 0.00% | `{"str": 7}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `无` | 4 |
| `操作赔付-优惠券-5元` | 2 |
| `小象整单申请退款` | 1 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `是` | 6 |
| `否` | 1 |

### Model Name Top 30

| Value | Count |
|---|---:|
| `model_a` | 7 |

### Signal Structure Assessment

- Summary: `{"no signal marker found in text": 7}`
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text

### Masked Samples

Line 1:
```json
{
  "session_id": "test001",
  "model_name": "model_a",
  "user_reply": "用户：好的，谢谢",
  "input": "User: ...",
  "target": "{\"Response\": \"好的，我已经为您申请了退款\", \"ResponseSolution\": \"小象整单申请退款\", \"DialogueAgreeSolution\": \"是\"}"
}
```
Line 2:
```json
{
  "session_id": "test002",
  "model_name": "model_a",
  "user_reply": "用户：不行，我不满意",
  "input": "User: ...",
  "target": "{\"Response\": \"好的，我会处理\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"否\"}"
}
```
Line 3:
```json
{
  "session_id": "test003",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...",
  "target": "{\"Response\": \"您可以安排上门取件，我们会取回商品\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"是\"}"
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_new_rules.jsonl

- Total lines: 8
- Parsed lines: 8
- Failed lines: 0
- Top-level fields: `input, model_name, session_id, target, user_reply`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 8
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_manual_1(1), test_manual_2(1), test_signal_1(1), test_signal_2(1), test_compensation_1(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 8 | 0.00% | `{"str": 8}` |
| `model_name` | 8 | 0.00% | `{"str": 8}` |
| `session_id` | 8 | 0.00% | `{"str": 8}` |
| `target` | 8 | 0.00% | `{"str": 8}` |
| `user_reply` | 8 | 0.00% | `{"str": 8}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `无` | 2 |
| `加急调度` | 2 |
| `操作赔付-优惠券-5元` | 2 |
| `取消订单` | 2 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `是` | 8 |

### Model Name Top 30

| Value | Count |
|---|---:|
| `model_a` | 8 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 6, "no signal marker found in text": 2}`
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=2, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "session_id": "test_manual_1",
  "model_name": "model_a",
  "user_reply": "用户：好的，转人工",
  "input": "User: ...",
  "target": "{\"Response\": \"好的，我会尽快为您处理这个问题\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"是\"}"
}
```
Line 2:
```json
{
  "session_id": "test_manual_2",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...",
  "target": "{\"Response\": \"我会帮您申诉处理，请稍等片刻\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"是\"}"
}
```
Line 3:
```json
{
  "session_id": "test_signal_1",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...\n{订单骑手状态:配送中}\n{订单门店状态:已接单}\n",
  "target": "{\"Response\": \"好的，我为您加急调度处理\", \"ResponseSolution\": \"加急调度\", \"DialogueAgreeSolution\": \"是\"}"
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_new_rules_output.jsonl

- Total lines: 3
- Parsed lines: 3
- Failed lines: 0
- Top-level fields: `input, metadata, session_id, target`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 3
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_signal_2(1), test_compensation_2(1), test_cancel_2(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 3 | 0.00% | `{"str": 3}` |
| `metadata` | 3 | 0.00% | `{"dict": 3}` |
| `session_id` | 3 | 0.00% | `{"str": 3}` |
| `target` | 3 | 0.00% | `{"dict": 3}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `加急调度` | 1 |
| `操作赔付-优惠券-5元` | 1 |
| `取消订单` | 1 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `是` | 3 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 3}`
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "input": "User: ...\n{订单骑手状态:无骑手接单}\n",
  "target": {
    "Response": "好的，我为您加急调度处理",
    "ResponseSolution": "加急调度",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test_signal_2",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的"
  }
}
```
Line 2:
```json
{
  "input": "User: ...\n{订单是否可赔付:是}\n",
  "target": {
    "Response": "好的，我为您申请赔付优惠券",
    "ResponseSolution": "操作赔付-优惠券-5元",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test_compensation_2",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的"
  }
}
```
Line 3:
```json
{
  "input": "User: ...\n{是否可取消订单:是}\n",
  "target": {
    "Response": "好的，我为您取消订单处理",
    "ResponseSolution": "取消订单",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test_cancel_2",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的"
  }
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_output.jsonl

- Total lines: 2
- Parsed lines: 2
- Failed lines: 0
- Top-level fields: `input, metadata, session_id, target`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 2
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test001(1), test007(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 2 | 0.00% | `{"str": 2}` |
| `metadata` | 2 | 0.00% | `{"dict": 2}` |
| `session_id` | 2 | 0.00% | `{"str": 2}` |
| `target` | 2 | 0.00% | `{"dict": 2}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `小象整单申请退款` | 1 |
| `操作赔付-优惠券-5元` | 1 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `是` | 2 |

### Signal Structure Assessment

- Summary: `{"no signal marker found in text": 2}`
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text
- `input`: structured=False, type=str, extracted_count=0, reason=no signal marker found in text

### Masked Samples

Line 1:
```json
{
  "input": "User: ...",
  "target": {
    "Response": "好的，我已经为您申请了退款",
    "ResponseSolution": "小象整单申请退款",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test001",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的，谢谢"
  }
}
```
Line 2:
```json
{
  "input": "User: ...",
  "target": {
    "Response": "已为您申请5元优惠券",
    "ResponseSolution": "操作赔付-优惠券-5元",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test007",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的"
  }
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_refund_output.jsonl

- Total lines: 3
- Parsed lines: 3
- Failed lines: 0
- Top-level fields: `input, metadata, session_id, target`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 3
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_refund_2(1), test_refund_3(1), test_refund_5(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 3 | 0.00% | `{"str": 3}` |
| `metadata` | 3 | 0.00% | `{"dict": 3}` |
| `session_id` | 3 | 0.00% | `{"str": 3}` |
| `target` | 3 | 0.00% | `{"dict": 3}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `小象整单申请退款` | 2 |
| `无` | 1 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `是` | 3 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 3}`
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "input": "User: ...\n{'商品名称': '苹果', '商品退款状态': '可退款'}\n",
  "target": {
    "Response": "好的，已为您申请退款，请耐心等待",
    "ResponseSolution": "小象整单申请退款",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test_refund_2",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的"
  }
}
```
Line 2:
```json
{
  "input": "User: ...\n{'商品名称': '苹果', '商品退款状态': '不可退款 已全部退款'}\n",
  "target": {
    "Response": "好的，已退款成功，请查收",
    "ResponseSolution": "无",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test_refund_3",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的"
  }
}
```
Line 3:
```json
{
  "input": "User: ...\n{'商品名称': '苹果', '商品退款状态': '可退款'}\n",
  "target": {
    "Response": "好的，已操作退款，正在审核中",
    "ResponseSolution": "小象整单申请退款",
    "DialogueAgreeSolution": "是"
  },
  "session_id": "test_refund_5",
  "metadata": {
    "model_name": "model_a",
    "user_reply": "用户：好的"
  }
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_refund_overpromise.jsonl

- Total lines: 6
- Parsed lines: 6
- Failed lines: 0
- Top-level fields: `input, model_name, session_id, target, user_reply`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 6
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_refund_1(1), test_refund_2(1), test_refund_3(1), test_refund_4(1), test_refund_5(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 6 | 0.00% | `{"str": 6}` |
| `model_name` | 6 | 0.00% | `{"str": 6}` |
| `session_id` | 6 | 0.00% | `{"str": 6}` |
| `target` | 6 | 0.00% | `{"str": 6}` |
| `user_reply` | 6 | 0.00% | `{"str": 6}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `小象整单申请退款` | 3 |
| `无` | 3 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `是` | 6 |

### Model Name Top 30

| Value | Count |
|---|---:|
| `model_a` | 6 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 6}`
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "session_id": "test_refund_1",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...\n{'商品名称': '苹果', '商品退款状态': '可退款'}\n",
  "target": "{\"Response\": \"好的，已退款成功，请查收\", \"ResponseSolution\": \"小象整单申请退款\", \"DialogueAgreeSolution\": \"是\"}"
}
```
Line 2:
```json
{
  "session_id": "test_refund_2",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...\n{'商品名称': '苹果', '商品退款状态': '可退款'}\n",
  "target": "{\"Response\": \"好的，已为您申请退款，请耐心等待\", \"ResponseSolution\": \"小象整单申请退款\", \"DialogueAgreeSolution\": \"是\"}"
}
```
Line 3:
```json
{
  "session_id": "test_refund_3",
  "model_name": "model_a",
  "user_reply": "用户：好的",
  "input": "User: ...\n{'商品名称': '苹果', '商品退款状态': '不可退款 已全部退款'}\n",
  "target": "{\"Response\": \"好的，已退款成功，请查收\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"是\"}"
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_xiaoxiang_refund.jsonl

- Total lines: 7
- Parsed lines: 7
- Failed lines: 0
- Top-level fields: `context, input, model_name, session_id, target, user_reply`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 7
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_xx_fail_01(1), test_xx_fail_02(1), test_xx_pass_01(1), test_xx_pass_02(1), test_xx_pass_03(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `context` | 7 | 0.00% | `{"str": 7}` |
| `input` | 7 | 0.00% | `{"str": 7}` |
| `model_name` | 7 | 0.00% | `{"str": 7}` |
| `session_id` | 7 | 0.00% | `{"str": 7}` |
| `target` | 7 | 0.00% | `{"str": 7}` |
| `user_reply` | 7 | 0.00% | `{"str": 7}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `小象单商品退款-50%` | 2 |
| `小象-单商品退款-100%` | 2 |
| `小象单商品退款-80%` | 1 |
| `小象整单申请退款` | 1 |
| `加急调度` | 1 |

### Model Name Top 30

| Value | Count |
|---|---:|
| `test` | 7 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 7}`
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "session_id": "test_xx_fail_01",
  "model_name": "test",
  "user_reply": "用户：好的，谢谢",
  "context": "用户：我要退款\n客服：好的，请稍等",
  "input": "User: 我要退款\nSystem signals: {订单配送状态: 已完成}",
  "target": "{\"Response\": \"好的，我帮您申请单商品退款。\", \"ResponseSolution\": \"小象单商品退款-50%\"}"
}
```
Line 2:
```json
{
  "session_id": "test_xx_fail_02",
  "model_name": "test",
  "user_reply": "用户：好的",
  "context": "用户：商品有问题\n客服：请问是哪个商品呢？\n用户：就那个",
  "input": "User: 商品有问题\nSystem signals: {订单配送状态: 已完成}",
  "target": "{\"Response\": \"好的，我为您操作退款。\", \"ResponseSolution\": \"小象-单商品退款-100%\"}"
}
```
Line 3:
```json
{
  "session_id": "test_xx_pass_01",
  "model_name": "test",
  "user_reply": "用户：好的，谢谢",
  "context": "用户：我要退款\n客服：好的，请您选择需要退款的商品\n用户：选择了第一个",
  "input": "User: 我要退款\nSystem signals: {订单配送状态: 已完成}",
  "target": "{\"Response\": \"好的，我帮您申请单商品退款。\", \"ResponseSolution\": \"小象单商品退款-50%\"}"
}
```

## huiliu-data-processor/huiliu-data-processor/tests/test_xiaoxiang_refund_output.jsonl

- Total lines: 4
- Parsed lines: 4
- Failed lines: 0
- Top-level fields: `input, metadata, session_id, target`
- Exact `session_id` exists: True
- Session field used for stats: `session_id`
- Unique sessions: 4
- Sessions with duplicates: 0
- Max duplicate count: 1
- Top duplicate sessions: test_xx_pass_01(1), test_xx_pass_02(1), test_xx_pass_03(1), test_other_solution_01(1)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 4 | 0.00% | `{"str": 4}` |
| `metadata` | 4 | 0.00% | `{"dict": 4}` |
| `session_id` | 4 | 0.00% | `{"str": 4}` |
| `target` | 4 | 0.00% | `{"dict": 4}` |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `小象单商品退款-50%` | 1 |
| `小象-单商品退款-100%` | 1 |
| `小象单商品退款-80%` | 1 |
| `小象整单申请退款` | 1 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 4}`
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=1, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "input": "User: 我要退款\nSystem signals: {订单配送状态: 已完成}",
  "target": {
    "Response": "好的，我帮您申请单商品退款。",
    "ResponseSolution": "小象单商品退款-50%"
  },
  "session_id": "test_xx_pass_01",
  "metadata": {
    "model_name": "test",
    "user_reply": "用户：好的，谢谢"
  }
}
```
Line 2:
```json
{
  "input": "User: 商品坏了\nSystem signals: {订单配送状态: 已完成}",
  "target": {
    "Response": "好的，我为您操作退款。",
    "ResponseSolution": "小象-单商品退款-100%"
  },
  "session_id": "test_xx_pass_02",
  "metadata": {
    "model_name": "test",
    "user_reply": "用户：好的"
  }
}
```
Line 3:
```json
{
  "input": "User: 退一个商品\nSystem signals: {订单配送状态: 已完成}",
  "target": {
    "Response": "好的，我为您操作退款。",
    "ResponseSolution": "小象单商品退款-80%"
  },
  "session_id": "test_xx_pass_03",
  "metadata": {
    "model_name": "test",
    "user_reply": "用户：好的"
  }
}
```

## xx_all_scene_service_v2_0408_signals_sort_process_multiple_chuli.jsonl

- Total lines: 13524
- Parsed lines: 13524
- Failed lines: 0
- Top-level fields: `input, sessionId, source, target, 问题场景`
- Exact `session_id` exists: False
- Session field used for stats: `sessionId`
- Unique sessions: 2384
- Sessions with duplicates: 2363
- Max duplicate count: 24
- Top duplicate sessions: 2018259425832247332(24), 2035021735775318057(24), 2035316938033029202(24), 2035675996229328975(22), 2035312098712485893(22)

### Field Presence

| Field | Count | Missing Rate | Types |
|---|---:|---:|---|
| `input` | 13524 | 0.00% | `{"str": 13524}` |
| `sessionId` | 13524 | 0.00% | `{"int": 13524}` |
| `source` | 13524 | 0.00% | `{"str": 13524}` |
| `target` | 13524 | 0.00% | `{"str": 13524}` |
| `问题场景` | 13524 | 0.00% | `{"str": 13524}` |

### Scene/场景 Top 30

| Value | Count |
|---|---:|
| `收货场景-品质问题` | 2565 |
| `履约场景-修改订单问题` | 1933 |
| `履约场景-配送问题` | 1893 |
| `收货场景-少送问题` | 817 |
| `发票场景` | 578 |
| `` | 549 |
| `收货场景-错送问题` | 534 |
| `会员场景-续费问题` | 403 |
| `收货场景-退款问题` | 395 |
| `活动场景-常规活动问题` | 363 |
| `会员场景-权益问题` | 312 |
| `收货场景-实描不符问题` | 266 |
| `会员场景-退卡问题` | 265 |
| `收货场景-催退款进度` | 255 |
| `活动场景-通用问题` | 220 |
| `收货场景-重量不足问题` | 218 |
| `其他场景-投诉问题` | 213 |
| `履约场景-履约中订单缺货` | 209 |
| `其他场景` | 141 |
| `其他场景-账号问题` | 138 |
| `长尾场景-金融` | 126 |
| `金融场景-支付问题` | 109 |
| `会员场景-退卡问题诉求` | 98 |
| `活动场景-省钱卡问题` | 89 |
| `会员场景-开通问题` | 86 |
| `金融场景-功能问题` | 86 |
| `其他场景-其他问题` | 82 |
| `未识别` | 76 |
| `履约场景-无骑手接单` | 70 |
| `活动场景-常规活动问题诉求` | 55 |

### ResponseSolution Top 50

| Value | Count |
|---|---:|
| `无` | 9712 |
| `选择商品` | 734 |
| `小象单商品退款-100%` | 475 |
| `取消订单` | 343 |
| `操作赔付-优惠券-3元` | 188 |
| `小象单商品退款-50%` | 187 |
| `催促退款审核;退审跟单` | 141 |
| `引导自助修改订单` | 121 |
| `操作赔付-优惠券-8元` | 114 |
| `操作赔付-优惠券-5元` | 111 |
| `会员卡退款` | 105 |
| `外呼骑手-协商调换货品` | 98 |
| `开发票` | 96 |
| `小象单商品退款-30%` | 88 |
| `管理会员自动续费` | 88 |
| `小象单商品退款-20%` | 69 |
| `操作赔付-优惠券-10元` | 65 |
| `小象整单申请退款` | 55 |
| `操作赔付-优惠券-15元` | 51 |
| `小象单商品退款-40%` | 50 |
| `加急催促退款审核` | 47 |
| `系统催单` | 44 |
| `小象单商品退款-10%` | 37 |
| `智能跟单` | 36 |
| `外呼骑手-催促配送` | 33 |
| `小象单商品退款-70%` | 32 |
| `再次外呼骑手-协商调换货品` | 31 |
| `小象单商品退款-80%` | 31 |
| `操作赔付-优惠券-20元` | 28 |
| `引导自助联系骑手` | 27 |
| `外呼骑手-修改订单` | 26 |
| `无骑手接单跟单` | 26 |
| `发送送达图片` | 26 |
| `再次外呼骑手-催促配送` | 24 |
| `小象单商品退款-60%` | 23 |
| `引导自助查看会员权益` | 18 |
| `催促退款审核` | 16 |
| `再次外呼骑手-修改订单` | 16 |
| `外呼门店-修改订单` | 15 |
| `操作赔付-运费券-3元` | 15 |
| `加急调度` | 13 |
| `引导自助查看配送范围` | 12 |
| `外呼骑手-核实情况` | 9 |
| `退审跟单` | 7 |
| `再次外呼门店-修改订单` | 7 |
| `再次外呼骑手-核实情况` | 7 |
| `引导自助开通会员` | 5 |
| `[地址已脱敏]` | 5 |
| `引导自助查看优惠券` | 4 |
| `操作赔付-优惠券-20元;智能跟单` | 3 |

### DialogueAgreeSolution Top 50

| Value | Count |
|---|---:|
| `无` | 12611 |
| `小象单商品退款-100%` | 273 |
| `取消订单` | 132 |
| `操作赔付-优惠券-3元` | 64 |
| `小象单商品退款-50%` | 60 |
| `外呼骑手-协商调换货品` | 48 |
| `会员卡退款` | 48 |
| `操作赔付-优惠券-8元` | 41 |
| `操作赔付-优惠券-5元` | 35 |
| `小象整单申请退款` | 27 |
| `操作赔付-优惠券-10元` | 21 |
| `外呼骑手-修改订单` | 21 |
| `小象单商品退款-80%` | 20 |
| `小象单商品退款-30%` | 17 |
| `操作赔付-优惠券-15元` | 16 |
| `小象单商品退款-20%` | 15 |
| `操作赔付-优惠券-20元` | 13 |
| `小象单商品退款-70%` | 13 |
| `催促退款审核` | 11 |
| `小象单商品退款-40%` | 10 |
| `外呼门店-修改订单` | 8 |
| `小象单商品退款-60%` | 8 |
| `操作赔付-运费券-3元` | 6 |
| `小象单商品退款-10%` | 6 |

### Signal Structure Assessment

- Summary: `{"text contains {key:value}-like fragments; not JSON/dict structured": 20}`
- `input`: structured=False, type=str, extracted_count=86, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=86, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=86, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=86, reason=text contains {key:value}-like fragments; not JSON/dict structured
- `input`: structured=False, type=str, extracted_count=81, reason=text contains {key:value}-like fragments; not JSON/dict structured

### Masked Samples

Line 1:
```json
{
  "sessionId": 2017995630392295439,
  "问题场景": "履约场景-配送问题",
  "source": "",
  "input": "User:\n你的名字叫团团，你是美团的智能客服助理。用户现在向你反馈美团业务的相关问题，你将收到方案列表、系统信号、对话历史等作为输入。\n请你根据提供的所有信息，按步骤执行以下任务：\n1. 输出客服在下一轮的最佳回复，要求输出格式为“客服:xxx”。\n2. 分析上述最佳回复中是否包含“方案列表”中的方案，输出方案名称或“无”。\n3. 查看对话历史的结尾部分，分析用户和客服是否就某个待执行方案达成一致，输出方案名称或“无”。\n4. 将以上信息整合成JSON格式输出：{\"Response\":\"[最佳回复]\", \"ResponseSolution\":\"[方案名称/无]\", \"DialogueAgreeSolution\":\"[方案名称/无]\"}\n\n## 你查询到的方案列表\n{\"name\": \"加急调度\", \"description\": \"当“订单骑手状态”信号值为“无骑手接单”时，即可向用户表示已经加急扩大调度骑手的范围\"}\n{\"name\": \"系统催单\", \"description\": \"符合催促履约的信号，即可向用户表示已经催促门店分拣/骑手配送\"}\n{\"name\": \"智能跟单\", \"description\": \"符合催促履约的信号，在结束对话时告知用户会持续跟进配送进度\"}\n{\"name\": \"取消订单\", \"description\": \"符合可取消订单的信号，用户同意后执行取消订单\"}\n{\"name\": \"操作赔付-优惠券-xx元\", \"description\": \"符合订单可赔付的信号，以优惠券形式给用户提供赔偿（优惠券仅有六个档位：3元、5元、8元、10元、15元、20元）\"}\n{\"name\": \"操作赔付-运费券-3元\", \"description\": \"符合订单可赔付的信号，以优惠券形式给用户提供赔偿（运费券仅有3元）\"}\n{\"name\": \"选择商品\", \"description\": \"指引用户选择要咨询的商品\"}\n{\"name\": \"发送送达图片\", \"description\": \"若用户反馈未找到包裹，可提供骑手送达时的现场照片，辅助用户寻找\"}\n{\"n...[截断]",
  "target": "{\"Response\": \"客服:我也是可以帮您处理的，辛苦您详细说下您遇到的问题\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"无\"}"
}
```
Line 2:
```json
{
  "sessionId": 2017995630392295439,
  "问题场景": "履约场景-配送问题",
  "source": "",
  "input": "User:\n你的名字叫团团，你是美团的智能客服助理。用户现在向你反馈美团业务的相关问题，你将收到方案列表、系统信号、对话历史等作为输入。\n请你根据提供的所有信息，按步骤执行以下任务：\n1. 输出客服在下一轮的最佳回复，要求输出格式为“客服:xxx”。\n2. 分析上述最佳回复中是否包含“方案列表”中的方案，输出方案名称或“无”。\n3. 查看对话历史的结尾部分，分析用户和客服是否就某个待执行方案达成一致，输出方案名称或“无”。\n4. 将以上信息整合成JSON格式输出：{\"Response\":\"[最佳回复]\", \"ResponseSolution\":\"[方案名称/无]\", \"DialogueAgreeSolution\":\"[方案名称/无]\"}\n\n## 你查询到的方案列表\n{\"name\": \"加急调度\", \"description\": \"当“订单骑手状态”信号值为“无骑手接单”时，即可向用户表示已经加急扩大调度骑手的范围\"}\n{\"name\": \"系统催单\", \"description\": \"符合催促履约的信号，即可向用户表示已经催促门店分拣/骑手配送\"}\n{\"name\": \"智能跟单\", \"description\": \"符合催促履约的信号，在结束对话时告知用户会持续跟进配送进度\"}\n{\"name\": \"取消订单\", \"description\": \"符合可取消订单的信号，用户同意后执行取消订单\"}\n{\"name\": \"操作赔付-优惠券-xx元\", \"description\": \"符合订单可赔付的信号，以优惠券形式给用户提供赔偿（优惠券仅有六个档位：3元、5元、8元、10元、15元、20元）\"}\n{\"name\": \"操作赔付-运费券-3元\", \"description\": \"符合订单可赔付的信号，以优惠券形式给用户提供赔偿（运费券仅有3元）\"}\n{\"name\": \"选择商品\", \"description\": \"指引用户选择要咨询的商品\"}\n{\"name\": \"发送送达图片\", \"description\": \"若用户反馈未找到包裹，可提供骑手送达时的现场照片，辅助用户寻找\"}\n{\"n...[截断]",
  "target": "{\"Response\": \"客服:查询到您的订单已经取消了，您可以重新下单再次购买\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"无\"}"
}
```
Line 3:
```json
{
  "sessionId": 2017995630392295439,
  "问题场景": "履约场景-配送问题",
  "source": "",
  "input": "User:\n你的名字叫团团，你是美团的智能客服助理。用户现在向你反馈美团业务的相关问题，你将收到方案列表、系统信号、对话历史等作为输入。\n请你根据提供的所有信息，按步骤执行以下任务：\n1. 输出客服在下一轮的最佳回复，要求输出格式为“客服:xxx”。\n2. 分析上述最佳回复中是否包含“方案列表”中的方案，输出方案名称或“无”。\n3. 查看对话历史的结尾部分，分析用户和客服是否就某个待执行方案达成一致，输出方案名称或“无”。\n4. 将以上信息整合成JSON格式输出：{\"Response\":\"[最佳回复]\", \"ResponseSolution\":\"[方案名称/无]\", \"DialogueAgreeSolution\":\"[方案名称/无]\"}\n\n## 你查询到的方案列表\n{\"name\": \"加急调度\", \"description\": \"当“订单骑手状态”信号值为“无骑手接单”时，即可向用户表示已经加急扩大调度骑手的范围\"}\n{\"name\": \"系统催单\", \"description\": \"符合催促履约的信号，即可向用户表示已经催促门店分拣/骑手配送\"}\n{\"name\": \"智能跟单\", \"description\": \"符合催促履约的信号，在结束对话时告知用户会持续跟进配送进度\"}\n{\"name\": \"取消订单\", \"description\": \"符合可取消订单的信号，用户同意后执行取消订单\"}\n{\"name\": \"操作赔付-优惠券-xx元\", \"description\": \"符合订单可赔付的信号，以优惠券形式给用户提供赔偿（优惠券仅有六个档位：3元、5元、8元、10元、15元、20元）\"}\n{\"name\": \"操作赔付-运费券-3元\", \"description\": \"符合订单可赔付的信号，以优惠券形式给用户提供赔偿（运费券仅有3元）\"}\n{\"name\": \"选择商品\", \"description\": \"指引用户选择要咨询的商品\"}\n{\"name\": \"发送送达图片\", \"description\": \"若用户反馈未找到包裹，可提供骑手送达时的现场照片，辅助用户寻找\"}\n{\"n...[截断]",
  "target": "{\"Response\": \"客服:是的，如您需要可以重新下单再次购买，请问还有什么诉求吗\", \"ResponseSolution\": \"无\", \"DialogueAgreeSolution\": \"无\"}"
}
```
