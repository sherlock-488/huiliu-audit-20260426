#!/usr/bin/env python3
"""
数据格式化模块
将原始数据格式化为训练格式
"""
import re


class DataFormatter:
    """数据格式化器"""

    @staticmethod
    def clean_text(text):
        """
        清洗文本

        Args:
            text: 输入文本

        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ""

        # 移除多余的空格
        text = re.sub(r' +', ' ', text)
        # 移除多余的换行符（保留单个换行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 去除首尾空白
        text = text.strip()

        return text

    @staticmethod
    def remove_punctuation(text):
        """
        移除标点符号

        Args:
            text: 输入文本

        Returns:
            str: 移除标点后的文本
        """
        punctuation = '！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～'
        return ''.join(char for char in text if char not in punctuation)

    @staticmethod
    def format_to_training_data(data):
        """
        格式化为训练数据格式

        Args:
            data: 原始数据字典

        Returns:
            dict: 训练数据格式
        """
        # 清洗输入和输出
        input_prompt = DataFormatter.clean_text(data['input_prompt'])
        output = DataFormatter.clean_text(data['output'])

        return {
            'input': input_prompt,
            'target': output,
            'session_id': data['session_id'],
            'metadata': {
                'model_name': data['model_name'],
                'source': 'huiliu_data'
            }
        }

    @staticmethod
    def extract_response_from_output(output):
        """
        从 output JSON 中提取 Response 字段

        Args:
            output: JSON 字符串

        Returns:
            str: Response 内容
        """
        import json
        try:
            data = json.loads(output)
            return data.get('Response', '')
        except:
            return ''
