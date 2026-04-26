# 工具脚本说明

本目录包含数据处理的辅助工具脚本。

## 📋 脚本列表

### 1. validate.py - 格式验证
**功能**：快速验证输入文件格式是否正确

**用法**：
```bash
python3 validate.py <输入文件>
```

**输出**：
- ✅ 格式正确的行数
- ❌ 格式错误的行数及错误信息

---

### 2. sample.py - 数据抽样
**功能**：从大文件中随机抽取指定数量的样本

**用法**：
```bash
python3 sample.py <输入文件> <输出文件> <样本数量>
```

**示例**：
```bash
# 从大文件中抽取 1000 条样本
python3 sample.py large_data.txt sample_1000.txt 1000
```

---

### 3. analyze.py - 数据分析
**功能**：分析原始数据的基本统计信息

**用法**：
```bash
python3 analyze.py <输入文件>
```

**输出**：
- 📊 总行数
- 🤖 模型分布（Top 10）
- 📏 输入长度统计（最小/最大/平均/中位数）
- 📏 输出长度统计（最小/最大/平均/中位数）

**示例输出**：
```
📂 分析文件: data.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ 读取数据...
  已读取: 1000 行

✅ 分析完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 总行数: 1,234

🤖 模型分布:
  - model_a: 800 (64.8%)
  - model_b: 434 (35.2%)

📏 输入长度统计:
  - 最小: 120 字符
  - 最大: 5,890 字符
  - 平均: 1,234 字符
  - 中位数: 1,100 字符

📏 输出长度统计:
  - 最小: 50 字符
  - 最大: 2,000 字符
  - 平均: 456 字符
  - 中位数: 400 字符
```

---

### 4. analyze_tools.py - 工具分布统计（新增）
**功能**：统计过滤后 JSONL 文件中的工具使用分布

**用法**：
```bash
python3 analyze_tools.py <输出文件.jsonl>
```

**输出**：
- 📊 总行数和解析失败数
- 🔧 ResponseSolution 工具分布
- 🤝 DialogueAgreeSolution 工具分布
- 📈 总体工具分布（Top 20）
- 🎯 有效工具分布（排除"无"）

**示例输出**：
```
📂 分析文件: output.jsonl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ 读取数据...
  已处理: 1,000 行
  已处理: 2,000 行

✅ 分析完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 总行数: 2,345
❌ 解析失败: 0

🔧 ResponseSolution 工具分布:
  - 小象超市商品退款                                          :    800 (34.11%)
  - 小象超市赔付                                            :    650 (27.72%)
  - 无                                                 :    895 (38.17%)

🤝 DialogueAgreeSolution 工具分布:
  - 无                                                 :  1,800 (76.76%)
  - 小象超市赔付                                            :    545 (23.24%)

📈 总体工具分布（Top 20）:
  - 无                                                 :  2,695 (57.46%)
  - 小象超市赔付                                            :  1,195 (25.48%)
  - 小象超市商品退款                                          :    800 (17.06%)

🎯 有效工具分布（排除'无'）:
  有效工具调用总数: 1,995
  - 小象超市赔付                                            :  1,195 (59.90%)
  - 小象超市商品退款                                          :    800 (40.10%)
```

**应用场景**：
- 了解过滤后数据中哪些工具使用最频繁
- 检查工具分布是否符合业务预期
- 为模型训练提供工具使用统计数据
- 发现异常工具调用（如果有）

---

## 🔄 典型工作流程

### 场景 1：处理小文件（< 10MB）
```bash
# 1. 验证格式
python3 validate.py input.txt

# 2. 分析原始数据
python3 analyze.py input.txt

# 3. 处理数据
cd .. && python3 process.py input.txt output.jsonl

# 4. 分析工具分布
python3 scripts/analyze_tools.py output.jsonl
```

### 场景 2：处理大文件（> 100MB）
```bash
# 1. 先抽样测试
python3 sample.py large_data.txt sample_1000.txt 1000

# 2. 分析样本
python3 analyze.py sample_1000.txt

# 3. 处理样本验证流程
cd .. && python3 process.py sample_1000.txt output_sample.jsonl

# 4. 分析样本工具分布
python3 scripts/analyze_tools.py output_sample.jsonl

# 5. 确认无误后处理完整数据
python3 process.py large_data.txt output_full.jsonl

# 6. 分析完整数据工具分布
python3 scripts/analyze_tools.py output_full.jsonl
```

### 场景 3：批量处理多个文件
```bash
# 批量处理并分析
for file in data/*.txt; do
  output="output/$(basename $file .txt).jsonl"
  python3 process.py "$file" "$output"
  python3 scripts/analyze_tools.py "$output"
done
```

---

## 📊 工具分布分析说明

### ResponseSolution vs DialogueAgreeSolution

- **ResponseSolution**：客服当前回合使用的工具
- **DialogueAgreeSolution**：用户同意的方案（通常是之前客服提出的方案）

### "无" 的含义

- 当字段值为 `null`、空字符串或不存在时，统计为 "无"
- "无" 表示该回合没有工具调用或方案同意

### 总体工具分布

- 统计了 `ResponseSolution` 和 `DialogueAgreeSolution` 两个字段的所有值
- 注意："无" 会被统计两次（每行都有两个字段）

### 有效工具分布

- 排除 "无" 后的工具分布
- 更清晰地展示实际使用的工具频率

---

## 💡 使用建议

1. **处理前先抽样**：大文件建议先抽取 1000-5000 条样本测试
2. **关注工具分布**：处理完成后务必检查工具分布是否合理
3. **异常检测**：如果某个工具频率异常高/低，可能需要检查过滤规则
4. **对比分析**：可以对比处理前后的工具分布变化

---

## 🔧 故障排查

| 问题 | 解决方案 |
|------|---------|
| `FileNotFoundError` | 检查文件路径是否正确 |
| `JSONDecodeError` | 检查 JSONL 格式是否正确（每行一个 JSON） |
| `KeyError: 'target'` | 确保是处理后的 JSONL 文件，不是原始 txt |
| 解析失败率高 | 检查数据格式，可能需要调整脚本 |
| 工具分布异常 | 检查过滤规则是否过于严格/宽松 |
