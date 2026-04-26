#!/usr/bin/env python3
"""
数据解析模块
支持 TSV 和 JSON 格式的输入数据解析
"""
import json


class DataParser:
    """数据解析器"""

    @staticmethod
    def parse_line(line, line_number=0):
        """
        解析单行数据

        Args:
            line: 输入行
            line_number: 行号（用于错误提示）

        Returns:
            dict: 包含 session_id, model_name, input_prompt, output 的字典
            None: 解析失败
        """
        try:
            line = line.strip()
            if not line:
                return None

            # 尝试解析 TSV 格式（制表符分隔）
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    return {
                        'session_id': parts[0],
                        'model_name': parts[1],
                        'input_prompt': parts[2],
                        'output': parts[3]
                    }

            # 尝试解析 JSON 格式
            data = json.loads(line)
            return {
                'session_id': data.get('session_id', ''),
                'model_name': data.get('model_name', ''),
                'input_prompt': data.get('input_prompt', ''),
                'output': data.get('output', '')
            }

        except json.JSONDecodeError:
            return None
        except Exception as e:
            return None

    @staticmethod
    def is_header_line(line):
        """
        判断是否是表头行

        Args:
            line: 输入行

        Returns:
            bool: 是否是表头
        """
        line = line.strip().lower()
        return line.startswith('session_id') and 'model_name' in line

    @staticmethod
    def read_file(file_path):
        """
        读取文件并解析所有行

        Args:
            file_path: 文件路径

        Yields:
            dict: 解析后的数据
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                # 跳过表头
                if i == 0 and DataParser.is_header_line(line):
                    continue

                data = DataParser.parse_line(line, i + 1)
                if data:
                    yield data
