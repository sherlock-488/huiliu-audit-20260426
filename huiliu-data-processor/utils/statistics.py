#!/usr/bin/env python3
"""
统计模块
收集和展示处理统计信息
"""

# 颜色定义
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


class Statistics:
    """统计信息收集器"""

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.filtered = 0
        self.reasons = {}

    def add_total(self, count=1):
        """增加总数"""
        self.total += count

    def add_passed(self, count=1):
        """增加通过数"""
        self.passed += count

    def add_filtered(self, reason):
        """增加过滤数并记录原因"""
        self.filtered += 1
        if reason not in self.reasons:
            self.reasons[reason] = 0
        self.reasons[reason] += 1

    def get_pass_rate(self):
        """获取通过率"""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100

    def print_summary(self, output_file=None):
        """打印统计摘要"""
        pass_rate = self.get_pass_rate()

        print()
        print(f"{GREEN}✅ 处理完成！{NC}")
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
        print(f"{GREEN}📊 处理统计{NC}")
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
        print(f"输入总行数: {YELLOW}{self.total:,}{NC}")
        print(f"✅ 通过过滤: {GREEN}{self.passed:,}{NC} ({pass_rate:.1f}%)")
        print(f"❌ 被过滤: {RED}{self.filtered:,}{NC} ({100 - pass_rate:.1f}%)")
        print()

        if self.reasons:
            print(f"过滤原因分布:")
            # 按数量排序
            sorted_reasons = sorted(self.reasons.items(), key=lambda x: x[1], reverse=True)
            for reason, count in sorted_reasons:
                percentage = (count / self.filtered * 100) if self.filtered > 0 else 0
                print(f"  - {reason}: {count:,} ({percentage:.1f}%)")

        if output_file:
            print()
            print(f"📁 输出文件: {GREEN}{output_file}{NC}")

        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")

    def export_to_json(self, file_path):
        """导出统计信息到 JSON 文件"""
        import json
        data = {
            'total': self.total,
            'passed': self.passed,
            'filtered': self.filtered,
            'pass_rate': self.get_pass_rate(),
            'filter_reasons': self.reasons
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
