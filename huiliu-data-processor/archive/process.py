#!/usr/bin/env python3
"""
回流数据处理主脚本（重构版）
输入：txt 文件（TSV 或 JSON 格式）
输出：jsonl 文件（训练格式）
"""
import sys
import argparse
import json
from pathlib import Path

# 导入工具模块
from utils import DataParser, DataValidator, DataFormatter, Statistics
from filters import *

# 颜色定义
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


class DataProcessor:
    """数据处理器"""

    def __init__(self, config=None):
        self.config = config or {}
        self.stats = Statistics()
        self.parser = DataParser()
        self.validator = DataValidator()
        self.formatter = DataFormatter()

    def apply_filters(self, data):
        """
        应用所有过滤规则

        Args:
            data: 数据字典

        Returns:
            tuple: (passed, reason)
        """
        output = data['output']

        # 1. 验证数据有效性
        is_valid, error_msg = self.validator.validate_data(data)
        if not is_valid:
            return False, error_msg

        # 2. 检查非法方案
        if check_illegal_solution(output):
            return False, '非法工具/方案'

        # 3. 检查用户负面反馈
        if filter_negative_data(output):
            return False, '用户负面反馈'

        # 4. 检查过度承诺
        if check_overpromise(output):
            return False, '过度承诺'

        # 5. 检查过多口语词
        if check_excessive_modal_particles(output):
            return False, '过多口语词'

        # 6. 检查输出长度
        if not check_output_length(output):
            return False, '输出长度不合理'

        # 7. 检查重复回复
        if check_repetitive_response(output):
            return False, '重复回复'

        # 8. 检查退货/取回关键词
        if check_return_keywords(output):
            return False, '包含退货/取回关键词'

        # 9. 检查其他业务名称
        if check_other_business_keywords(output):
            return False, '包含其他业务名称'

        return True, None

    def process_file(self, input_file, output_file):
        """处理文件"""
        self.print_header(input_file, output_file)

        # 读取并处理数据
        results = []
        print(f"{YELLOW}⏳ 正在处理数据...{NC}")
        print()

        for i, data in enumerate(self.parser.read_file(input_file)):
            self.stats.add_total()

            # 显示进度
            if (i + 1) % 1000 == 0:
                print(f"  处理进度: {i + 1} 行 ({self.stats.passed} 通过, {self.stats.filtered} 过滤)")

            # 应用过滤规则
            passed, reason = self.apply_filters(data)

            if passed:
                # 格式化为训练数据
                formatted_data = self.formatter.format_to_training_data(data)
                results.append(formatted_data)
                self.stats.add_passed()
            else:
                self.stats.add_filtered(reason)

        # 写入输出文件
        self.write_output(output_file, results)

        # 显示统计信息
        self.stats.print_summary(output_file)

        # 导出统计信息
        stats_file = str(Path(output_file).with_suffix('.stats.json'))
        self.stats.export_to_json(stats_file)
        print(f"\n📈 统计信息已导出: {stats_file}")

    def print_header(self, input_file, output_file):
        """打印处理头部信息"""
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
        print(f"{GREEN}🔄 回流数据处理{NC}")
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
        print(f"📂 输入文件: {YELLOW}{input_file}{NC}")
        print(f"📁 输出文件: {YELLOW}{output_file}{NC}")
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
        print()

    def write_output(self, output_file, results):
        """写入输出文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='回流数据处理工具 - 将原始对话数据处理成训练数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.txt output.jsonl
  %(prog)s input.txt output.jsonl --config config.json
  %(prog)s input.txt output.jsonl --stats stats.json
        """
    )
    parser.add_argument('input_file', help='输入 txt 文件路径（TSV 或 JSON 格式）')
    parser.add_argument('output_file', help='输出 jsonl 文件路径')
    parser.add_argument('--config', help='配置文件路径（可选）')
    parser.add_argument('--stats', help='统计信息输出路径（可选）')

    args = parser.parse_args()

    # 检查输入文件
    if not Path(args.input_file).exists():
        print(f"{RED}❌ 输入文件不存在: {args.input_file}{NC}")
        sys.exit(1)

    # 加载配置
    config = {}
    if args.config and Path(args.config).exists():
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

    # 创建输出目录
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 处理数据
    try:
        processor = DataProcessor(config)
        processor.process_file(args.input_file, args.output_file)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  处理被用户中断{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ 处理失败: {e}{NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
