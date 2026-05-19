"""
工作计划 CRUD 操作
"""
import uuid
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, joinedload

from models import WorkPlan, ProjectProfile, ProjectPhase


def get_plans(db: Session, profile_id: str = None, status: str = None):
    """
    获取工作计划列表
    
    Args:
        db: 数据库会话
        profile_id: 项目档案 ID（可选，用于筛选）
        status: 状态（可选，用于筛选）
    
    Returns:
        list[WorkPlan]: 工作计划列表
    """
    query = select(WorkPlan)
    
    conditions = []
    if profile_id:
        conditions.append(WorkPlan.profile_id == profile_id)
    if status:
        conditions.append(WorkPlan.status == status)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(WorkPlan.created_at.asc())
    result = db.execute(query)
    return result.scalars().all()


def get_plan(db: Session, plan_id: str):
    """
    获取工作计划详情（含关联的 profile 和 workflow 信息）
    
    Args:
        db: 数据库会话
        plan_id: 计划 ID
    
    Returns:
        WorkPlan: 工作计划对象，包含关联的 profile 和 workflow
    """
    query = (
        select(WorkPlan)
        .options(
            joinedload(WorkPlan.profile),
            joinedload(WorkPlan.phase)
        )
        .where(WorkPlan.plan_id == plan_id)
    )
    result = db.execute(query)
    return result.scalars().first()


def create_plan(db: Session, plan_data: dict):
    """
    创建工作计划
    
    Args:
        db: 数据库会话
        plan_data: 计划数据（dict，包含 profile_id, phase_record_id, plan_name 等）
    
    Returns:
        WorkPlan: 创建的工作计划对象
    """
    # 生成 plan_id
    if 'plan_id' not in plan_data or not plan_data['plan_id']:
        plan_data['plan_id'] = f"plan_{uuid.uuid4().hex[:16]}"
    
    db_plan = WorkPlan(**plan_data)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_plan_tasks(db: Session, plan_id: str, status: str = None):
    """
    获取计划的任务列表（统一使用tasks_v2表）
    
    Args:
        db: 数据库会话
        plan_id: 计划 ID
        status: 状态（可选，用于筛选）
    
    Returns:
        list[Task]: 任务列表（从tasks_v2表转换）
    """
    from models import Task
    from models.task_v2 import TaskV2
    import json
    
    # 查询tasks_v2表
    query_tasks_v2 = select(TaskV2).where(TaskV2.plan_id == plan_id)
    if status:
        # 状态映射：前端状态 -> tasks_v2状态
        status_mapping = {
            "待执行": "pending",
            "执行中": "in_progress",
            "已完成": "completed",
            "已验证": "verified",
            "验证失败": "verification_failed",
            "执行失败": "failed"
        }
        v2_status = status_mapping.get(status, status)
        query_tasks_v2 = query_tasks_v2.where(TaskV2.status == v2_status)
    
    tasks_v2_result = db.execute(query_tasks_v2)
    tasks_v2 = list(tasks_v2_result.scalars().all())
    
    result_tasks = []
    
    # 将TaskV2转换为Task（使用tasks_v2表中的实际数据）
    for task_v2 in tasks_v2:
        # 解析input_data获取描述信息
        description = ""
        requirements = ""
        expected_output = []
        try:
            if task_v2.input_data:
                input_json = json.loads(task_v2.input_data)
                description = input_json.get('description', '')
                requirements = input_json.get('requirements', '')
                expected_output = input_json.get('expected_output_files', [])
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
            plan_date=task_v2.plan_date if hasattr(task_v2, 'plan_date') else task_v2.created_at,
            plan_complete_time=task_v2.plan_complete_time if hasattr(task_v2, 'plan_complete_time') else None,
            executor=task_v2.executor if hasattr(task_v2, 'executor') else "ac-glm5",
            status=task_status,
            priority=task_v2.priority if hasattr(task_v2, 'priority') else "高",
            execution_steps=f"执行{task_v2.task_name}。{description if description else requirements}",
            expected_result=f"成功完成{task_v2.task_name}",
            execution_log=task_v2.execution_log,
            output_result="",
            execution_date=task_v2.execution_date if hasattr(task_v2, 'execution_date') else None,
            verification_result=verification_result,
            verifier=task_v2.verifier if hasattr(task_v2, 'verifier') else None,
            verification_time=task_v2.verification_time if hasattr(task_v2, 'verification_time') else None,
            created_at=task_v2.created_at,
            updated_at=task_v2.updated_at,
            verification_log=task_v2.verification_log,
            exec_start_time=task_v2.exec_start_time if hasattr(task_v2, 'exec_start_time') else None,
            exec_estimated_complete=task_v2.exec_estimated_complete if hasattr(task_v2, 'exec_estimated_complete') else None,
            exec_complete_time=task_v2.exec_complete_time if hasattr(task_v2, 'exec_complete_time') else None,
            verify_start_time=task_v2.verify_start_time if hasattr(task_v2, 'verify_start_time') else None,
            verify_estimated_complete=task_v2.verify_estimated_complete if hasattr(task_v2, 'verify_estimated_complete') else None,
            verify_complete_time=task_v2.verify_complete_time if hasattr(task_v2, 'verify_complete_time') else None,
            agent_id=task_v2.agent_id if hasattr(task_v2, 'agent_id') else None,
            phase_record_id=task_v2.phase_record_id if hasattr(task_v2, 'phase_record_id') else None,
            locked_by=task_v2.locked_by if hasattr(task_v2, 'locked_by') else None,
            locked_at=task_v2.locked_at if hasattr(task_v2, 'locked_at') else None
        )
        result_tasks.append(task)
    
    # 统一排序（按创建时间倒序）
    result_tasks.sort(key=lambda x: x.created_at, reverse=True)
    
    return result_tasks
