#!/usr/bin/env python3
"""
回流数据处理主脚本 V2
阶段1: 将原始 txt 转换为带 user_reply 的 jsonl
阶段2: 应用过滤规则，生成训练数据
"""
import sys
import argparse
import json
import re
from pathlib import Path

# 颜色定义
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def extract_cot_target(target_str):
    """提取 CoT target"""
    try:
        # 移除可能的前缀
        if target_str.startswith('```json'):
            target_str = target_str[7:]
        if target_str.endswith('```'):
            target_str = target_str[:-3]
        return target_str.strip()
    except:
        return target_str


def extract_context(input_prompt):
    """从 input_prompt 中提取对话历史，支持多种格式"""
    patterns = [
        r'## 你与用户的对话历史\n(.*?)\nThinking',
        r'## 你与用户的对话历史\n(.*?)\nAssistant:',
        r'【对话历史】如下：\n(.*?)\nAssistant:',
        r'【对话历史】如下：\n(.*?)\nThinking',
    ]
    for pattern in patterns:
        m = re.search(pattern, input_prompt, re.DOTALL)
        if m:
            return m.group(1).strip()
    raise Exception("未找到对话历史")

def collect_data_from_txt(input_file, output_file):
    """
    阶段1: 将原始 txt 转换为带 user_reply 的 jsonl

    输入格式: session_id\tmodel_name\tinput_prompt\toutput (TSV)
    输出格式: {"session_id": ..., "model_name": ..., "user_reply": ..., "input": ..., "target": {...}}
    """
    print(f"{BLUE}{'='*60}{NC}")
    print(f"{GREEN}阶段1: 数据转换 (txt → jsonl with user_reply){NC}")
    print(f"{BLUE}{'='*60}{NC}")
    print(f"📂 输入文件: {YELLOW}{input_file}{NC}")
    print(f"📁 输出文件: {YELLOW}{output_file}{NC}\n")

    all_contexts = {}
    origin_datas = []
    count = 0

    print(f"{YELLOW}⏳ 正在读取原始数据...{NC}")

    with open(input_file, "r", errors="ignore") as rf:
        for line in rf:
            count += 1
            if count % 10000 == 0:
                print(f"  已读取: {count} 行")

            try:
                stripped = line.strip()
                if not stripped:
                    continue

                # 自动检测格式：JSONL 或 TSV
                if stripped.startswith('{'):
                    obj = json.loads(stripped)
                    session_id = obj.get('session_id', '')
                    model_name = obj.get('model_name', '')
                    input_prompt = obj.get('input_prompt', '')
                    target = extract_cot_target(obj.get('output', ''))
                else:
                    line_ = stripped.split('\t')
                    if len(line_) != 4 or not line_[2].startswith("User"):
                        continue
                    session_id = line_[0]
                    model_name = line_[1]
                    input_prompt = line_[2]
                    target = extract_cot_target(line_[3])

                if not input_prompt.startswith("User"):
                    continue

                input_prompt = input_prompt.replace("\\n", "\n")
                target = json.loads(target)
                message_history_str = extract_context(input_prompt)

                origin_datas.append({
                    'session_id': session_id,
                    'model_name': model_name,
                    'context': message_history_str,
                    "input": input_prompt,
                    "target": target
                })

                # 收集该 session 所有轮次的 context
                if session_id not in all_contexts:
                    all_contexts[session_id] = set()
                all_contexts[session_id].add(message_history_str)
            except Exception as e:
                continue

    print(f"\n✅ 读取完成:")
    print(f"  - 总行数: {count}")
    print(f"  - 有效会话数: {len(all_contexts)}")
    print(f"  - 有效数据条数: {len(origin_datas)}\n")

    print(f"{YELLOW}⏳ 正在提取用户回复...{NC}")

    user_reply_dict = {}
    for session_id, contexts in all_contexts.items():
        user_context = {}
        for message_history in contexts:
            message_history_lines = message_history.split("\n")
            for index, current_message in enumerate(message_history_lines):
                if current_message.startswith("用户") and index > 0 and message_history_lines[index-1].startswith("客服") and len(current_message) > 3:
                    context = "\n".join(message_history_lines[:index])
                    user_context[context] = current_message
        if len(user_context) > 0:
            user_reply_dict[session_id] = user_context

    print(f"✅ 提取完成: {len(user_reply_dict)} 个会话包含用户回复\n")

    print(f"{YELLOW}⏳ 正在匹配数据...{NC}")

    datas = []
    for data in origin_datas:
        try:
            session_id = data["session_id"]
            model_name = data["model_name"]
            context = data["context"]
            input_prompt = data["input"]
            target = data["target"]
            response = target["Response"]
            message_history = f'{context}\n{response}'

            user_reply = None

            # 方法1：精确匹配（原逻辑，session 完整时使用）
            if session_id in user_reply_dict and message_history in user_reply_dict[session_id]:
                user_reply = user_reply_dict[session_id][message_history]
            else:
                # 方法2：从 context 本身直接提取下一条用户回复
                # context 末尾是"客服:xxx"，下一条用户回复在 context 的后续行里
                # 实际上 user_reply 就是 context 里紧跟在 response 后面的用户行
                # 但 context 不包含 response 后的内容，所以从 user_reply_dict 里
                # 用 suffix 匹配：找 context 的后缀能匹配到的 key
                if session_id in user_reply_dict:
                    ctx_lines = message_history.split("\n")
                    # 从末尾往前找，用越来越短的后缀去匹配
                    for start in range(len(ctx_lines)):
                        suffix = "\n".join(ctx_lines[start:])
                        if suffix in user_reply_dict[session_id]:
                            user_reply = user_reply_dict[session_id][suffix]
                            break

            if user_reply is None:
                continue

            datas.append({
                "session_id": session_id,
                "model_name": model_name,
                "user_reply": user_reply,
                "input": input_prompt,
                "target": json.dumps(target, ensure_ascii=False)
            })
        except Exception as e:
            continue

    print(f"✅ 匹配完成: {len(datas)} 条数据\n")

    print(f"{YELLOW}⏳ 正在写入文件...{NC}")
    with open(output_file, "w") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    print(f"{GREEN}✅ 阶段1完成！{NC}")
    print(f"📁 输出文件: {output_file}")
    print(f"📊 数据条数: {len(datas)}\n")

    return len(datas)


# ==================== 过滤规则 ====================

# 用户认可关键词
POSITIVE_KEYWORDS = ["好的", "好吧", "那行吧", "谢谢", "好的谢谢", "好的好的谢谢", "要得谢谢哈", "好谢谢", "哦哦谢谢", "谢谢啦", "是的", "是的是的", "是的呢", "是的啊", "是的亲", "是的呀", "是的啦", "对", "嗯", "嗯嗯", "恩", "行", "是", "好", "没事了", "没问题", "是啊", "好的再见", "喔喔那好吧", "对的", "对啊", "是的恢复评价", "那好吧", "行吧", "可以谢谢", "可以的", "可以", "可以啊", "可以了已解决", "可以麻烦了", "可以的谢谢", "可以谢谢", "可以了", "可以谢谢你", "可以尽快", "可以知道了", "可以请尽快"]

# 用户负面关键词
NEGATIVE_KEYWORDS = ["不行", "不可以", "不要", "不满意", "投诉", "退款", "差评", "垃圾", "骗人", "太差", "差", "不解决", "不处理", "不帮忙", "不理我", "不回复", "无语了", "失望", "生气了", "气死了", "烦死了", "受够了", "恶心", "滚", "去死吧", "死全家了", "你们公司垃圾", "你们客服垃圾", "你们服务太差", "你们太差了", "你们公司太差了", "你们公司垃圾死全家了", "你们客服垃圾死全家了", "你们服务太差死全家了", "你们太差了死全家了", "你妈", "尼玛", "操你", "卧槽", "麻痹", "妈逼", "妈的", "妈了个", "马勒戈壁", "麻辣隔壁", "听不懂", "人话", "傻逼", "弱智", "SB", "CNM", "cnm", "sb", "滚", "不要", "不好", "不行", "不可以", "不是", "不对", "不愿意", "人工", "客服电话"]

# 过度承诺关键词
OVERPROMISE_KEYWORDS = ["一定", "保证", "必须", "肯定", "绝对", "100%"]

# 口语词
MODAL_PARTICLES = ["哦", "啊", "呃", "嗯", "哈", "呢", "吧", "啦", "哟"]

# 退货/取回相关关键词
RETURN_KEYWORDS = [
    '退货', '退回', '取回', '保留商品', '上门取件', '取件',
    '自行处理', '丢弃', '扔掉', '寄回', '退还',
    '商品处理', '物品处理', '货物退回',
]

# 其他业务名称
OTHER_BUSINESS_KEYWORDS = [
    '拼好饭', '放心吃', '美团买菜', '美团优选', '美团闪购',
    '象大厨', '象会员', '象超市',
]

# 转人工关键词（user_reply 中）
MANUAL_SERVICE_KEYWORDS = [
    '转人工', '人工', '转人工服务', '人工服务',
    '转人工客服', '人工客服', '客服电话'
]

# 转人工关键词（response 中）
MANUAL_SERVICE_RESPONSE_KEYWORDS = [
    '帮您申诉', '帮您提交', '智能', '匹配',
    '反馈专员', '升级专员', '转接', '转交', '回访'
]

# 合法工具列表
LEGAL_TOOLS = [
    "加急调度", "系统催单", "智能跟单", "取消订单",
    "操作赔付-优惠券-x元", "操作赔付-运费券-3元",
    "选择商品", "小象单商品退款-xx%", "小象整单申请退款",
    "催促退款审核", "退审跟单", "引导自助修改订单", "引导自助联系骑手",
    "外呼骑手-修改订单", "外呼骑手-协商调换货品", "外呼骑手-催促配送",
    "外呼骑手-核实情况", "再次外呼骑手-……",
    "外呼门店-修改订单", "再次外呼门店-修改订单",
    "投诉骑手", "开发票", "会员卡退款", "管理会员自动续费"
]

# 合法赔付金额
LEGAL_COMPENSATION = [3, 5, 8, 10, 15, 20]
LEGAL_DELIVERY_FEE = [3]


def check_user_approval(user_reply):
    """1. 检查用户是否认可（必须通过）"""
    if not user_reply:
        return False
    for keyword in POSITIVE_KEYWORDS:
        if keyword in user_reply:
            return True
    return False


def check_user_negative(user_reply):
    """2. 检查用户是否负面反馈"""
    if not user_reply:
        return False
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in user_reply:
            return True
    return False


def check_illegal_solution(response_solution, dialogue_agree_solution):
    """3. 检查工具/方案是否合法"""
    try:
        if response_solution == "无":
            return False

        # 检查退款比例（支持两种格式：小象单商品退款-xx% 和 小象-单商品退款-xx%）
        pattern_refund = r'^小象-?单商品退款-(\d+)%$'
        match = re.match(pattern_refund, response_solution)
        if match:
            bili = int(match.group(1))
            return bili < 0 or bili > 100

        # 检查优惠券金额
        pattern_compensation = r'^操作赔付-优惠券-(\d+)元$'
        match = re.match(pattern_compensation, response_solution)
        if match:
            amount = int(match.group(1))
            return amount not in LEGAL_COMPENSATION

        # 检查运费券金额
        pattern_delivery = r'^操作赔付-运费券-(\d+)元$'
        match = re.match(pattern_delivery, response_solution)
        if match:
            amount = int(match.group(1))
            return amount not in LEGAL_DELIVERY_FEE

        # 检查是否在合法工具列表中
        for tool in LEGAL_TOOLS:
            if response_solution.startswith(tool.replace("x", "").replace("xx", "")):
                return False

        return True  # 不在合法列表中
    except:
        return True


def check_overpromise(response):
    """4. 检查是否过度承诺"""
    for keyword in OVERPROMISE_KEYWORDS:
        if keyword in response:
            return True
    return False


def check_excessive_modal_particles(response, max_count=5):
    """5. 检查是否有过多的口语词"""
    count = 0
    for particle in MODAL_PARTICLES:
        count += response.count(particle)
    return count > max_count


def check_output_length(response, min_length=10, max_length=2000):
    """6. 检查输出长度是否合理"""
    length = len(response)
    return not (min_length <= length <= max_length)


def check_repetitive_response(response):
    """7. 检查是否有重复回复"""
    for i in range(len(response) - 3):
        substr = response[i:i+3]
        if response.count(substr) > 3:
            return True
    return False


def check_return_keywords(response):
    """8. 检查是否包含退货/取回关键词"""
    for keyword in RETURN_KEYWORDS:
        if keyword in response:
            return True
    return False


def check_other_business_keywords(response):
    """9. 检查是否包含其他业务名称"""
    for keyword in OTHER_BUSINESS_KEYWORDS:
        if keyword in response:
            return True
    return False


def check_manual_service_keywords(user_reply, response):
    """10. 检查是否包含转人工关键词"""
    # 检查 user_reply 中的转人工关键词
    for keyword in MANUAL_SERVICE_KEYWORDS:
        if keyword in user_reply:
            return True

    # 检查 response 中的转人工关键词
    for keyword in MANUAL_SERVICE_RESPONSE_KEYWORDS:
        if keyword in response:
            return True

    return False


def extract_signal(text, pattern):
    """从文本中提取信号值"""
    import re
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None


def check_signal_logic(input_prompt, response_solution):
    """
    11. 信号逻辑校验

    检查工具方案与信号是否一致：
    - 加急调度: 需要 {订单骑手状态:无骑手接单} 或 {订单门店状态:等待骑手接单}
    - 取消订单: 需要 {是否可取消订单:是}
    - 催促退款审核: 需要商品退款状态为 '不可退款 退款进行中'
    """
    import re

    # 场景1: 加急调度
    if "加急调度" in response_solution:
        val_rider = extract_signal(input_prompt, r'\{订单骑手状态:(.*?)\}')
        val_store = extract_signal(input_prompt, r'\{订单门店状态:(.*?)\}')

        condition_1 = (val_rider == "无骑手接单")
        condition_2 = (val_store == "等待骑手接单")

        if not (condition_1 or condition_2):
            return True  # 信号不一致，过滤

    # 场景2: 取消订单
    elif "取消订单" in response_solution:
        val_cancel = extract_signal(input_prompt, r'\{是否可取消订单:(.*?)\}')

        if val_cancel != "是":
            return True  # 信号不一致，过滤

    # 场景3: 催促退款审核
    elif "催促退款审核" in response_solution:
        # 提取所有商品退款状态
        pat_refund_status = r"['\"]商品退款状态['\"]\s*:\s*['\"]([^'\"]*)['\"]"
        all_statuses = re.findall(pat_refund_status, input_prompt, re.DOTALL)
        clean_statuses = [s.strip() for s in all_statuses]

        target_status = "不可退款 退款进行中"
        if target_status not in clean_statuses:
            return True  # 信号不一致，过滤

    return False


def check_compensation_conflict(input_prompt, response_solution):
    """
    12. 检查不可赔付但操作赔付的冲突

    规则: 当 {订单是否可赔付:否} 且工具中有 "操作赔付" 时，过滤
    """
    import ast

    # 如果没有"操作赔付"，直接通过
    if "操作赔付" not in response_solution:
        return False

    # 查找 {订单是否可赔付:否}
    for line in input_prompt.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 方法A: 尝试解析字典
        if line.startswith('{') and line.endswith('}'):
            try:
                p_dict = ast.literal_eval(line)
                if isinstance(p_dict, dict):
                    if p_dict.get('订单是否可赔付') == '否':
                        return True  # 冲突，过滤
            except (SyntaxError, ValueError):
                pass

        # 方法B: 字符串匹配兜底
        clean_line = line.replace(" ", "").replace("'", "").replace('"', "")
        if "订单是否可赔付:否" in clean_line:
            return True  # 冲突，过滤

    return False


def extract_products_info(input_text):
    """从 input 中提取商品信息（商品名称和退款状态）"""
    products = []

    # 提取商品信息字典
    patterns = [
        r"'商品名称':\s*'([^']*)'[^}]*'商品退款状态':\s*'([^']*)'",
        r'"商品名称":\s*"([^"]*)"[^}]*"商品退款状态":\s*"([^"]*)"',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, input_text)
        for name, status in matches:
            products.append({
                "商品名称": name,
                "商品退款状态": status
            })

    return products


def check_claim_human(response, context):
    """
    14. 检查客服是否声称自己是真人

    规则:
    1. 客服回复中包含"我是人工"、"我是真人"等表述
    2. 用户问"你是人工吗"且客服回答"是的"、"我是真人"等
    """
    # 规则1: 客服主动声称自己是真人
    if re.search(r"我(是|就是|也是)(.*?)(人工|真人|真实)", response):
        return True

    # 规则2: 用户询问是否是人工，客服确认
    # 从 context 中提取最后一轮用户对话
    context_lines = context.split('\n') if context else []
    last_turn = context_lines[-1] if context_lines else ""

    if last_turn.startswith('用户'):
        # 用户问"你是人工吗"、"你是真人吗"等
        if re.search(r"你(是|是不是|不是)(.*?)(人工|真人)(.*?)(吗)?(\?|？)?", last_turn):
            # 客服回答"是的"、"对的"、"我是真人"等
            if re.search(r'是的|对的|没错|我是真|我是人', response):
                return True

    return False


def check_refund_overpromise(response, input_prompt):
    """
    15. 检查退款越权（不能说"已退款"）

    规则: 客服不能说"已退款"、"退款已到账"等已完成的表述
    豁免: 商品状态为"不可退款 已全部退款"时可以说
    """

    # 1. 定义违规表述模式（已完成结果表述）
    violation_patterns = [
        r'直接退款成功',
        r'已(?:成功)?退款(?:成功)?(?!申请)(?!审核)',  # 排除"已退款申请"、"已退款审核"
        r'已(?:成功)?退费(?:成功)?',
        r'已(?:成功)?赔付(?:成功)?',
        r'已(?:成功)?补偿(?:成功)?',
        r'退款已到账',
        r'退款已?成功',
        r'已经退款给您',
        r'已经退款到',
        r'退款到账',
        r'已为您退款(?!申请)',  # 排除"已为您退款申请"
        r'已给您退款',
        r'退款已处理完成',
        r'退款已完成',
        r'已经完成退款',
        r'退费已到账',
        r'赔付已到账',
        r'补偿已到账',
    ]

    # 2. 定义需要排除的过程态表述（即使匹配到上述模式，如果包含这些词也不算违规）
    allowed_process_patterns = [
        r'已.*?操作.*?退款',
        r'已.*?提交.*?退款',
        r'已.*?申请.*?退款',
        r'退款.*?已.*?操作',
        r'退款.*?已.*?提交',
        r'退款.*?已.*?申请',
        r'已.*?帮您.*?退款',
        r'退款.*?正在',
        r'退款.*?审核',
    ]

    # 3. 检查是否包含违规表述
    matched_violations = []
    for pattern in violation_patterns:
        matches = re.finditer(pattern, response)
        for match in matches:
            matched_violations.append(match.group())

    # 如果没有匹配到违规表述，判为不违规
    if not matched_violations:
        return False

    # 4. 检查是否包含过程态表述（如果有，则不算违规）
    for pattern in allowed_process_patterns:
        if re.search(pattern, response):
            return False  # 属于过程态，不算违规

    # 5. 检查豁免条件：商品状态是否为"不可退款 已全部退款"
    products = extract_products_info(input_prompt)
    has_fully_refunded = False
    for product in products:
        status = product.get('商品退款状态', '')
        if '不可退款' in status and '已全部退款' in status:
            has_fully_refunded = True
            break

    if has_fully_refunded:
        return False  # 符合豁免条件

    # 6. 最终判定为违规
    return True


def check_call_user(response):
    """
    15. 检查是否说要给用户打电话

    规则: 智能客服不能说要给用户打电话、联系用户等
    """
    # 规则1: 我...给/为你/您打/拨/回拨/来电/致电/去电/回电
    if re.search(r"我.{0,6}(给|为)[你您](打|拨|回拨|来电|致电|去电|回电)", response):
        return True

    # 规则2: 我...联系/外呼/致电/去电你/您
    if re.search(r"我.{0,4}(联系|外呼|致电|去电)[你您]", response):
        return True

    # 规则3: 给你/您回电/来电
    if re.search(r"(给|为)[你您](回电|来电)", response):
        return True

    # 规则4: 外呼 + 注意接听
    if re.search(r"外呼", response) and re.search(r"注意接听", response):
        return True

    return False


def check_escalate_transfer(response):
    """
    16. 检查是否说要升级/转接其他客服

    规则: 智能客服不能说要转接到专员、升级到更高级客服等
    """
    # 检查升级/转接关键词
    if re.search(r"帮您转到|帮您转入|转接|专员|专属客服|专人|专家|升级|更专业的|更高级的", response):
        return True

    return False


def check_refund_operation(response):
    """
    18. 检查是否说"帮您操作退款"

    规则: 智能客服不能承诺"帮您操作退款"，属于越权承诺
    """
    return bool(re.search(r'帮[您你]操作退款', response))


def check_invoice_promise(response):
    """
    19. 检查是否承诺代办发票

    规则: 智能客服不能承诺帮用户代办/开具/申请发票
    """
    return bool(re.search(r'帮[您你].{0,6}(开|申请|办理|代办|提交|处理).{0,4}发票', response))


def check_close_monthly_payment(response):
    """
    20. 检查是否告知已帮用户关闭月付

    规则: 智能客服不能说已帮用户关闭月付，属于越权操作
    """
    return bool(re.search(r'(已|帮[您你]).{0,6}(关闭|取消|停用|关停).{0,6}月付', response))


def check_low_quality_response(response):
    """
    23. 检查低质话术：我无法系列

    规则: 客服说"我无法"属于无效回复，应过滤
    """
    return bool(re.search(r'我无法', response))


def check_invoice_void(response):
    """
    24. 检查是否提及发票作废

    规则: 客服不能提及"作废发票"、"发票作废"等，智能客服无此操作权限
    """
    return bool(re.search(r'(作废发票|发票作废)', response))


def check_xiaoxiang_refund_context(response_solution, context):
    """
    17. 检查小象单商品退款是否有必要的上下文（图片或选择）

    规则: 如果使用"小象单商品退款"方案，对话历史中必须包含"图片"或"选择"
    原因: 用户需要选择商品并提供商品图片
    """
    # 检查是否是小象单商品退款方案（支持两种格式）
    pattern = r'小象-?单商品退款-\d+%'
    is_xiaoxiang_refund = bool(re.search(pattern, response_solution))

    if not is_xiaoxiang_refund:
        return False  # 不是小象单商品退款，不需要检查

    # 检查必要条件：必须包含 "图片" 或 "选择"
    has_required_context = ('图片' in context) or ('选择' in context)

    if not has_required_context:
        return True  # 缺少必要的上下文，过滤

    return False  # 有必要的上下文，通过


def check_response_signal_oversold(input_prompt, response):
    """
    18. 检查话术与信号匹配：超售后状态

    规则: 当 {订单是否超售后:否} 时，Response 不应该包含"超售后"相关表述
    原因: 订单未超售后，不应该提及超售后问题
    """
    # 提取订单是否超售后信号
    val_oversold = extract_signal(input_prompt, r'\{订单是否超售后:(.*?)\}')

    if val_oversold == "否":
        # 订单未超售后，检查话术中是否提及超售后
        if "超售后" in response:
            return True  # 信号不一致，过滤

    return False


def check_response_signal_rider(input_prompt, response):
    """
    19. 检查话术与信号匹配：骑手接单状态

    规则:
    - 当 {订单骑手状态:无骑手接单} 时，Response 不应该说"已有骑手接单"
    - 当 {订单骑手状态} 不是"无骑手接单"时，Response 也不应该说"已有骑手接单"

    原因: "已有骑手接单"表述只在骑手状态为"无骑手接单"时才合理（表示现在已经有骑手接单了）
    """
    # 提取订单骑手状态信号
    val_rider = extract_signal(input_prompt, r'\{订单骑手状态:(.*?)\}')

    # 检查话术中是否有"已有骑手接单"
    if "已有骑手接单" in response or "已有骑手" in response:
        # 这个表述只在骑手状态为"无骑手接单"时才合理
        # 如果是其他状态或为空，都应该过滤
        if val_rider != "无骑手接单":
            return True  # 信号不一致，过滤

    return False


def apply_filters_skip_approval(data):
    """
    应用过滤规则，但跳过规则1（用户认可度检查）

    用于认可 session 的前置轮次：这些轮次的 user_reply 可能不包含正面词汇，
    但因为属于认可 session，所以应该保留，只需检查规则2-17即可。

    Args:
        data: {"user_reply": ..., "target": "..."}

    Returns:
        tuple: (passed, reason)
    """
    try:
        user_reply = data.get("user_reply", "")
        target = json.loads(data.get("target", "{}"))

        response = target.get("Response", "")
        response_solution = target.get("ResponseSolution", "无")
        dialogue_agree_solution = target.get("DialogueAgreeSolution", "")
        context = data.get("context", "")
        input_prompt = data.get("input", "")

        # 跳过规则1（用户认可度检查）
        # 直接从规则2开始

        # 2. 用户负面反馈检查
        if check_user_negative(user_reply):
            return False, "用户负面反馈"

        # 3. 非法工具/方案检查
        if check_illegal_solution(response_solution, dialogue_agree_solution):
            return False, "非法工具/方案"

        # 4. 过度承诺检查
        if check_overpromise(response):
            return False, "过度承诺"

        # 5. 过多口语词检查
        if check_excessive_modal_particles(response):
            return False, "过多口语词"

        # 6. 输出长度检查
        if check_output_length(response):
            return False, "输出长度不合理"

        # 7. 重复回复检查
        if check_repetitive_response(response):
            return False, "重复回复"

        # 8. 退货/取回关键词检查
        if check_return_keywords(response):
            return False, "包含退货/取回关键词"

        # 9. 其他业务名称检查
        if check_other_business_keywords(response):
            return False, "包含其他业务名称"

        # 10. 转人工关键词检查
        if check_manual_service_keywords(user_reply, response):
            return False, "包含转人工关键词"

        # 11. 信号逻辑校验
        if check_signal_logic(input_prompt, response_solution):
            return False, "信号逻辑不一致"

        # 12. 不可赔付但操作赔付检查
        if check_compensation_conflict(input_prompt, response_solution):
            return False, "不可赔付但操作赔付"

        # 13. 退款越权检查（不能说"已退款"）
        if check_refund_overpromise(response, input_prompt):
            return False, "退款越权（已退款表述）"

        # 14. 客服声称自己是真人检查
        if check_claim_human(response, context):
            return False, "客服声称自己是真人"

        # 15. 说要给用户打电话检查
        if check_call_user(response):
            return False, "说要给用户打电话"

        # 16. 升级/转接其他客服检查
        if check_escalate_transfer(response):
            return False, "升级/转接其他客服"

        # 17. 小象单商品退款上下文检查
        if check_xiaoxiang_refund_context(response_solution, context):
            return False, "小象单商品退款缺少图片或选择"

        # 18. 话术与信号匹配：超售后状态
        if check_response_signal_oversold(input_prompt, response):
            return False, "话术与信号不一致（超售后）"

        # 19. 话术与信号匹配：骑手接单状态
        if check_response_signal_rider(input_prompt, response):
            return False, "话术与信号不一致（骑手接单）"

        # 20. 帮您操作退款检查
        if check_refund_operation(response):
            return False, "帮您操作退款（越权承诺）"

        # 21. 承诺代办发票检查
        if check_invoice_promise(response):
            return False, "承诺代办发票（越权承诺）"

        # 22. 告知已关闭月付检查
        if check_close_monthly_payment(response):
            return False, "告知已关闭月付（越权操作）"

        # 23. 低质话术检查（我无法）
        if check_low_quality_response(response):
            return False, "低质话术（我无法）"

        # 24. 发票作废检查
        if check_invoice_void(response):
            return False, "提及发票作废（越权操作）"

        return True, None

    except Exception as e:
        return False, f"数据解析错误: {str(e)}"


def apply_filters(data):
    """
    应用所有过滤规则

    Args:
        data: {"user_reply": ..., "target": "..."}

    Returns:
        tuple: (passed, reason)
    """
    try:
        user_reply = data.get("user_reply", "")
        target = json.loads(data.get("target", "{}"))

        response = target.get("Response", "")
        response_solution = target.get("ResponseSolution", "无")
        dialogue_agree_solution = target.get("DialogueAgreeSolution", "")

        # 2. 用户负面反馈检查
        if check_user_negative(user_reply):
            return False, "用户负面反馈"

        # 3. 非法工具/方案检查
        if check_illegal_solution(response_solution, dialogue_agree_solution):
            return False, "非法工具/方案"

        # 4. 过度承诺检查
        if check_overpromise(response):
            return False, "过度承诺"

        # 5. 过多口语词检查
        if check_excessive_modal_particles(response):
            return False, "过多口语词"

        # 6. 输出长度检查
        if check_output_length(response):
            return False, "输出长度不合理"

        # 7. 重复回复检查
        if check_repetitive_response(response):
            return False, "重复回复"

        # 8. 退货/取回关键词检查
        if check_return_keywords(response):
            return False, "包含退货/取回关键词"

        # 9. 其他业务名称检查
        if check_other_business_keywords(response):
            return False, "包含其他业务名称"

        # 10. 转人工关键词检查
        if check_manual_service_keywords(user_reply, response):
            return False, "包含转人工关键词"

        # 11. 信号逻辑校验
        input_prompt = data.get("input", "")
        if check_signal_logic(input_prompt, response_solution):
            return False, "信号逻辑不一致"

        # 12. 不可赔付但操作赔付检查
        if check_compensation_conflict(input_prompt, response_solution):
            return False, "不可赔付但操作赔付"

        # 13. 退款越权检查（不能说"已退款"）
        if check_refund_overpromise(response, input_prompt):
            return False, "退款越权（已退款表述）"

        # 14. 客服声称自己是真人检查
        context = data.get("context", "")
        if check_claim_human(response, context):
            return False, "客服声称自己是真人"

        # 15. 说要给用户打电话检查
        if check_call_user(response):
            return False, "说要给用户打电话"

        # 16. 升级/转接其他客服检查
        if check_escalate_transfer(response):
            return False, "升级/转接其他客服"

        # 17. 小象单商品退款上下文检查
        if check_xiaoxiang_refund_context(response_solution, context):
            return False, "小象单商品退款缺少图片或选择"

        # 18. 话术与信号匹配：超售后状态
        if check_response_signal_oversold(input_prompt, response):
            return False, "话术与信号不一致（超售后）"

        # 19. 话术与信号匹配：骑手接单状态
        if check_response_signal_rider(input_prompt, response):
            return False, "话术与信号不一致（骑手接单）"

        # 20. 帮您操作退款检查
        if check_refund_operation(response):
            return False, "帮您操作退款（越权承诺）"

        # 21. 承诺代办发票检查
        if check_invoice_promise(response):
            return False, "承诺代办发票（越权承诺）"

        # 22. 告知已关闭月付检查
        if check_close_monthly_payment(response):
            return False, "告知已关闭月付（越权操作）"

        # 23. 低质话术检查（我无法）
        if check_low_quality_response(response):
            return False, "低质话术（我无法）"

        # 24. 发票作废检查
        if check_invoice_void(response):
            return False, "提及发票作废（越权操作）"

        return True, None

    except Exception as e:
        return False, f"数据解析错误: {str(e)}"


def filter_data(input_file, output_file):
    """
    阶段2: 应用过滤规则，生成训练数据

    两遍扫描：
    1. 第一遍：找出所有认可 session（user_reply 包含正面词汇且通过规则1）
    2. 第二遍：保留规则 - 认可 session 的所有轮次，其他 session 则检查全部规则

    输入格式: {"session_id": ..., "model_name": ..., "user_reply": ..., "input": ..., "target": {...}}
    输出格式: {"input": ..., "target": {...}, "session_id": ..., "metadata": {...}}
    """
    print(f"{BLUE}{'='*60}{NC}")
    print(f"{GREEN}阶段2: 数据过滤{NC}")
    print(f"{BLUE}{'='*60}{NC}")
    print(f"📂 输入文件: {YELLOW}{input_file}{NC}")
    print(f"📁 输出文件: {YELLOW}{output_file}{NC}\n")

    # 第一遍：读取所有数据
    print(f"{YELLOW}⏳ 第一遍扫描：读取数据...{NC}")
    all_data = []

    with open(input_file, "r") as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                all_data.append(data)
            except:
                pass

    print(f"✅ 读取 {len(all_data)} 条数据\n")

    # 第二遍：过滤
    stats = {
        "total": 0,
        "passed": 0,
        "filtered": 0,
        "reasons": {}
    }

    results = []

    print(f"{YELLOW}⏳ 第二遍扫描：应用过滤规则...{NC}\n")

    for i, data in enumerate(all_data):
        stats["total"] += 1

        if (i + 1) % 1000 == 0:
            print(f"  处理进度: {i + 1} 行 ({stats['passed']} 通过, {stats['filtered']} 过滤)")

        try:
            session_id = data["session_id"]

            passed, reason = apply_filters(data)

            if passed:
                # 格式化为训练数据
                target = json.loads(data["target"])
                results.append({
                    "input": data["input"],
                    "target": target,
                    "session_id": data["session_id"],
                    "metadata": {
                        "model_name": data["model_name"],
                        "user_reply": data["user_reply"]
                    }
                })
                stats["passed"] += 1
            else:
                stats["filtered"] += 1
                stats["reasons"][reason] = stats["reasons"].get(reason, 0) + 1
        except Exception as e:
            stats["filtered"] += 1
            stats["reasons"]["数据解析错误"] = stats["reasons"].get("数据解析错误", 0) + 1

    # 写入输出文件
    print(f"\n{YELLOW}⏳ 正在写入结果...{NC}")
    with open(output_file, "w") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    # 打印统计信息
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{GREEN}📊 处理统计{NC}")
    print(f"{BLUE}{'='*60}{NC}")
    print(f"输入总行数: {stats['total']:,}")
    print(f"✅ 通过过滤: {stats['passed']:,} ({stats['passed']/stats['total']*100:.1f}%)")
    print(f"❌ 被过滤: {stats['filtered']:,} ({stats['filtered']/stats['total']*100:.1f}%)")

    if stats['reasons']:
        print(f"\n过滤原因分布:")
        for reason, count in sorted(stats['reasons'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {reason}: {count:,}")

    print(f"\n📁 输出文件: {output_file}")
    print(f"{BLUE}{'='*60}{NC}\n")

    return stats


def parse_row(stripped):
    """解析单行数据（JSONL 或 TSV），返回 (session_id, model_name, input_prompt, target_str) 或 None"""
    if not stripped:
        return None
    if stripped.startswith('{'):
        obj = json.loads(stripped)
        return (
            obj.get('session_id', ''),
            obj.get('model_name', ''),
            obj.get('input_prompt', ''),
            extract_cot_target(obj.get('output', ''))
        )
    else:
        parts = stripped.split('\t')
        if len(parts) != 4 or not parts[2].startswith("User"):
            return None
        return parts[0], parts[1], parts[2], extract_cot_target(parts[3])


def process_from_rows(lines, output_file, append=False, shard_label=''):
    """
    从行迭代器（文件/stdin）直接完成阶段1+2，结果写入 output_file。
    append=True 时追加写，不清空文件。
    """
    origin_datas = []
    count = 0
    # session_id -> set of all context strings (all rounds)
    all_contexts = {}

    for line in lines:
        count += 1
        try:
            row = parse_row(line.strip())
            if row is None:
                continue
            session_id, model_name, input_prompt, target_str = row
            if not input_prompt.startswith("User"):
                continue
            input_prompt = input_prompt.replace("\\n", "\n")
            target = json.loads(target_str)
            message_history_str = extract_context(input_prompt)
            origin_datas.append({
                'session_id': session_id,
                'model_name': model_name,
                'context': message_history_str,
                'input': input_prompt,
                'target': target,
            })
            # 收集该 session 所有轮次的 context
            if session_id not in all_contexts:
                all_contexts[session_id] = set()
            all_contexts[session_id].add(message_history_str)
        except Exception:
            continue

    # 从每个 session 的所有 context 中提取 user_reply
    # 每条 context 都解析一遍，合并到同一个 dict
    user_reply_dict = {}
    for session_id, contexts in all_contexts.items():
        user_context = {}
        for message_history in contexts:
            lines_h = message_history.split("\n")
            for idx, msg in enumerate(lines_h):
                if msg.startswith("用户") and idx > 0 and lines_h[idx-1].startswith("客服") and len(msg) > 3:
                    ctx = "\n".join(lines_h[:idx])
                    user_context[ctx] = msg
        if user_context:
            user_reply_dict[session_id] = user_context

    # 阶段1：匹配 user_reply（不过滤）
    all_data = []
    for data in origin_datas:
        try:
            session_id = data['session_id']
            context = data['context']
            target = data['target']
            response = target.get("Response", "")
            message_history = f'{context}\n{response}'

            user_reply = None
            if session_id in user_reply_dict:
                if message_history in user_reply_dict[session_id]:
                    user_reply = user_reply_dict[session_id][message_history]
                else:
                    # suffix 匹配：跨片 session 用后缀找 user_reply
                    ctx_lines = message_history.split("\n")
                    for start in range(len(ctx_lines)):
                        suffix = "\n".join(ctx_lines[start:])
                        if suffix in user_reply_dict[session_id]:
                            user_reply = user_reply_dict[session_id][suffix]
                            break

            if user_reply is None:
                continue

            all_data.append({
                "session_id": session_id,
                "model_name": data['model_name'],
                "user_reply": user_reply,
                "input": data['input'],
                "target": json.dumps(target, ensure_ascii=False),
                "context": context,
                "target_obj": target,
            })
        except Exception:
            continue

    # 阶段2：过滤（两遍扫描）
    # 过滤并写出
    stats = {"total": 0, "passed": 0, "filtered": 0, "reasons": {}}
    write_mode = 'a' if append else 'w'

    with open(output_file, write_mode) as f:
        for data in all_data:
            try:
                session_id = data["session_id"]
                user_reply = data["user_reply"]

                row = {
                    "session_id": session_id,
                    "model_name": data["model_name"],
                    "user_reply": user_reply,
                    "input": data["input"],
                    "target": data["target"],
                    "context": data["context"],
                }

                passed, reason = apply_filters(row)

                stats["total"] += 1
                if passed:
                    result = {
                        "input": row["input"],
                        "target": data["target_obj"],
                        "session_id": session_id,
                        "metadata": {
                            "model_name": row["model_name"],
                            "user_reply": user_reply,
                        }
                    }
                    f.write(json.dumps(result, ensure_ascii=False) + "\n")
                    stats["passed"] += 1
                else:
                    stats["filtered"] += 1
                    stats["reasons"][reason] = stats["reasons"].get(reason, 0) + 1
            except Exception:
                continue

    label = f" [{shard_label}]" if shard_label else ""
    print(f"✅{label} 读取 {count} 行，匹配 {stats['total']} 条，通过 {stats['passed']} 条，过滤 {stats['filtered']} 条")
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='回流数据处理工具 V2 - 两阶段处理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程（推荐）
  %(prog)s input.txt output.jsonl

  # 仅执行阶段1（转换）
  %(prog)s input.txt intermediate.jsonl --stage 1

  # 仅执行阶段2（过滤）
  %(prog)s intermediate.jsonl output.jsonl --stage 2
        """
    )
    parser.add_argument('input_file', nargs='?', help='输入文件路径（--stdin 模式下可省略）')
    parser.add_argument('output_file', help='输出文件路径')
    parser.add_argument('--stage', type=int, choices=[1, 2], help='指定执行阶段（1=转换, 2=过滤），不指定则执行完整流程')
    parser.add_argument('--stdin', action='store_true', help='从 stdin 读取 JSON 内容，直接完成阶段1+2')
    parser.add_argument('--append', action='store_true', help='追加写入输出文件（用于多片合并）')
    parser.add_argument('--shard', default='', help='分片标签，用于日志显示')

    args = parser.parse_args()

    # 创建输出目录
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if args.stdin:
            # stdin 模式：从 stdin 读 JSON，直接完成阶段1+2
            import ijson
            content = sys.stdin.buffer.read()
            # 找到 JSON 数组起始位置
            start = content.find(b'[')
            if start == -1:
                print(f"{RED}❌ stdin 中未找到 JSON 数组{NC}")
                sys.exit(1)
            # 提取所有 JSON 数组段（合并文件里可能有多段）
            def iter_all_json_arrays(raw_bytes):
                """从可能包含多段 JSON 数组的内容中逐条 yield item"""
                pos = 0
                while True:
                    start_pos = raw_bytes.find(b'[', pos)
                    if start_pos == -1:
                        break
                    # 找匹配的 ]
                    depth = 0
                    end_pos = start_pos
                    for i in range(start_pos, len(raw_bytes)):
                        if raw_bytes[i:i+1] == b'[':
                            depth += 1
                        elif raw_bytes[i:i+1] == b']':
                            depth -= 1
                            if depth == 0:
                                end_pos = i + 1
                                break
                    chunk = raw_bytes[start_pos:end_pos]
                    try:
                        for item in ijson.items(chunk, 'item'):
                            yield item
                    except Exception:
                        pass
                    pos = end_pos

            def json_to_lines(raw_bytes):
                for item in iter_all_json_arrays(raw_bytes):
                    if not isinstance(item, dict):
                        continue
                    sid = item.get('session_id', '')
                    mn = item.get('model_name', '')
                    ip = item.get('input_prompt', '')
                    op = item.get('output', '')
                    yield f"{sid}\t{mn}\t{ip}\t{op}"

            process_from_rows(json_to_lines(content), args.output_file,
                              append=args.append, shard_label=args.shard)

        elif not args.input_file:
            print(f"{RED}❌ 请提供输入文件路径，或使用 --stdin{NC}")
            sys.exit(1)

        # 检查输入文件
        elif not Path(args.input_file).exists():
            print(f"{RED}❌ 输入文件不存在: {args.input_file}{NC}")
            sys.exit(1)

        elif args.stage == 1:
            collect_data_from_txt(args.input_file, args.output_file)
        elif args.stage == 2:
            filter_data(args.input_file, args.output_file)
        else:
            # 执行完整流程
            intermediate_file = str(output_path.parent / f"{output_path.stem}_intermediate.jsonl")
            collect_data_from_txt(args.input_file, intermediate_file)
            filter_data(intermediate_file, args.output_file)
            print(f"{YELLOW}🗑️  清理中间文件: {intermediate_file}{NC}")
            Path(intermediate_file).unlink()
            print(f"{GREEN}✅ 全部完成！{NC}")

    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  处理被用户中断{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ 处理失败: {e}{NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
