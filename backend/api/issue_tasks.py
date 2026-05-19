"""
Issue Task Relation 管理 API 接口模块
AutoCraft 问题跟踪系统 - Issue 与 Task 关联关系 RESTful API
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from crud.issue_task_relation import (
    create_relation,
    get_relations_by_issue_id,
    delete_relation,
    get_relation
)
from crud.task import get_task_by_id
from crud.issue import get_issue_by_id
from schemas.issue import IssueResponse, MessageResponse
from schemas.task_models import TaskResponse

router = APIRouter(prefix="/issues", tags=["问题任务关联"])


# ============================================================================
# 请求/响应模型
# ============================================================================

class IssueTaskRelationResponse(BaseModel):
    """Issue 与 Task 关联关系响应模型"""
    id: int = Field(..., description="关联关系 ID")
    issue_id: int = Field(..., description="Issue ID")
    task_id: int = Field(..., description="Task ID")
    created_by: str = Field(..., description="创建人")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class TaskInfo(BaseModel):
    """任务基本信息响应模型"""
    id: int = Field(..., description="任务 ID")
    task_no: str = Field(..., description="任务单号")
    task_name: str = Field(..., description="任务名称")
    status: str = Field(..., description="任务状态")
    priority: str = Field(..., description="优先级")
    executor: Optional[str] = Field(None, description="执行人")

    model_config = ConfigDict(from_attributes=True)


class IssueTaskListResponse(BaseModel):
    """Issue 关联任务列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: List[TaskInfo] = Field(..., description="任务列表")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 关联任务
# ============================================================================

@router.post("/{issue_id}/tasks", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def link_task_to_issue(
    issue_id: int,
    task_id: int,
    created_by: str,
    db: Session = Depends(get_db)
):
    """
    关联任务到 Issue

    - 验证 Issue 是否存在
    - 验证 Task 是否存在
    - 验证关联是否已存在
    - 创建关联关系
    """
    # 验证 Issue 是否存在
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{issue_id}"
        )

    # 验证 Task 是否存在
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在：{task_id}"
        )

    # 检查关联是否已存在
    existing = get_relation(db, issue_id, task_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"问题与任务的关联已存在：issue_id={issue_id}, task_id={task_id}"
        )

    try:
        relation = create_relation(db, issue_id, task_id, created_by)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建关联关系失败"
            )
        return MessageResponse(
            message="任务关联成功",
            issue_no=issue.issue_no
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"关联任务失败：{str(e)}"
        )


# ============================================================================
# 取消关联
# ============================================================================

@router.delete("/{issue_id}/tasks/{task_id}", response_model=MessageResponse)
def unlink_task_from_issue(
    issue_id: int,
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    取消 Issue 与 Task 的关联

    - 验证 Issue 是否存在
    - 验证 Task 是否存在
    - 验证关联是否存在
    - 删除关联关系
    """
    # 验证 Issue 是否存在
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{issue_id}"
        )

    # 验证 Task 是否存在
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在：{task_id}"
        )

    # 检查关联是否存在
    relation = get_relation(db, issue_id, task_id)
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题与任务的关联不存在：issue_id={issue_id}, task_id={task_id}"
        )

    try:
        success = delete_relation(db, issue_id, task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除关联关系失败"
            )
        return MessageResponse(
            message="任务取消关联成功",
            issue_no=issue.issue_no
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消关联失败：{str(e)}"
        )


# ============================================================================
# 获取关联任务列表
# ============================================================================

@router.get("/{issue_id}/tasks", response_model=IssueTaskListResponse)
def get_issue_tasks(
    issue_id: int,
    db: Session = Depends(get_db)
):
    """
    获取 Issue 关联的任务列表

    - 验证 Issue 是否存在
    - 返回关联任务的基本信息
    - 按创建时间倒序排列
    """
    # 验证 Issue 是否存在
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{issue_id}"
        )

    try:
        relations = get_relations_by_issue_id(db, issue_id)
        
        # 提取任务信息
        tasks = []
        for relation in relations:
            task = get_task_by_id(db, relation.task_id)
            if task:
                tasks.append(TaskInfo(
                    id=task.id,
                    task_no=task.task_no,
                    task_name=task.task_name,
                    status=task.status,
                    priority=task.priority,
                    executor=task.executor
                ))
        
        return IssueTaskListResponse(
            total=len(tasks),
            items=tasks
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取关联任务列表失败：{str(e)}"
        )
