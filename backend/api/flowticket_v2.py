"""
FlowTicket v2 API实现
"""
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database import get_db
from models.task_v2 import TaskV2, FlowTicketInstance, FlowTicketLog
from api.execution_engine import (
    execute_plan_decompose_task as engine_execute_plan_decompose,
    execute_system_task as engine_execute_system_task,
    resume_from_node,
    add_log as engine_add_log,
)
import logging

# 创建路由
router = APIRouter(prefix="/api/v2/flowticket", tags=["FlowTicket v2 API"])


def generate_flowticket_id() -> str:
    """生成FlowTicket实例ID"""
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"FT-{date_str}-{unique_id}"


@router.post("/start", response_model=Dict[str, Any])
async def start_flowticket(
    start_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    启动FlowTicket执行
    
    参数:
    - plan_id: 工作计划ID（必填）
    - flowticket_id: FlowTicket实例ID（可选，不提供则自动生成）
    """
    plan_id = start_data.get("plan_id")
    if not plan_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要字段: plan_id"
        )
    
    # 生成或使用提供的flowticket_id
    flowticket_id = start_data.get("flowticket_id", generate_flowticket_id())
    
    # 检查是否已存在
    existing_instance = db.query(FlowTicketInstance).filter(
        FlowTicketInstance.flowticket_id == flowticket_id
    ).first()
    
    if existing_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"FlowTicket实例已存在: {flowticket_id}"
        )
    
    # 查询计划单对应的任务
    tasks = db.query(TaskV2).filter(TaskV2.plan_id == plan_id).all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"计划单不存在或没有任务: plan_id={plan_id}"
        )
    
    # 创建FlowTicket实例
    instance = FlowTicketInstance(
        flowticket_id=flowticket_id,
        plan_id=plan_id,
        status="running",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # 查找计划拆解任务（000）
    plan_decompose_task = None
    for task in tasks:
        if task.task_no == "000":
            plan_decompose_task = task
            break
    
    # 设置当前任务
    if plan_decompose_task:
        instance.current_task_id = plan_decompose_task.id
    
    # 保存实例
    db.add(instance)
    db.commit()
    db.refresh(instance)
    
    # 记录启动日志
    log = FlowTicketLog(
        flowticket_id=flowticket_id,
        log_type="start",
        content=json.dumps({
            "plan_id": plan_id,
            "task_count": len(tasks),
            "has_plan_decompose": plan_decompose_task is not None
        }, ensure_ascii=False),
        created_at=datetime.now()
    )
    db.add(log)
    db.commit()
    
    # 如果是计划拆解任务，开始执行
    if plan_decompose_task:
        background_tasks.add_task(
            _run_plan_decompose,
            flowticket_id,
            plan_decompose_task.id
        )
    
    return {
        "status": "success",
        "flowticket_id": flowticket_id,
        "message": "FlowTicket启动成功",
        "next_action": "开始执行计划拆解任务(000)" if plan_decompose_task else "开始执行系统任务",
        "task_count": len(tasks),
        "created_at": instance.created_at.isoformat()
    }


@router.get("/status", response_model=Dict[str, Any])
async def get_flowticket_status(
    flowticket_id: str,
    db: Session = Depends(get_db)
):
    """
    查询FlowTicket执行状态
    """
    instance = db.query(FlowTicketInstance).filter(
        FlowTicketInstance.flowticket_id == flowticket_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FlowTicket实例不存在: {flowticket_id}"
        )
    
    # 查询任务进度
    tasks = db.query(TaskV2).filter(TaskV2.plan_id == instance.plan_id).all()
    
    status_counts = {
        "pending": 0,
        "in_progress": 0,
        "pending_verification": 0,
        "completed": 0,
        "paused": 0,
        "failed": 0
    }
    
    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
    
    total_tasks = len(tasks)
    completed_tasks = status_counts["completed"]
    
    # 获取当前任务信息
    current_task_info = None
    if instance.current_task_id:
        current_task = db.query(TaskV2).filter(TaskV2.id == instance.current_task_id).first()
        if current_task:
            current_task_info = {
                "task_id": current_task.id,
                "task_no": current_task.task_no,
                "task_name": current_task.task_name,
                "status": current_task.status
            }
    
    # 获取最近日志
    recent_logs = db.query(FlowTicketLog).filter(
        FlowTicketLog.flowticket_id == flowticket_id
    ).order_by(FlowTicketLog.created_at.desc()).limit(5).all()
    
    return {
        "status": "success",
        "flowticket_id": flowticket_id,
        "plan_id": instance.plan_id,
        "flowticket_status": instance.status,
        "current_task": current_task_info,
        "progress": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": status_counts["pending"],
            "in_progress_tasks": status_counts["in_progress"],
            "pending_verification_tasks": status_counts["pending_verification"],
            "paused_tasks": status_counts["paused"],
            "failed_tasks": status_counts["failed"],
            "completion_rate": round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0
        },
        "recent_logs": [
            {
                "log_type": log.log_type,
                "content": json.loads(log.content) if log.content else {},
                "created_at": log.created_at.isoformat()
            }
            for log in recent_logs
        ],
        "started_at": instance.created_at.isoformat(),
        "updated_at": instance.updated_at.isoformat()
    }


@router.post("/resume", response_model=Dict[str, Any])
async def resume_flowticket(
    resume_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    手动恢复FlowTicket执行
    """
    flowticket_id = resume_data.get("flowticket_id")
    if not flowticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要字段: flowticket_id"
        )
    
    instance = db.query(FlowTicketInstance).filter(
        FlowTicketInstance.flowticket_id == flowticket_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FlowTicket实例不存在: {flowticket_id}"
        )
    
    # 验证状态
    if instance.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"FlowTicket未暂停，当前状态: {instance.status}"
        )
    
    task_id = resume_data.get("task_id")
    resume_from = resume_data.get("resume_from", "前置检查")
    
    # 如果指定了task_id，验证任务存在且状态为paused
    if task_id:
        task = db.query(TaskV2).filter(TaskV2.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务不存在: task_id={task_id}"
            )
        
        if task.status != "paused":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"任务未暂停，当前状态: {task.status}"
            )
        
        instance.current_task_id = task_id
    else:
        # 如果没有指定task_id，找到第一个paused状态的任务
        paused_task = db.query(TaskV2).filter(
            and_(TaskV2.plan_id == instance.plan_id, TaskV2.status == "paused")
        ).order_by(TaskV2.task_no).first()
        
        if not paused_task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有找到暂停的任务"
            )
        
        instance.current_task_id = paused_task.id
    
    # 更新FlowTicket状态
    instance.status = "running"
    instance.updated_at = datetime.now()
    db.commit()
    
    # 记录恢复日志
    log = FlowTicketLog(
        flowticket_id=flowticket_id,
        task_id=instance.current_task_id,
        log_type="resume",
        content=json.dumps({
            "resume_from": resume_from,
            "task_id": instance.current_task_id
        }, ensure_ascii=False),
        created_at=datetime.now()
    )
    db.add(log)
    db.commit()
    
    # 在后台恢复执行
    background_tasks.add_task(
        _run_resume,
        flowticket_id,
        instance.current_task_id,
        resume_from
    )
    
    return {
        "status": "success",
        "flowticket_id": flowticket_id,
        "resumed_task_id": instance.current_task_id,
        "resume_from": resume_from,
        "message": "FlowTicket恢复成功"
    }


@router.post("/cancel", response_model=Dict[str, Any])
async def cancel_flowticket(
    cancel_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    强制取消FlowTicket执行
    """
    flowticket_id = cancel_data.get("flowticket_id")
    if not flowticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要字段: flowticket_id"
        )
    
    instance = db.query(FlowTicketInstance).filter(
        FlowTicketInstance.flowticket_id == flowticket_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FlowTicket实例不存在: {flowticket_id}"
        )
    
    # 更新FlowTicket状态
    instance.status = "failed"
    instance.updated_at = datetime.now()
    
    # 更新所有进行中任务状态为failed
    tasks_to_cancel = db.query(TaskV2).filter(
        and_(
            TaskV2.plan_id == instance.plan_id,
            TaskV2.status.in_(["pending", "in_progress", "pending_verification", "paused"])
        )
    ).all()
    
    canceled_count = 0
    for task in tasks_to_cancel:
        task.status = "failed"
        task.updated_at = datetime.now()
        canceled_count += 1
    
    db.commit()
    
    # 记录取消日志
    log = FlowTicketLog(
        flowticket_id=flowticket_id,
        log_type="cancel",
        content=json.dumps({
            "canceled_tasks": canceled_count,
            "total_tasks": len(tasks_to_cancel)
        }, ensure_ascii=False),
        created_at=datetime.now()
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "success",
        "flowticket_id": flowticket_id,
        "message": "FlowTicket已取消",
        "canceled_tasks": canceled_count
    }


# ==================== 后台任务函数 ====================

def _get_db_session():
    """Get a fresh DB session for background tasks."""
    from database import SessionLocal
    return SessionLocal()


def _run_plan_decompose(flowticket_id: str, task_id: int):
    """Run plan decompose in background with fresh DB session."""
    db = _get_db_session()
    try:
        result = engine_execute_plan_decompose(db, flowticket_id, task_id)
        logger.info(f"Plan decompose result: {result}")
    except Exception as e:
        logger.error(f"Plan decompose error: {e}")
    finally:
        db.close()


def _run_resume(flowticket_id: str, task_id: int, resume_from: str):
    """Run resume in background with fresh DB session."""
    db = _get_db_session()
    try:
        result = resume_from_node(db, flowticket_id, task_id, resume_from)
        logger.info(f"Resume result: {result}")
    except Exception as e:
        logger.error(f"Resume error: {e}")
    finally:
        db.close()


logger = logging.getLogger("flowticket_v2")
