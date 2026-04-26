#!/usr/bin/env python3
"""
数据验证模块
验证数据的完整性和有效性
"""


class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_required_fields(data):
        """
        验证必要字段是否存在且非空

        Args:
            data: 数据字典

        Returns:
            tuple: (is_valid, missing_fields)
        """
        required_fields = ['session_id', 'model_name', 'input_prompt', 'output']
        missing_fields = []

        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)

        return len(missing_fields) == 0, missing_fields

    @staticmethod
    def validate_json_output(output):
        """
        验证 output 是否是有效的 JSON

        Args:
            output: 输出字符串

        Returns:
            tuple: (is_valid, parsed_data)
        """
        import json
        try:
            parsed = json.loads(output)
            return True, parsed
        except:
            return False, None

    @staticmethod
    def validate_data(data):
        """
        综合验证数据

        Args:
            data: 数据字典

        Returns:
            tuple: (is_valid, error_message)
        """
        # 验证必要字段
        is_valid, missing_fields = DataValidator.validate_required_fields(data)
        if not is_valid:
            return False, f"缺少必要字段: {', '.join(missing_fields)}"

        # 验证 output 格式
        is_valid, _ = DataValidator.validate_json_output(data['output'])
        if not is_valid:
            return False, "output 不是有效的 JSON"

        return True, None
