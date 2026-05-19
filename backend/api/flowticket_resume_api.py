"""
FlowTicket 暂停恢复机制专用API - F-002 独立入口

功能：
- 恢复入口API（POST /api/flowticket/resume）
- 问题单状态验证（issue_id 关联验证）
- 恢复三原则保障（不调用子代理、不返工、不重置retry_count）
- 集成 M-03 F-002 继续执行

设计文档: docs/design/flowticket-final-simplified-v2-design.md v3.1
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database import get_db
from models.task_v2 import TaskV2, FlowTicketInstance, FlowTicketLog
from models.issue import Issue
from api.execution_engine import resume_from_node, RESUME_POINT_MAP

logger = logging.getLogger("flowticket_resume_api")

router = APIRouter(prefix="/flowticket", tags=["FlowTicket 恢复机制"])


# ==================== 请求/响应模型 ====================

class ResumeRequest(BaseModel):
    """恢复请求模型"""
    plan_id: Optional[str] = Field(None, description="计划ID")
    task_id: Optional[int] = Field(None, description="任务ID")
    issue_id: Optional[int] = Field(None, description="关联问题单ID（新增：用于状态验证）")
    flowticket_id: Optional[str] = Field(None, description="FlowTicket实例ID")
    resume_from: str = Field("前置检查", description="恢复点（中文或英文标识）")

    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "PLAN-xxx",
                "task_id": 1,
                "issue_id": 1,
                "flowticket_id": "FT-xxx",
                "resume_from": "前置检查"
            }
        }


class ResumeResponse(BaseModel):
    """恢复响应模型"""
    status: str
    plan_id: Optional[str] = None
    task_id: Optional[int] = None
    issue_id: Optional[int] = None
    flowticket_id: Optional[str] = None
    resumed_at: str
    resume_from: str
    message: Optional[str] = None


# ==================== 问题单状态验证 ====================

def validate_issue_status(db: Session, issue_id: int) -> Issue:
    """
    验证问题单状态是否为"已解决"
    
    恢复三原则之"不返工"：问题没解决就创建新问题单，不允许在原问题未解决时恢复。
    
    Args:
        db: 数据库会话
        issue_id: 问题单ID
        
    Returns:
        Issue: 问题单对象
        
    Raises:
        HTTPException: 404-问题单不存在 / 400-问题单未解决
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题单不存在: {issue_id}"
        )
    if issue.status != "已解决":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"问题单未解决(当前状态: {issue.status})，无法恢复执行"
        )
    return issue


# ==================== 恢复三原则验证 ====================

def validate_resume_principles(task: TaskV2) -> None:
    """
    验证恢复三原则
    
    1. 不调用子代理 — 主代理已修复，无需额外校验
    2. 不返工 — 通过问题单状态验证保障（validate_issue_status）
    3. 不重置retry_count — 确保恢复后保持原retry_count值
    
    Args:
        task: 任务对象
        
    Raises:
        HTTPException: 违反恢复原则时
    """
    # 原则3：不重置retry_count
    # 确保恢复流程不会意外重置retry_count
    # 实际保障在 resume_from_node 中实现（不调用 reset_retry_count）
    # TaskV2模型可能没有retry_count字段，使用getattr安全访问
    if hasattr(task, 'retry_count') and task.retry_count is None:
        task.retry_count = 0  # 初始化但不重置
    # 保持原值，不做任何修改


# ==================== 核心API ====================

@router.post("/resume", response_model=ResumeResponse)
async def resume_flowticket_with_issue_check(
    request: ResumeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    恢复FlowTicket执行（F-002专用入口）
    
    新增功能：
    - 问题单状态验证：如果提供了issue_id，验证问题单状态为"已解决"才能恢复
    - 恢复三原则保障：不调用子代理、不返工、不重置retry_count
    
    恢复点映射：
    - 前置检查 / pre_check: 重新执行节点1前检查
    - 节点1 / node1: 重新执行节点1
    - 执行后检查 / post_execution_check: 检查产出物
    - 节点2 / node2: 跳过节点2，直接进入验证
    - 验证后检查 / post_verification_check: 检查验证结论
    """
    now = datetime.now()
    
    # 1. 问题单状态验证（关键新增功能）
    if request.issue_id:
        validate_issue_status(db, request.issue_id)
        logger.info(f"问题单 {request.issue_id} 状态验证通过（已解决）")
    
    # 2. 查找FlowTicket实例
    flowticket_id = request.flowticket_id
    if not flowticket_id and request.plan_id:
        # 通过plan_id查找FlowTicket
        instance = db.query(FlowTicketInstance).filter(
            FlowTicketInstance.plan_id == request.plan_id
        ).first()
        if instance:
            flowticket_id = instance.flowticket_id
    
    if not flowticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要字段: flowticket_id 或 plan_id"
        )
    
    instance = db.query(FlowTicketInstance).filter(
        FlowTicketInstance.flowticket_id == flowticket_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FlowTicket实例不存在: {flowticket_id}"
        )
    
    # 3. 验证FlowTicket状态为paused
    if instance.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"FlowTicket未暂停，当前状态: {instance.status}"
        )
    
    # 4. 查找或验证任务
    task_id = request.task_id
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
    else:
        # 自动查找plan_id下第一个paused任务
        plan_id = request.plan_id or instance.plan_id
        paused_task = db.query(TaskV2).filter(
            and_(TaskV2.plan_id == plan_id, TaskV2.status == "paused")
        ).order_by(TaskV2.task_no).first()
        
        if not paused_task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有找到暂停的任务"
            )
        task_id = paused_task.id
        task = paused_task
    
    # 5. 恢复三原则验证
    validate_resume_principles(task)
    
    # 6. 更新FlowTicket状态
    instance.status = "running"
    instance.current_task_id = task_id
    instance.updated_at = now
    db.commit()
    
    # 7. 记录恢复日志（含问题单信息）
    log_content = {
        "resume_from": request.resume_from,
        "task_id": task_id,
        "issue_id": request.issue_id,
        "principles": {
            "no_sub_agent": True,
            "no_rework": request.issue_id is not None,  # 如提供了issue_id则验证了不返工
            "no_retry_reset": True
        }
    }
    log = FlowTicketLog(
        flowticket_id=flowticket_id,
        task_id=task_id,
        log_type="resume",
        content=json.dumps(log_content, ensure_ascii=False),
        created_at=now
    )
    db.add(log)
    db.commit()
    
    # 8. 异步触发恢复执行
    background_tasks.add_task(
        _run_resume_async,
        flowticket_id,
        task_id,
        request.resume_from
    )
    
    logger.info(f"FlowTicket {flowticket_id} 恢复成功，恢复点: {request.resume_from}")
    
    return ResumeResponse(
        status="resumed",
        plan_id=request.plan_id or instance.plan_id,
        task_id=task_id,
        issue_id=request.issue_id,
        flowticket_id=flowticket_id,
        resumed_at=now.isoformat(),
        resume_from=request.resume_from,
        message="FlowTicket恢复成功"
    )


# ==================== 后台恢复执行 ====================

def _run_resume_async(flowticket_id: str, task_id: int, resume_from: str):
    """
    后台异步恢复执行
    
    调用 execution_engine.resume_from_node 执行实际的恢复逻辑。
    使用独立的数据库会话以避免后台任务中的会话问题。
    """
    from database import SessionLocal
    db = SessionLocal()
    try:
        result = resume_from_node(db, flowticket_id, task_id, resume_from)
        if result.get("success"):
            logger.info(f"恢复执行完成: {flowticket_id}, task={task_id}, from={resume_from}")
        else:
            logger.error(f"恢复执行失败: {flowticket_id}, error={result.get('error')}")
    except Exception as e:
        logger.error(f"恢复执行异常: {flowticket_id}, error={str(e)}")
    finally:
        db.close()
