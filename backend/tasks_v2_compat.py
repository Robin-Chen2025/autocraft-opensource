"""
tasks_v2表兼容层 - 让旧的/tasks API能够使用tasks_v2表数据

由于tasks表已删除，需要将tasks_v2表的数据转换为Task模型格式，
以便旧的API能够继续工作。
"""
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Task
from models.task_v2 import TaskV2


def get_task_v2_by_no(db: Session, task_no: str) -> Optional[TaskV2]:
    """从tasks_v2表获取任务"""
    query = select(TaskV2).where(TaskV2.task_no == task_no)
    result = db.execute(query)
    return result.scalar_one_or_none()


def convert_task_v2_to_task(task_v2: TaskV2) -> Task:
    """将TaskV2对象转换为Task对象"""
    if not task_v2:
        return None
    
    # 解析input_data获取描述信息
    description = ""
    requirements = ""
    try:
        if task_v2.input_data:
            input_json = json.loads(task_v2.input_data)
            description = input_json.get('description', '')
            requirements = input_json.get('requirements', '')
    except:
        pass
    
    # 状态转换：tasks_v2状态 -> tasks表状态
    v2_to_task_status = {
        "pending": "待执行",
        "in_progress": "执行中",
        "completed": "已完成",
        "verified": "已验证",
        "verification_failed": "验证失败",
        "failed": "执行失败"
    }
    task_status = v2_to_task_status.get(task_v2.status, "待执行")
    
    # 验证结果字段处理
    verification_result = "待验证"
    if task_v2.status == "verified":
        verification_result = "验证通过"
    elif task_v2.status == "verification_failed":
        verification_result = "验证失败"
    
    # 创建Task对象，使用tasks_v2表中的实际字段值
    task = Task(
        id=task_v2.id,
        task_no=task_v2.task_no,
        task_name=task_v2.task_name,
        task_type=task_v2.task_type,
        plan_id=task_v2.plan_id,
        plan_date=getattr(task_v2, 'plan_date', task_v2.created_at),
        plan_complete_time=getattr(task_v2, 'plan_complete_time', None),
        executor=getattr(task_v2, 'executor', "ac-glm5"),
        status=task_status,
        priority=getattr(task_v2, 'priority', "高"),
        execution_steps=f"执行{task_v2.task_name}。{description if description else requirements}",
        expected_result=f"成功完成{task_v2.task_name}",
        execution_log=task_v2.execution_log,
        output_result="",
        execution_date=getattr(task_v2, 'execution_date', None),
        verification_result=verification_result,
        verifier=getattr(task_v2, 'verifier', None),
        verification_time=getattr(task_v2, 'verification_time', None),
        created_at=task_v2.created_at,
        updated_at=task_v2.updated_at,
        verification_log=task_v2.verification_log,
        exec_start_time=getattr(task_v2, 'exec_start_time', None),
        exec_estimated_complete=getattr(task_v2, 'exec_estimated_complete', None),
        exec_complete_time=getattr(task_v2, 'exec_complete_time', None),
        verify_start_time=getattr(task_v2, 'verify_start_time', None),
        verify_estimated_complete=getattr(task_v2, 'verify_estimated_complete', None),
        verify_complete_time=getattr(task_v2, 'verify_complete_time', None),
        agent_id=getattr(task_v2, 'agent_id', None),
        phase_record_id=getattr(task_v2, 'phase_record_id', None),
        locked_by=getattr(task_v2, 'locked_by', None),
        locked_at=getattr(task_v2, 'locked_at', None),
        input_data=task_v2.input_data,
        extra_data=getattr(task_v2, 'extra_data', None)
    )
    
    return task


def get_task_by_no_compat(db: Session, task_no: str) -> Optional[Task]:
    """兼容版本：从tasks_v2表获取任务并转换为Task对象"""
    task_v2 = get_task_v2_by_no(db, task_no)
    if not task_v2:
        return None
    return convert_task_v2_to_task(task_v2)


def get_tasks_compat(db: Session, limit: int = 100, offset: int = 0) -> List[Task]:
    """兼容版本：从tasks_v2表获取任务列表"""
    query = select(TaskV2).order_by(TaskV2.created_at.desc()).limit(limit).offset(offset)
    result = db.execute(query)
    tasks_v2 = result.scalars().all()
    
    tasks = []
    for task_v2 in tasks_v2:
        task = convert_task_v2_to_task(task_v2)
        if task:
            tasks.append(task)
    
    return tasks