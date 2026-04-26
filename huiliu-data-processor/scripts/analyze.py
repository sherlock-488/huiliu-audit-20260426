#!/usr/bin/env python3
"""
数据分析脚本
分析数据的基本统计信息
"""
import sys
import json
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import DataParser


def analyze_file(file_path):
    """分析文件"""
    print(f"📂 分析文件: {file_path}")
    print("━" * 60)

    parser = DataParser()

    total = 0
    model_names = []
    input_lengths = []
    output_lengths = []

    print("⏳ 读取数据...")
    for data in parser.read_file(file_path):
        total += 1
        model_names.append(data['model_name'])
        input_lengths.append(len(data['input_prompt']))
        output_lengths.append(len(data['output']))

        if total % 1000 == 0:
            print(f"  已读取: {total} 行")

    print()
    print("✅ 分析完成")
    print("━" * 60)
    print(f"📊 总行数: {total:,}")
    print()

    # 模型分布
    print("🤖 模型分布:")
    model_counter = Counter(model_names)
    for model, count in model_counter.most_common(10):
        percentage = count / total * 100
        print(f"  - {model}: {count:,} ({percentage:.1f}%)")
    if len(model_counter) > 10:
        print(f"  ... 还有 {len(model_counter) - 10} 个模型")
    print()

    # 长度统计
    print("📏 输入长度统计:")
    print(f"  - 最小: {min(input_lengths):,} 字符")
    print(f"  - 最大: {max(input_lengths):,} 字符")
    print(f"  - 平均: {sum(input_lengths)/len(input_lengths):,.0f} 字符")
    print(f"  - 中位数: {sorted(input_lengths)[len(input_lengths)//2]:,} 字符")
    print()

    print("📏 输出长度统计:")
    print(f"  - 最小: {min(output_lengths):,} 字符")
    print(f"  - 最大: {max(output_lengths):,} 字符")
    print(f"  - 平均: {sum(output_lengths)/len(output_lengths):,.0f} 字符")
    print(f"  - 中位数: {sorted(output_lengths)[len(output_lengths)//2]:,} 字符")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 analyze.py <输入文件>")
        sys.exit(1)

    analyze_file(sys.argv[1])
