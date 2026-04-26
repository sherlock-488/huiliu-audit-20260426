# 去重和质量检查脚本

## 概述

`dedup_and_quality.py` 是在标注前对数据进行全局去重、优选和质量检查的脚本。

**输入**：`cleaned_data.jsonl`（来自 `process.py` 的输出）  
**输出**：`deduped_data.jsonl`（去重和质量检查后的数据）

## 处理流程

### 第1层：按 input + Response 分组

根据用户问题（input）和模型回复（Response）分组，找出所有"问题相同、回复相同"的数据。

```
input="怎么退货" + Response="可以申请退款" → [data_a, data_b, data_c]
input="怎么退货" + Response="请提供订单号" → [data_d, data_e]
```

### 第2层：组内优选

对每个分组内的数据进行优选：

1. **优先保留有方案的数据**：`ResponseSolution != '无'` 优于 `ResponseSolution == '无'`
2. **其次按 target 长度**：同等情况下，target 更长（信息更完整）的优先

```
组内数据：
- data_a: ResponseSolution='无'（过滤）
- data_b: ResponseSolution='小象单商品退款-50%'（保留）✅
- data_c: ResponseSolution='小象整单申请退款'（保留）✅
```

### 第3层：全局去重

按 `Response + ResponseSolution` 进行全局去重，确保最终数据集中没有"回复和方案完全相同"的重复。

```
data_b: Response="可以申请退款" + ResponseSolution="小象单商品退款-50%"
data_c: Response="可以申请退款" + ResponseSolution="小象单商品退款-50%"

结果：只保留 data_c（后来的覆盖前面的）
```

### 第4层：质量检查

#### 检查1：与历史对话重复

检测模型的回复是否与最近的历史对话过于相似（可能是复制粘贴）。

**原理**：计算编辑距离相似度，与最近 5 条历史回复比较。

**阈值**：相似度 >= 0.6 则过滤

```
历史对话：
客服：可以申请退款
客服：请提供订单号
客服：我来帮您查一下

当前 Response："我来帮您查一下"

对比：与"我来帮您查一下" 相似度 = 1.0 ✅ 重复！过滤
```

#### 检查2：句内字符重复

检测单条回复内部是否有过多重复字符（如"哈哈哈哈哈"、"谢谢谢谢谢"）。

**条件**：
- 回复长度 >= 30 字符
- 字符多样性 < 0.5（不重复字符数 / 总字符数）

```
response = "谢谢谢谢谢谢谢谢谢谢谢谢谢谢谢谢谢谢谢谢" (20个字)
字符多样性 = 1 / 20 = 0.05 < 0.5 ✅ 过滤

response = "我很抱歉为您造成了困扰，请您放心，我们会尽快为您处理这个问题" (30个字)
字符多样性 = 25 / 30 ≈ 0.83 > 0.5 ✅ 通过
```

## 使用方法

### 基本用法

```bash
python3 dedup_and_quality.py cleaned_data.jsonl deduped_data.jsonl
```

### 跳过特定步骤

```bash
# 只进行质量检查，跳过去重
python3 dedup_and_quality.py cleaned_data.jsonl deduped_data.jsonl --skip-dedup

# 只进行去重，跳过质量检查
python3 dedup_and_quality.py cleaned_data.jsonl deduped_data.jsonl --skip-quality
```

### 在 Pipeline 中的位置

在 `huiliu-pipeline/pipeline.sh` 中，该脚本在步骤3执行：

```
步骤1：查询 AIDA Workflow 数据
步骤2：数据清洗和过滤 (process.py)
步骤3：去重和质量检查 (dedup_and_quality.py) ← 新增
步骤4：构建标注数据集 (annotate.py)
步骤5：模型推理标注（可选）
步骤6：过滤推理结果（可选）
```

## 输出示例

```
📖 读取数据中...
✅ 读取完成: 83,011 条数据

🔄 执行全局去重和优选...
✅ 去重完成:
  - 去重前: 83,011 条
  - 去重后: 19,662 条
  - 去重率: 76.3%

✅ 执行质量检查...
  已处理: 5000/19662
  已处理: 10000/19662
  已处理: 15000/19662
✅ 质量检查完成:
  - 检查前: 19,662 条
  - 检查后: 18,945 条
  - 过滤率: 3.6%
  - 过滤原因:
    - 与历史对话重复: 523
    - 句内字符重复: 194

💾 写入输出文件...
✅ 输出完成: /path/to/deduped_data.jsonl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 处理总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
原始数据: 83,011 条
最终数据: 18,945 条
总过滤率: 77.2%
保留率: 22.8%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 性能指标

| 业务 | 原始数据 | 去重后 | 质量检查后 | 最终保留率 |
|------|---------|--------|-----------|----------|
| 小象超市客服 | 83,011 | 19,662 | 18,945 | 22.8% |

## 相关函数

### `filter_weiyi_dataset(data_list)`

执行三层去重和优选逻辑。

### `calculate_edit_distance(str1, str2)`

计算两个字符串的编辑距离相似度（0-1 之间，1 表示完全相同）。

### `check_repeat_sample(response, context, threshold=0.6, top_n=5)`

检查是否与历史对话重复。

### `check_inner_repeat(response, threshold=0.5)`

检查句内字符重复。

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `check_repeat_sample.threshold` | 0.6 | 与历史对话重复的相似度阈值 |
| `check_repeat_sample.top_n` | 5 | 比较最近的 N 条历史回复 |
| `check_inner_repeat.threshold` | 0.5 | 字符多样性阈值 |

## 注意事项

1. **去重逻辑是不可逆的**：一旦去重，相同的数据会被永久删除。建议在处理前备份原始数据。

2. **质量检查的阈值可调**：如果觉得过滤太严格或太宽松，可以修改脚本中的阈值参数。

3. **性能考虑**：对于大规模数据（100w+ 条），编辑距离计算可能较慢。如果需要优化，可以考虑：
   - 使用更高效的相似度算法（如 n-gram）
   - 并行处理

4. **数据格式要求**：输入数据必须是 JSONL 格式，每行一个完整的 JSON 对象，包含以下字段：
   - `input`：用户问题
   - `target`：包含 Response 和 ResponseSolution 的 JSON 字符串或字典
   - `context`：对话历史
   - `session_id`：会话 ID
