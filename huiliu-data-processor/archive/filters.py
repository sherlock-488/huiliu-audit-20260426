#!/usr/bin/env python3
"""
回流数据过滤规则模块
"""
import re
import json

# 合法工具列表
LEGAL_TOOLS = [
    "加急调度",
    "系统催单",
    "智能跟单",
    "取消订单",
    "操作赔付-优惠券-x元",
    "操作赔付-运费券-3元",
    "选择商品",
    "小象单商品退款-xx%",
    "小象整单申请退款",
    "催促退款审核",
    "退审跟单",
    "引导自助修改订单",
    "引导自助联系骑手",
    "外呼骑手-修改订单",
    "外呼骑手-协商调换货品",
    "外呼骑手-催促配送",
    "外呼骑手-核实情况",
    "再次外呼骑手-……",
    "外呼门店-修改订单",
    "再次外呼门店-修改订单",
    "投诉骑手",
    "开发票",
    "会员卡退款",
    "管理会员自动续费"
]

# 合法赔付金额（优惠券档位）
LEGAL_COMPENSATION = [3, 5, 8, 10, 15, 20]

# 合法运费券金额
LEGAL_DELIVERY_FEE = [3]

# 用户认可关键词
POSITIVE_KEYWORDS = ["好的", "好吧", "那行吧", "谢谢", "好的谢谢", "好", "行", "可以", "嗯嗯", "ok", "OK"]

# 用户负面关键词
NEGATIVE_KEYWORDS = ["不行", "不可以", "不要", "不满意", "投诉", "退款", "差评", "垃圾", "骗人"]

# 过度承诺关键词
OVERPROMISE_KEYWORDS = ["一定", "保证", "必须", "肯定", "绝对", "100%"]

# 口语词
MODAL_PARTICLES = ["哦", "啊", "呃", "嗯", "哈", "呢", "吧", "啦", "哟"]

# 退货/取回相关关键词（智能客服没有此能力）
RETURN_KEYWORDS = [
    '退货', '退回', '取回', '保留商品', '上门取件', '取件',
    '自行处理', '丢弃', '扔掉', '寄回', '退还',
    '商品处理', '物品处理', '货物退回',
]

# 其他业务名称（不应出现在小象客服对话中）
OTHER_BUSINESS_KEYWORDS = [
    '拼好饭', '放心吃', '美团买菜', '美团优选', '美团闪购',
    '象大厨', '象会员', '象超市',
]


def check_illegal_solution(target):
    """检查是否包含非法方案"""
    try:
        data = json.loads(target)
        response_solution = data.get("ResponseSolution", "无")

        if response_solution == "无":
            return False

        # 检查赔付金额是否合规
        pattern_refund_bili = r'^小象单商品退款-(\d+)%$'
        match = re.match(pattern_refund_bili, response_solution)
        if match:
            bili = int(match.group(1))
            if bili < 0 or bili > 100:
                return True  # 非法
            return False

        # 检查优惠券金额是否合规
        pattern_compensation = r'^操作赔付-优惠券-(\d+)元$'
        match = re.match(pattern_compensation, response_solution)
        if match:
            amount = int(match.group(1))
            if amount not in LEGAL_COMPENSATION:
                return True  # 非法
            return False

        # 检查运费券金额是否合规
        pattern_delivery = r'^操作赔付-运费券-(\d+)元$'
        match = re.match(pattern_delivery, response_solution)
        if match:
            amount = int(match.group(1))
            if amount not in LEGAL_DELIVERY_FEE:
                return True  # 非法
            return False

        # 检查是否在合法工具列表中
        for tool in LEGAL_TOOLS:
            if response_solution.startswith(tool.replace("x", "").replace("xx", "")):
                return False

        return True  # 不在合法列表中

    except Exception as e:
        return True  # 解析失败，视为非法


def filter_back_data(output):
    """检查是否包含用户认可关键词"""
    try:
        data = json.loads(output)
        response = data.get("Response", "")

        # 检查是否包含正面关键词
        for keyword in POSITIVE_KEYWORDS:
            if keyword in response:
                return True

        return False

    except Exception:
        return False


def filter_negative_data(output):
    """检查是否包含用户负面关键词"""
    try:
        data = json.loads(output)
        response = data.get("Response", "")

        # 检查是否包含负面关键词
        for keyword in NEGATIVE_KEYWORDS:
            if keyword in response:
                return True

        return False

    except Exception:
        return False


def check_overpromise(output):
    """检查是否过度承诺"""
    try:
        data = json.loads(output)
        response = data.get("Response", "")

        # 检查是否包含过度承诺关键词
        for keyword in OVERPROMISE_KEYWORDS:
            if keyword in response:
                return True

        return False

    except Exception:
        return False


def check_excessive_modal_particles(output, max_count=5):
    """检查是否有过多的口语词"""
    try:
        data = json.loads(output)
        response = data.get("Response", "")

        count = 0
        for particle in MODAL_PARTICLES:
            count += response.count(particle)

        return count > max_count

    except Exception:
        return False


def check_output_length(output, min_length=10, max_length=2000):
    """检查输出长度是否合理"""
    try:
        data = json.loads(output)
        response = data.get("Response", "")

        length = len(response)
        return min_length <= length <= max_length

    except Exception:
        return False


def check_repetitive_response(output):
    """检查是否有重复回复"""
    try:
        data = json.loads(output)
        response = data.get("Response", "")

        # 简单检查：是否有连续重复的字符串（超过3次）
        for i in range(len(response) - 3):
            substr = response[i:i+3]
            if response.count(substr) > 3:
                return True

        return False

    except Exception:
        return False


def clean_text(text):
    """清洗文本"""
    # 移除多余的空格
    text = re.sub(r'\s+', ' ', text)
    # 移除多余的换行符
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def remove_punctuation(text):
    """移除标点符号"""
    punctuation = '！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～'
    return ''.join(char for char in text if char not in punctuation)


def check_return_keywords(output):
    """检查是否包含退货/取回相关关键词（智能客服没有此能力）"""
    try:
        data = json.loads(output)
        response = data.get("Response", "")

        # 检查是否包含退货/取回关键词
        for keyword in RETURN_KEYWORDS:
            if keyword in response:
                return True

        return False

    except Exception:
        return False


def check_other_business_keywords(output):
    """检查是否包含其他业务名称（如拼好饭、放心吃等）"""
    try:
        data = json.loads(output)
        response = data.get("Response", "")

        # 检查是否包含其他业务关键词
        for keyword in OTHER_BUSINESS_KEYWORDS:
            if keyword in response:
                return True

        return False

    except Exception:
        return False
