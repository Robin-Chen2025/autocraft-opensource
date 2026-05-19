"""
工具函数模块
"""
from datetime import datetime


import random

def generate_task_no() -> str:
    """
    生成任务单号
    格式: TSK-YYYYMMDD-NNNN
    """
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    # 使用随机4位数作为序号，避免同一秒内重复
    sequence = random.randint(1000, 9999)
    return f"TSK-{date_str}-{sequence:04d}"


def get_current_datetime() -> datetime:
    """获取当前时间"""
    return datetime.now()


# 状态选项
TASK_STATUS_OPTIONS = [
    "新建",
    "待执行",
    "进行中",
    "待验证",
    "完成",
    "失败"
]

# 优先级选项
TASK_PRIORITY_OPTIONS = [
    "高",
    "中",
    "低"
]

# 验证结论选项
VERIFICATION_RESULT_OPTIONS = [
    "待验证",
    "通过",
    "不通过"
]
