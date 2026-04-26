# 工具模块说明

本目录包含数据处理的核心工具模块，采用模块化设计，便于维护和扩展。

## 模块列表

### 1. parser.py - 数据解析器

**功能**：解析输入文件，支持多种格式

**核心类**：`DataParser`

**主要方法**：
```python
# 读取文件并逐行解析
for data in parser.read_file(file_path):
    # data 是字典格式: {'session_id', 'model_name', 'input_prompt', 'output'}
    pass

# 解析单行数据（自动识别 TSV 或 JSON）
data = DataParser.parse_line(line, line_number)
```

**支持格式**：
- TSV（Tab-Separated Values）- 推荐格式
- JSON（每行一条）

**使用示例**：
```python
from utils import DataParser

parser = DataParser()
for data in parser.read_file('input.txt'):
    print(data['session_id'], data['model_name'])
```

---

### 2. validator.py - 数据验证器

**功能**：验证数据完整性和有效性

**核心类**：`DataValidator`

**主要方法**：
```python
# 验证数据是否有效
is_valid, error_msg = validator.validate_data(data)

# 验证必需字段
is_valid, missing = DataValidator.validate_required_fields(data)

# 验证字段类型
is_valid, invalid = DataValidator.validate_field_types(data)
```

**验证规则**：
- 必需字段：session_id, model_name, input_prompt, output
- 字段类型：所有字段必须是字符串
- 字段非空：不能为空字符串

**使用示例**：
```python
from utils import DataValidator

validator = DataValidator()
is_valid, error_msg = validator.validate_data(data)
if not is_valid:
    print(f"验证失败: {error_msg}")
```

---

### 3. formatter.py - 数据格式化器

**功能**：清理和格式化文本数据

**核心类**：`DataFormatter`

**主要方法**：
```python
# 清理文本（去除多余空格、换行）
clean_text = DataFormatter.clean_text(text)

# 格式化为训练数据格式
training_data = formatter.format_to_training_data(data)
```

**清理规则**：
- 合并多余空格
- 合并多余换行（3+ 个换行 → 2 个）
- 去除首尾空白

**输出格式**：
```python
{
    "input": "格式化后的输入",
    "target": "格式化后的输出",
    "session_id": "会话ID",
    "metadata": {
        "model_name": "模型名称",
        "original_length": 原始长度
    }
}
```

**使用示例**：
```python
from utils import DataFormatter

formatter = DataFormatter()
training_data = formatter.format_to_training_data(raw_data)
```

---

### 4. statistics.py - 统计信息收集器

**功能**：收集和展示处理统计信息

**核心类**：`Statistics`

**主要方法**：
```python
# 添加统计
stats.add_total()           # 总数 +1
stats.add_passed()          # 通过数 +1
stats.add_filtered(reason)  # 过滤数 +1，记录原因

# 获取统计
total = stats.total
passed = stats.passed
filtered = stats.filtered
pass_rate = stats.get_pass_rate()

# 打印摘要
stats.print_summary(output_file)

# 导出 JSON
stats.export_to_json('stats.json')
```

**统计内容**：
- 总行数
- 通过行数
- 过滤行数
- 通过率
- 过滤原因分布（按类型统计）

**使用示例**：
```python
from utils import Statistics

stats = Statistics()
for data in all_data:
    stats.add_total()
    if valid:
        stats.add_passed()
    else:
        stats.add_filtered('数据无效')

stats.print_summary('output.jsonl')
```

---

## 模块化设计优势

### 1. 职责分离
- **parser**：只负责解析，不关心验证
- **validator**：只负责验证，不关心格式化
- **formatter**：只负责格式化，不关心统计
- **statistics**：只负责统计，不关心数据处理

### 2. 易于测试
每个模块都可以独立测试：
```python
# 测试解析器
data = DataParser.parse_line('xxx\tyyy\tzzz\twww')
assert data['session_id'] == 'xxx'

# 测试验证器
is_valid, _ = DataValidator.validate_required_fields({'session_id': 'x'})
assert not is_valid
```

### 3. 易于扩展
需要新功能时，只需修改对应模块：
- 支持新格式？修改 `parser.py`
- 新验证规则？修改 `validator.py`
- 新清理规则？修改 `formatter.py`
- 新统计维度？修改 `statistics.py`

### 4. 代码复用
其他脚本可以直接导入使用：
```python
# scripts/validate.py
from utils import DataParser, DataValidator

# scripts/sample.py
from utils import DataParser

# scripts/analyze.py
from utils import DataParser
```

---

## 使用模式

### 完整处理流程
```python
from utils import DataParser, DataValidator, DataFormatter, Statistics

# 初始化
parser = DataParser()
validator = DataValidator()
formatter = DataFormatter()
stats = Statistics()

# 处理数据
for data in parser.read_file('input.txt'):
    stats.add_total()

    # 验证
    is_valid, error = validator.validate_data(data)
    if not is_valid:
        stats.add_filtered(error)
        continue

    # 格式化
    formatted = formatter.format_to_training_data(data)
    results.append(formatted)
    stats.add_passed()

# 输出统计
stats.print_summary('output.jsonl')
```

### 只验证不处理
```python
from utils import DataParser, DataValidator

parser = DataParser()
validator = DataValidator()

for data in parser.read_file('input.txt'):
    is_valid, error = validator.validate_data(data)
    if not is_valid:
        print(f"行 {i}: {error}")
```

### 只解析不验证
```python
from utils import DataParser

parser = DataParser()
for data in parser.read_file('input.txt'):
    print(data['model_name'])
```

---

## 静态方法说明

所有模块都使用 `@staticmethod` 装饰器，这意味着：

**优点**：
- 不需要实例化即可使用
- 明确表示方法不依赖实例状态
- 便于作为工具函数使用

**使用方式**：
```python
# 方式 1：直接调用类方法
data = DataParser.parse_line(line)

# 方式 2：实例化后调用（效果相同）
parser = DataParser()
data = parser.parse_line(line)  # 也可以
```

**推荐**：简单工具函数用方式 1，需要保持状态的用方式 2（如 Statistics）。
