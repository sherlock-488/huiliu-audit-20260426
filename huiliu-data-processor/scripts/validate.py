#!/usr/bin/env python3
"""
数据验证脚本
快速验证输入文件的格式和质量
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import DataParser, DataValidator


def validate_file(file_path):
    """验证文件"""
    print(f"📂 验证文件: {file_path}")
    print("━" * 60)

    parser = DataParser()
    validator = DataValidator()

    total = 0
    valid = 0
    invalid = 0
    errors = {}

    for data in parser.read_file(file_path):
        total += 1

        is_valid, error_msg = validator.validate_data(data)
        if is_valid:
            valid += 1
        else:
            invalid += 1
            if error_msg not in errors:
                errors[error_msg] = 0
            errors[error_msg] += 1

        if total % 1000 == 0:
            print(f"  已验证: {total} 行 (有效: {valid}, 无效: {invalid})")

    print()
    print("✅ 验证完成")
    print("━" * 60)
    print(f"总行数: {total}")
    print(f"✅ 有效: {valid} ({valid/total*100:.1f}%)")
    print(f"❌ 无效: {invalid} ({invalid/total*100:.1f}%)")

    if errors:
        print()
        print("错误分布:")
        for error, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {error}: {count}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 validate.py <输入文件>")
        sys.exit(1)

    validate_file(sys.argv[1])
