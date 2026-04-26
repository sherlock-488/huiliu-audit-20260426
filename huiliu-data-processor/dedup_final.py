#!/usr/bin/env python3
"""
最终训练数据重复度筛选脚本

对已生成的训练数据进行重复度检测和去重
支持多种相似度计算方法

输入: 训练数据 (JSONL 格式)
输出: 去重后的训练数据 (JSONL 格式)
"""
import json
import argparse
import sys
from pathlib import Path
from collections import defaultdict

# 颜色定义
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def calculate_edit_distance(str1, str2):
    """
    计算两个字符串的编辑距离相似度
    返回值: 0-1 之间，1 表示完全相同
    """
    m = len(str1)
    n = len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j - 1], dp[i][j - 1], dp[i - 1][j]) + 1

    return 1 - (dp[m][n] / max(m, n))


def calculate_jaccard_similarity(str1, str2):
    """
    计算 Jaccard 相似度（基于字符集）
    返回值: 0-1 之间，1 表示完全相同
    """
    set1 = set(str1)
    set2 = set(str2)

    if not set1 and not set2:
        return 1.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0


def calculate_cosine_similarity(str1, str2):
    """
    计算余弦相似度（基于字符频率）
    返回值: 0-1 之间，1 表示完全相同
    """
    from collections import Counter
    import math

    counter1 = Counter(str1)
    counter2 = Counter(str2)

    all_chars = set(counter1.keys()) | set(counter2.keys())

    if not all_chars:
        return 1.0

    # 计算点积
    dot_product = sum(counter1.get(char, 0) * counter2.get(char, 0) for char in all_chars)

    # 计算向量长度
    len1 = math.sqrt(sum(count ** 2 for count in counter1.values()))
    len2 = math.sqrt(sum(count ** 2 for count in counter2.values()))

    if len1 == 0 or len2 == 0:
        return 0

    return dot_product / (len1 * len2)


def get_similarity_func(method):
    """获取相似度计算函数"""
    methods = {
        'edit': calculate_edit_distance,
        'jaccard': calculate_jaccard_similarity,
        'cosine': calculate_cosine_similarity,
    }
    return methods.get(method, calculate_edit_distance)


def check_duplicates(data_list, key_field, threshold=0.8, method='edit', top_n=None):
    """
    检查数据重复度

    Args:
        data_list: 数据列表
        key_field: 用于比较的字段名（如 'Response'、'input'）
        threshold: 相似度阈值
        method: 相似度计算方法 ('edit', 'jaccard', 'cosine')
        top_n: 只保留相似度最高的 N 条（None 表示保留所有）

    Returns:
        (去重后的数据, 统计信息)
    """
    similarity_func = get_similarity_func(method)

    # 按 key_field 分组
    groups = defaultdict(list)
    for idx, data in enumerate(data_list):
        # 支持嵌套字段（如 'target.Response'）
        if '.' in key_field:
            field_path = key_field.split('.')
            value = data
            for field in field_path:
                if isinstance(value, str):
                    value = json.loads(value)
                value = value.get(field, '')
        else:
            value = data.get(key_field, '')

        groups[value].append((idx, data))

    # 去重处理
    unique_data = []
    duplicates_removed = 0

    for value, group in groups.items():
        if len(group) == 1:
            unique_data.append(group[0][1])
        else:
            # 多条相同数据
            if top_n:
                # 保留前 top_n 条
                unique_data.extend([item[1] for item in group[:top_n]])
                duplicates_removed += len(group) - top_n
            else:
                # 保留第一条
                unique_data.append(group[0][1])
                duplicates_removed += len(group) - 1

    stats = {
        'original': len(data_list),
        'unique': len(unique_data),
        'duplicates_removed': duplicates_removed,
        'method': method,
        'threshold': threshold,
    }

    return unique_data, stats


def check_similarity_duplicates(data_list, key_field, threshold=0.8, method='edit'):
    """
    基于相似度的去重（不仅仅是完全相同）

    Args:
        data_list: 数据列表
        key_field: 用于比较的字段名
        threshold: 相似度阈值
        method: 相似度计算方法

    Returns:
        (去重后的数据, 统计信息)
    """
    similarity_func = get_similarity_func(method)

    # 提取所有值
    values = []
    for data in data_list:
        if '.' in key_field:
            field_path = key_field.split('.')
            value = data
            for field in field_path:
                if isinstance(value, str):
                    value = json.loads(value)
                value = value.get(field, '')
        else:
            value = data.get(key_field, '')
        values.append(value)

    # 标记要删除的索引
    to_remove = set()

    for i in range(len(data_list)):
        if i in to_remove:
            continue

        for j in range(i + 1, len(data_list)):
            if j in to_remove:
                continue

            similarity = similarity_func(values[i], values[j])

            if similarity >= threshold:
                # 保留索引较小的，删除索引较大的
                to_remove.add(j)

    # 保留未被标记删除的数据
    unique_data = [data for idx, data in enumerate(data_list) if idx not in to_remove]

    stats = {
        'original': len(data_list),
        'unique': len(unique_data),
        'duplicates_removed': len(to_remove),
        'method': method,
        'threshold': threshold,
    }

    return unique_data, stats


def main():
    parser = argparse.ArgumentParser(
        description='最终训练数据重复度筛选',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完全相同去重
  %(prog)s data.jsonl output.jsonl --key-field Response

  # 基于相似度去重（编辑距离）
  %(prog)s data.jsonl output.jsonl --key-field Response --similarity --threshold 0.9

  # 基于相似度去重（Jaccard）
  %(prog)s data.jsonl output.jsonl --key-field Response --similarity --method jaccard --threshold 0.8

  # 支持嵌套字段
  %(prog)s data.jsonl output.jsonl --key-field target.Response --similarity
        """
    )
    parser.add_argument('input_file', help='输入文件路径（JSONL 格式）')
    parser.add_argument('output_file', help='输出文件路径')
    parser.add_argument('--key-field', default='Response', help='用于去重的字段名（默认: Response）')
    parser.add_argument('--similarity', action='store_true', help='使用相似度去重而非完全相同')
    parser.add_argument('--method', choices=['edit', 'jaccard', 'cosine'], default='edit',
                        help='相似度计算方法（默认: edit）')
    parser.add_argument('--threshold', type=float, default=0.8,
                        help='相似度阈值，0-1 之间（默认: 0.8）')
    parser.add_argument('--top-n', type=int, help='完全相同时保留前 N 条')

    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_path = Path(args.output_file)

    if not input_path.exists():
        print(f"{RED}❌ 输入文件不存在: {input_path}{NC}")
        sys.exit(1)

    if args.threshold < 0 or args.threshold > 1:
        print(f"{RED}❌ 相似度阈值必须在 0-1 之间{NC}")
        sys.exit(1)

    # 读取数据
    print(f"{BLUE}📖 读取数据中...{NC}")
    data_list = []
    try:
        with open(input_path) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    data_list.append(data)
                except json.JSONDecodeError as e:
                    print(f"{YELLOW}⚠️  第 {line_num} 行 JSON 解析失败: {e}{NC}")
                    continue
    except Exception as e:
        print(f"{RED}❌ 读取文件失败: {e}{NC}")
        sys.exit(1)

    print(f"{GREEN}✅ 读取完成: {len(data_list)} 条数据{NC}")

    # 执行去重
    print(f"\n{BLUE}🔄 执行重复度筛选...{NC}")
    print(f"  字段: {args.key_field}")
    print(f"  方法: {'相似度' if args.similarity else '完全相同'}")
    if args.similarity:
        print(f"  算法: {args.method}")
        print(f"  阈值: {args.threshold}")
    print()

    if args.similarity:
        unique_data, stats = check_similarity_duplicates(
            data_list,
            args.key_field,
            threshold=args.threshold,
            method=args.method
        )
    else:
        unique_data, stats = check_duplicates(
            data_list,
            args.key_field,
            threshold=args.threshold,
            method=args.method,
            top_n=args.top_n
        )

    # 打印统计信息
    print(f"{GREEN}✅ 筛选完成:{NC}")
    print(f"  - 原始数据: {stats['original']:,} 条")
    print(f"  - 保留数据: {stats['unique']:,} 条")
    print(f"  - 移除数据: {stats['duplicates_removed']:,} 条")
    print(f"  - 保留率: {stats['unique'] / stats['original'] * 100:.1f}%")
    print(f"  - 去重率: {stats['duplicates_removed'] / stats['original'] * 100:.1f}%")

    # 写入输出
    print(f"\n{BLUE}💾 写入输出文件...{NC}")
    try:
        with open(output_path, 'w') as f:
            for data in unique_data:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        print(f"{GREEN}✅ 输出完成: {output_path}{NC}")
    except Exception as e:
        print(f"{RED}❌ 写入文件失败: {e}{NC}")
        sys.exit(1)


if __name__ == '__main__':
    main()
