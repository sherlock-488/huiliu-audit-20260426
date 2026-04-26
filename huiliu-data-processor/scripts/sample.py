#!/usr/bin/env python3
"""
数据抽样脚本
从大文件中随机抽取样本
"""
import sys
import random
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import DataParser


def sample_file(input_file, output_file, sample_size=1000, random_seed=42):
    """抽样数据"""
    print(f"📂 输入文件: {input_file}")
    print(f"📁 输出文件: {output_file}")
    print(f"📊 抽样数量: {sample_size}")
    print("━" * 60)

    random.seed(random_seed)
    parser = DataParser()

    # 读取所有数据
    print("⏳ 读取数据...")
    all_data = list(parser.read_file(input_file))
    total = len(all_data)

    print(f"✅ 共读取 {total} 行数据")

    # 抽样
    if sample_size >= total:
        print(f"⚠️  抽样数量大于总数，将输出全部数据")
        sampled_data = all_data
    else:
        print(f"🎲 随机抽样 {sample_size} 行...")
        sampled_data = random.sample(all_data, sample_size)

    # 写入文件
    print(f"💾 写入输出文件...")
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入表头
        f.write("session_id\tmodel_name\tinput_prompt\toutput\n")
        # 写入数据
        for data in sampled_data:
            f.write(f"{data['session_id']}\t{data['model_name']}\t{data['input_prompt']}\t{data['output']}\n")

    print()
    print(f"✅ 抽样完成！")
    print(f"📁 输出文件: {output_file}")
    print(f"📊 抽样行数: {len(sampled_data)}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 sample.py <输入文件> <输出文件> [抽样数量=1000]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    sample_size = int(sys.argv[3]) if len(sys.argv) > 3 else 1000

    sample_file(input_file, output_file, sample_size)
