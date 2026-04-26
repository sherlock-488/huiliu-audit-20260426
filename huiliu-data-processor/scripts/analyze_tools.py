#!/usr/bin/env python3
"""
工具分布统计脚本
统计过滤后 JSONL 文件中的工具使用分布

用法:
    python3 analyze_tools.py <输入文件.jsonl>

输出:
    - ResponseSolution 工具分布
    - DialogueAgreeSolution 工具分布
    - 总体工具分布
    - Top 10 高频工具
"""
import sys
import json
from collections import Counter
from pathlib import Path


def analyze_tools(file_path):
    """分析工具分布"""
    print(f"📂 分析文件: {file_path}")
    print("━" * 80)

    # 统计数据结构
    stats = {
        "total": 0,
        "ResponseSolution": Counter(),
        "DialogueAgreeSolution": Counter(),
        "all_tools": Counter(),
        "parse_errors": 0
    }

    print("⏳ 读取数据...")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                # 解析外层 JSON
                data = json.loads(line)
                stats["total"] += 1

                # 获取 target 字段
                target_raw = data.get('target', '{}')

                # 解析内层 target 字符串
                if isinstance(target_raw, str):
                    target_obj = json.loads(target_raw)
                else:
                    target_obj = target_raw

                # 检查两个字段
                fields = ["ResponseSolution", "DialogueAgreeSolution"]

                for field in fields:
                    val = target_obj.get(field, "无")
                    if val is None:
                        val = "无"

                    # 记录字段分布
                    stats[field][val] += 1

                    # 记录总分布
                    stats["all_tools"][val] += 1

                # 进度提示
                if stats["total"] % 1000 == 0:
                    print(f"  已处理: {stats['total']:,} 行")

            except json.JSONDecodeError as e:
                stats["parse_errors"] += 1
                print(f"  ⚠️  行 {line_num} 解析失败: {e}")
            except Exception as e:
                stats["parse_errors"] += 1
                print(f"  ⚠️  行 {line_num} 处理失败: {e}")

    print()
    print("✅ 分析完成")
    print("━" * 80)

    # 输出统计结果
    print_statistics(stats)


def print_statistics(stats):
    """打印统计结果"""
    total = stats["total"]

    print(f"📊 总行数: {total:,}")
    print(f"❌ 解析失败: {stats['parse_errors']:,}")
    print()

    # ResponseSolution 分布
    print("🔧 ResponseSolution 工具分布:")
    print_tool_distribution(stats["ResponseSolution"], total)
    print()

    # DialogueAgreeSolution 分布
    print("🤝 DialogueAgreeSolution 工具分布:")
    print_tool_distribution(stats["DialogueAgreeSolution"], total)
    print()

    # 总体分布（去重"无"）
    print("📈 总体工具分布（Top 20）:")
    all_tools = stats["all_tools"].copy()
    # 注意："无" 会被统计两次（每行都有两个字段），这里展示原始统计
    print_tool_distribution(all_tools, total * 2, top_n=20)  # total * 2 因为有两个字段
    print()

    # 有效工具（排除"无"）
    print("🎯 有效工具分布（排除'无'）:")
    valid_tools = {k: v for k, v in all_tools.items() if k != "无"}
    valid_total = sum(valid_tools.values())
    print(f"  有效工具调用总数: {valid_total:,}")
    print_tool_distribution(Counter(valid_tools), valid_total, top_n=20)


def print_tool_distribution(counter, total, top_n=10):
    """打印工具分布"""
    if not counter:
        print("  （无数据）")
        return

    for tool, count in counter.most_common(top_n):
        percentage = count / total * 100 if total > 0 else 0
        # 格式化工具名称（截断过长的）
        tool_display = tool if len(tool) <= 50 else tool[:47] + "..."
        print(f"  - {tool_display:50s}: {count:6,} ({percentage:5.2f}%)")

    if len(counter) > top_n:
        remaining = len(counter) - top_n
        remaining_count = sum(count for tool, count in counter.most_common()[top_n:])
        print(f"  ... 还有 {remaining} 个工具，共 {remaining_count:,} 次调用")


def export_to_json(stats, output_file):
    """导出统计结果到 JSON 文件"""
    export_data = {
        "total": stats["total"],
        "parse_errors": stats["parse_errors"],
        "ResponseSolution": dict(stats["ResponseSolution"].most_common()),
        "DialogueAgreeSolution": dict(stats["DialogueAgreeSolution"].most_common()),
        "all_tools": dict(stats["all_tools"].most_common())
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"📁 统计结果已导出到: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 analyze_tools.py <输入文件.jsonl> [--export <输出JSON>]")
        print()
        print("示例:")
        print("  python3 analyze_tools.py output.jsonl")
        print("  python3 analyze_tools.py output.jsonl --export stats.json")
        sys.exit(1)

    input_file = sys.argv[1]

    # 检查文件是否存在
    if not Path(input_file).exists():
        print(f"❌ 文件不存在: {input_file}")
        sys.exit(1)

    # 分析工具分布
    analyze_tools(input_file)

    # 如果指定了导出选项
    if '--export' in sys.argv:
        try:
            export_index = sys.argv.index('--export')
            output_file = sys.argv[export_index + 1]
            # 重新读取数据以导出
            print()
            print("━" * 80)
            print("📤 导出统计结果...")
            # TODO: 实现导出功能（需要重新读取或保存 stats）
            print("⚠️  导出功能待实现")
        except (IndexError, ValueError):
            print("⚠️  --export 选项需要指定输出文件名")
