"""
数据库 CRUD 操作模块
"""
import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, select
from models import Task
from models.task_v2 import TaskV2  # 使用TaskV2模型
from schemas import TaskCreate, TaskUpdate, TaskQueryParams
from utils import generate_task_no

# ============================================
# 兼容层：所有操作都使用tasks_v2表
# ============================================


def create_task(db: Session, task_data: TaskCreate) -> Task:
    """创建任务"""
    db_task = Task(
        task_no=task_data.task_no or generate_task_no(),
        plan_id=task_data.plan_id,
        task_name=task_data.task_name,
        task_type=task_data.task_type,
        plan_date=task_data.plan_date,
        plan_complete_time=task_data.plan_complete_time,
        executor=task_data.executor,
        status=task_data.status or "pending",
        priority=task_data.priority or "medium",
        execution_steps=task_data.execution_steps,
        expected_result=task_data.expected_result,
        execution_log=task_data.execution_log,
        output_result=task_data.output_result,
        execution_date=task_data.execution_date,
        verification_result=task_data.verification_result or "待验证",
        verifier=task_data.verifier,
        verification_time=task_data.verification_time,
        exec_start_time=task_data.exec_start_time,
        exec_estimated_complete=task_data.exec_estimated_complete,
        exec_complete_time=task_data.exec_complete_time,
        verify_start_time=task_data.verify_start_time,
        verify_estimated_complete=task_data.verify_estimated_complete,
        verify_complete_time=task_data.verify_complete_time,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_no(db: Session, task_no: str) -> Optional[TaskV2]:
    """根据任务单号获取任务（兼容层 - 查询tasks_v2表）"""
    return db.query(TaskV2).filter(TaskV2.task_no == task_no).first()


def get_task_by_id(db: Session, task_id: int) -> Optional[TaskV2]:
    """根据任务ID获取任务（兼容层 - 查询tasks_v2表）"""
    return db.query(TaskV2).filter(TaskV2.id == task_id).first()


def get_tasks(db: Session, params: TaskQueryParams) -> tuple[list[Task], int]:
    """
    获取任务列表（支持分页和多字段组合搜索）
    返回: (任务列表, 总记录数)
    """
    query = db.query(Task)

    # 关键词搜索（任务名称）
    if params.keyword:
        query = query.filter(Task.task_name.contains(params.keyword))

    # 任务单号搜索
    if params.task_no:
        query = query.filter(Task.task_no.contains(params.task_no))

    # 执行人搜索
    if params.executor:
        query = query.filter(Task.executor.contains(params.executor))

    # 验证人搜索
    if params.verifier:
        query = query.filter(Task.verifier.contains(params.verifier))

    # 状态筛选（支持多值，逗号分隔）
    if params.status:
        status_list = [s.strip() for s in params.status.split(',') if s.strip()]
        if len(status_list) == 1:
            query = query.filter(Task.status == status_list[0])
        elif len(status_list) > 1:
            query = query.filter(Task.status.in_(status_list))

    # 优先级筛选（支持多值，逗号分隔）
    if params.priority:
        priority_list = [p.strip() for p in params.priority.split(',') if p.strip()]
        if len(priority_list) == 1:
            query = query.filter(Task.priority == priority_list[0])
        elif len(priority_list) > 1:
            query = query.filter(Task.priority.in_(priority_list))

    # 验证结论筛选（支持多值，逗号分隔）
    if params.verification_result:
        result_list = [r.strip() for r in params.verification_result.split(',') if r.strip()]
        if len(result_list) == 1:
            query = query.filter(Task.verification_result == result_list[0])
        elif len(result_list) > 1:
            query = query.filter(Task.verification_result.in_(result_list))

    # 计划日期范围查询
    if params.plan_date_start:
        query = query.filter(Task.plan_date >= params.plan_date_start)
    if params.plan_date_end:
        query = query.filter(Task.plan_date <= params.plan_date_end)

    # 计划完成时间范围查询
    if params.plan_complete_start:
        query = query.filter(Task.plan_complete_time >= params.plan_complete_start)
    if params.plan_complete_end:
        query = query.filter(Task.plan_complete_time <= params.plan_complete_end)

    # 验证时间范围查询
    if params.verification_time_start:
        query = query.filter(Task.verification_time >= params.verification_time_start)
    if params.verification_time_end:
        query = query.filter(Task.verification_time <= params.verification_time_end)

    # 执行开始时间范围查询
    if params.exec_start_time_start:
        # 将 ISO 8601 格式的 T 替换为空格，以匹配数据库存储格式
        start_time = params.exec_start_time_start.replace('T', ' ')
        query = query.filter(Task.exec_start_time >= start_time)
    if params.exec_start_time_end:
        end_time = params.exec_start_time_end.replace('T', ' ')
        query = query.filter(Task.exec_start_time <= end_time)

    # 执行完成时间范围查询
    if params.exec_complete_time_start:
        start_time = params.exec_complete_time_start.replace('T', ' ')
        query = query.filter(Task.exec_complete_time >= start_time)
    if params.exec_complete_time_end:
        end_time = params.exec_complete_time_end.replace('T', ' ')
        query = query.filter(Task.exec_complete_time <= end_time)

    # 验证开始时间范围查询
    if params.verify_start_time_start:
        start_time = params.verify_start_time_start.replace('T', ' ')
        query = query.filter(Task.verify_start_time >= start_time)
    if params.verify_start_time_end:
        end_time = params.verify_start_time_end.replace('T', ' ')
        query = query.filter(Task.verify_start_time <= end_time)

    # 验证完成时间范围查询
    if params.verify_complete_time_start:
        start_time = params.verify_complete_time_start.replace('T', ' ')
        query = query.filter(Task.verify_complete_time >= start_time)
    if params.verify_complete_time_end:
        end_time = params.verify_complete_time_end.replace('T', ' ')
        query = query.filter(Task.verify_complete_time <= end_time)

    # 计算总记录数
    total = query.count()

    # 分页和排序（按创建时间倒序）
    offset = (params.page - 1) * params.page_size
    tasks = query.order_by(desc(Task.created_at)).offset(offset).limit(params.page_size).all()

    return tasks, total


def update_task(db: Session, task: TaskV2, task_update: TaskUpdate) -> TaskV2:
    """更新任务（兼容层 - 操作tasks_v2表）"""
    update_data = task_update.model_dump(exclude_unset=True)
    
    # 状态变更时自动设置时间
    new_status = update_data.get('status')
    if new_status:
        # ===== execution_log 校验 =====
        # 状态从"进行中"变为"待验证"或"已完成"时，检查execution_log非空
        old_status = task.status
        in_progress_states = ['executing', 'in_progress']
        target_states = ['pending_verification', 'completed', 'verified']
        
        if old_status in in_progress_states and new_status in target_states:
            execution_log = update_data.get('execution_log') or task.execution_log
            if not execution_log or (isinstance(execution_log, str) and execution_log.strip() == ''):
                raise ValueError("执行日志(execution_log)不能为空，请填写执行过程记录")
        # ===== 校验结束 =====
    
    # 更新时间
    update_data['updated_at'] = datetime.now()

    # 更新字段
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: TaskV2) -> None:
    """删除任务（兼容层 - 操作tasks_v2表）"""
    db.delete(task)
    db.commit()


def task_exists(db: Session, task_no: str) -> bool:
    """检查任务是否存在（兼容层 - 查询tasks_v2表）"""
    return db.query(TaskV2).filter(TaskV2.task_no == task_no).first() is not None


def get_tasks_by_plan(db: Session, plan_id: str, status: Optional[str] = None) -> list[TaskV2]:
    """
    按工作计划查询任务（兼容层 - 查询tasks_v2表）
    
    Args:
        db: 数据库会话
        plan_id: 工作计划 ID
        status: 可选的状态筛选
    
    Returns:
        任务列表
    """
    query = db.query(TaskV2).filter(TaskV2.plan_id == plan_id)
    if status:
        query = query.filter(TaskV2.status == status)
    return query.order_by(TaskV2.created_at.desc()).all()


def lock_task(db: Session, task_no: str, agent_id: str) -> dict:
    """
    锁定任务（兼容层 - 操作tasks_v2表）
    返回：{"success": bool, "locked_by": str, "locked_at": datetime, "error": str}
    """
    task = get_task_by_no(db, task_no)
    if not task:
        return {"success": False, "error": "任务不存在"}
    
    if task.locked_by:
        return {
            "success": False, 
            "error": "任务已被锁定", 
            "locked_by": task.locked_by, 
            "locked_at": task.locked_at
        }
    
    task.locked_by = agent_id
    task.locked_at = datetime.now()
    task.updated_at = datetime.now()
    db.commit()
    db.refresh(task)
    
    return {"success": True, "locked_by": agent_id, "locked_at": task.locked_at}


def unlock_task(db: Session, task_no: str, agent_id: str) -> dict:
    """
    解锁任务（兼容层 - 操作tasks_v2表）
    只有锁定者才能解锁
    返回：{"success": bool, "error": str}
    """
    task = get_task_by_no(db, task_no)
    if not task:
        return {"success": False, "error": "任务不存在"}
    
    if not task.locked_by:
        return {"success": False, "error": "任务未被锁定"}
    
    if task.locked_by != agent_id:
        return {"success": False, "error": f"只有锁定者 ({task.locked_by}) 才能解锁"}
    
    task.locked_by = None
    task.locked_at = None
    task.updated_at = datetime.now()
    db.commit()
    
    return {"success": True}


def update_task_verification(db: Session, task_no: str, verification_result: str, 
                             verification_log: str = None, verifier: str = None,
                             cascade_update: bool = False) -> Optional[TaskV2]:
    """
    更新任务验证信息，自动更新任务状态（兼容层 - 操作tasks_v2表）
    
    验证结果支持：
    - 中文：通过 / 不通过
    - 英文：pass / fail
    
    cascade_update: 是否级联更新上级状态（默认 False，由代理决定）
    """
    task = get_task_by_no(db, task_no)
    if not task:
        return None
    
    # 统一验证结果为中文
    result_normalized = verification_result.lower() if verification_result else ""
    if result_normalized in ["通过", "pass", "passed"]:
        task.verification_result = "通过"
        task.status = "verified"  # 使用tasks_v2表的状态
    elif result_normalized in ["不通过", "fail", "failed"]:
        task.verification_result = "不通过"
        task.status = "verification_failed"  # 使用tasks_v2表的状态
    else:
        task.verification_result = verification_result
        task.status = "verification_failed"
    
    # 更新验证日志（使用verification_log字段）
    if task.verification_log:
        # 如果已有验证日志，追加新日志
        try:
            existing_log = task.verification_log if isinstance(task.verification_log, dict) else json.loads(task.verification_log)
        except:
            existing_log = {}
        existing_log['latest'] = {
            'result': verification_result,
            'log': verification_log,
            'verifier': verifier,
            'time': datetime.now().isoformat()
        }
        task.verification_log = json.dumps(existing_log, ensure_ascii=False)
    else:
        # 创建新的验证日志
        task.verification_log = json.dumps({
            'latest': {
                'result': verification_result,
                'log': verification_log,
                'verifier': verifier,
                'time': datetime.now().isoformat()
            }
        }, ensure_ascii=False)
    
    # 更新时间
    task.updated_at = datetime.now()
    db.commit()
    db.refresh(task)
    
    # 级联更新上级状态（可选，由代理决定是否调用）
    if cascade_update:
        try:
            from crud.status_update import cascade_status_update
            cascade_status_update(db, task_no)
        except Exception as e:
            print(f"级联状态更新失败: {e}")
    
    return task
