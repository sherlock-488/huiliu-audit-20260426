#!/usr/bin/env python3
"""
全局去重、优选和质量检查脚本

在标注前对数据进行处理：
1. 全局去重和优选（三层去重逻辑）
2. 质量检查（去重复、去垃圾回复）

输入: cleaned_data.jsonl（来自 process.py 的输出）
输出: deduped_data.jsonl（去重和质量检查后的数据）
"""
import json
import argparse
import sys
import re
from pathlib import Path

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


def check_repeat_sample(response, context, threshold=0.6, top_n=5):
    """
    检查是否与历史对话重复

    Args:
        response: 当前回复
        context: 对话历史（包含"客服:"前缀的行）
        threshold: 相似度阈值
        top_n: 比较最近的 N 条回复

    Returns:
        bool: True 表示重复，应该过滤
    """
    context_lines = context.split('\n')
    context_customer = []

    for text in context_lines:
        if text.startswith('客服:'):
            context_customer.append(text[3:])

    if response.startswith('客服:'):
        response = response[3:]

    reversed_context = context_customer[::-1]
    top_context = reversed_context[:top_n]

    max_similarity = 0
    for context_text in top_context:
        similarity = calculate_edit_distance(context_text, response)
        if similarity > max_similarity:
            max_similarity = similarity
        if max_similarity >= threshold:
            break

    return max_similarity >= threshold


def check_inner_repeat(response, threshold=0.5):
    """
    检查句内字符重复（如"谢谢谢谢谢"）

    Args:
        response: 回复文本
        threshold: 字符多样性阈值

    Returns:
        bool: True 表示有重复字符问题，应该过滤
    """
    response = response.replace('客服:', '')

    if len(response) >= 30:
        diversity = len(set(response)) * 1.0 / len(response)
        if diversity < threshold:
            return True

    return False


def filter_weiyi_dataset(data_list):
    """
    三层去重和优选逻辑

    1. 按 input + Response 分组
    2. 组内优选：优先保留 ResponseSolution 不为 '无' 的样本
    3. 按 Response + ResponseSolution 全局去重
    """
    # 第1层：按 input + Response 分组
    origin_datas_dic = {}
    for data in data_list:
        target_dict = json.loads(data['target']) if isinstance(data['target'], str) else data['target']
        key = data['input'] + target_dict.get('Response', '')

        if key not in origin_datas_dic:
            origin_datas_dic[key] = []
        origin_datas_dic[key].append(data)

    # 第2层：组内优选
    origin_datas = []
    for key, value in origin_datas_dic.items():
        if not value:
            continue

        # 按 target 字符串长度倒序排列
        sorted_value = sorted(value, key=lambda x: len(x['target']), reverse=True)

        # 筛选出方案不为 '无' 的数据
        tmp_datas = []
        for da in sorted_value:
            target_dict = json.loads(da['target']) if isinstance(da['target'], str) else da['target']
            if target_dict.get('ResponseSolution') != '无':
                tmp_datas.append(da)

        if len(tmp_datas) == 0:
            origin_datas.append(sorted_value[0])
        else:
            origin_datas.extend(tmp_datas)

    # 第3层：按 Response + ResponseSolution 全局去重
    unique_datas_dic = {}
    for data in origin_datas:
        target_dict = json.loads(data['target']) if isinstance(data['target'], str) else data['target']
        key = target_dict.get('Response', '') + target_dict.get('ResponseSolution', '')
        unique_datas_dic[key] = data

    return list(unique_datas_dic.values())


def main():
    parser = argparse.ArgumentParser(description='去重、优选和质量检查')
    parser.add_argument('input_file', help='输入文件路径（cleaned_data.jsonl）')
    parser.add_argument('output_file', help='输出文件路径')
    parser.add_argument('--skip-dedup', action='store_true', help='跳过去重步骤')
    parser.add_argument('--skip-quality', action='store_true', help='跳过质量检查步骤')

    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_path = Path(args.output_file)

    if not input_path.exists():
        print(f"{RED}❌ 输入文件不存在: {input_path}{NC}")
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

    original_count = len(data_list)

    # 步骤1：全局去重和优选
    if not args.skip_dedup:
        print(f"\n{BLUE}🔄 执行全局去重和优选...{NC}")
        data_list = filter_weiyi_dataset(data_list)
        dedup_count = len(data_list)
        dedup_rate = (1 - dedup_count / original_count) * 100 if original_count else 0
        print(f"{GREEN}✅ 去重完成:{NC}")
        print(f"  - 去重前: {original_count} 条")
        print(f"  - 去重后: {dedup_count} 条")
        print(f"  - 去重率: {dedup_rate:.1f}%")
    else:
        print(f"\n{YELLOW}⏭️  跳过去重步骤{NC}")
        dedup_count = original_count

    # 步骤2：质量检查
    if not args.skip_quality:
        print(f"\n{BLUE}✅ 执行质量检查...{NC}")
        filtered_data = []
        quality_stats = {
            'repeat_sample': 0,
            'inner_repeat': 0,
            'passed': 0
        }

        for idx, data in enumerate(data_list):
            target_dict = json.loads(data['target']) if isinstance(data['target'], str) else data['target']
            response = target_dict.get('Response', '')
            context = data.get('context', '')

            # 检查与历史对话重复
            if check_repeat_sample(response, context):
                quality_stats['repeat_sample'] += 1
                continue

            # 检查句内字符重复
            if check_inner_repeat(response):
                quality_stats['inner_repeat'] += 1
                continue

            filtered_data.append(data)
            quality_stats['passed'] += 1

            if (idx + 1) % 5000 == 0:
                print(f"  已处理: {idx + 1}/{dedup_count}")

        data_list = filtered_data
        quality_rate = (1 - len(filtered_data) / dedup_count) * 100 if dedup_count else 0

        print(f"{GREEN}✅ 质量检查完成:{NC}")
        print(f"  - 检查前: {dedup_count} 条")
        print(f"  - 检查后: {len(filtered_data)} 条")
        print(f"  - 过滤率: {quality_rate:.1f}%")
        print(f"  - 过滤原因:")
        print(f"    - 与历史对话重复: {quality_stats['repeat_sample']}")
        print(f"    - 句内字符重复: {quality_stats['inner_repeat']}")
    else:
        print(f"\n{YELLOW}⏭️  跳过质量检查步骤{NC}")

    # 写入输出
    print(f"\n{BLUE}💾 写入输出文件...{NC}")
    try:
        with open(output_path, 'w') as f:
            for data in data_list:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
        print(f"{GREEN}✅ 输出完成: {output_path}{NC}")
    except Exception as e:
        print(f"{RED}❌ 写入文件失败: {e}{NC}")
        sys.exit(1)

    # 总结
    print(f"\n{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"{GREEN}📊 处理总结{NC}")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
    print(f"原始数据: {original_count:,} 条")
    print(f"最终数据: {len(data_list):,} 条")
    print(f"总过滤率: {(1 - len(data_list) / original_count) * 100:.1f}%")
    print(f"保留率: {len(data_list) / original_count * 100:.1f}%")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")


if __name__ == '__main__':
    main()
