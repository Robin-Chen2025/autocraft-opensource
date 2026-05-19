"""
问题状态流转 API 接口模块
AutoCraft 问题跟踪系统 - Issue 状态变更 RESTful API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from database import get_db
from crud.issue import get_issue_by_id, update_issue
from crud.issue_status_log import create_status_log
from schemas.issue import IssueStatus, MessageResponse

router = APIRouter(prefix="/issues", tags=["问题状态管理"])


# ============================================================================
# 状态流转规则定义
# ============================================================================

# 状态流转规则：key=当前状态，value=允许流转的目标状态列表
STATUS_TRANSITION_RULES = {
    "新建": ["处理中", "已关闭"],
    "处理中": ["已解决", "新建"],
    "已解决": ["已关闭", "处理中"],
    "已关闭": ["处理中"],
}

# 状态流转说明
STATUS_TRANSITION_DESCRIPTION = {
    ("新建", "处理中"): "问题开始处理",
    ("新建", "已关闭"): "问题直接关闭（无需处理）",
    ("处理中", "已解决"): "问题已解决",
    ("处理中", "新建"): "问题重新打开",
    ("已解决", "已关闭"): "问题确认关闭",
    ("已解决", "处理中"): "问题重新处理",
    ("已关闭", "处理中"): "问题重新激活",
}


def validate_status_transition(from_status: str, to_status: str) -> tuple[bool, str]:
    """
    校验状态流转是否合法
    
    Args:
        from_status: 当前状态
        to_status: 目标状态
    
    Returns:
        (是否合法，错误信息/说明)
    """
    # 状态相同，不允许
    if from_status == to_status:
        return False, "目标状态与当前状态相同，无需变更"
    
    # 检查流转规则
    allowed_transitions = STATUS_TRANSITION_RULES.get(from_status, [])
    if to_status not in allowed_transitions:
        return False, f"不允许从状态'{from_status}'流转到'{to_status}'，允许的目标状态：{allowed_transitions}"
    
    # 获取流转说明
    transition_desc = STATUS_TRANSITION_DESCRIPTION.get((from_status, to_status), "状态变更")
    return True, transition_desc


# ============================================================================
# 请求/响应模型
# ============================================================================

class IssueStatusChangeRequest(BaseModel):
    """问题状态变更请求模型"""
    to_status: IssueStatus = Field(..., description="目标状态")
    reason: Optional[str] = Field(None, description="变更原因")


class IssueStatusLogResponse(BaseModel):
    """状态变更日志响应模型"""
    id: int = Field(..., description="日志 ID")
    issue_id: int = Field(..., description="Issue ID")
    from_status: str = Field(..., description="变更前状态")
    to_status: str = Field(..., description="变更后状态")
    operator: str = Field(..., description="操作人")
    operator_role: Optional[str] = Field(None, description="操作人角色")
    reason: Optional[str] = Field(None, description="变更原因")
    created_at: datetime = Field(..., description="创建时间")
    
    model_config = {"from_attributes": True}


class IssueStatusLogListResponse(BaseModel):
    """状态变更日志列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: List[IssueStatusLogResponse] = Field(..., description="日志列表")


# ============================================================================
# API 接口
# ============================================================================

@router.post("/{issue_id}/status", response_model=MessageResponse)
def change_issue_status(
    issue_id: int,
    request: IssueStatusChangeRequest,
    db: Session = Depends(get_db),
    operator: Optional[str] = Query(default="system", description="操作人")
):
    """
    变更问题状态
    
    - 校验状态流转规则（新建→处理中→已解决→已关闭）
    - 自动记录状态变更日志
    - 支持指定操作人（默认 system）
    
    状态流转规则：
    - 新建 → 处理中、已关闭
    - 处理中 → 已解决、新建
    - 已解决 → 已关闭、处理中
    - 已关闭 → 处理中
    """
    # 1. 查询 Issue
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{issue_id}"
        )
    
    # 2. 校验状态流转
    from_status = issue.status
    to_status = request.to_status.value if hasattr(request.to_status, 'value') else str(request.to_status)
    
    is_valid, message = validate_status_transition(from_status, to_status)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 3. 更新 Issue 状态
    try:
        from schemas.issue import IssueUpdate
        issue_update = IssueUpdate(status=to_status)
        updated_issue = update_issue(db, issue, issue_update)
        
        # 4. 记录状态变更日志
        create_status_log(
            db=db,
            issue_id=issue_id,
            from_status=from_status,
            to_status=to_status,
            operator=operator,
            reason=request.reason
        )
        
        return MessageResponse(
            message=f"问题状态已更新：{from_status} → {to_status}",
            issue_no=updated_issue.issue_no
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"状态变更失败：{str(e)}"
        )


@router.get("/{issue_id}/status-logs", response_model=IssueStatusLogListResponse)
def get_issue_status_logs(
    issue_id: int,
    limit: Optional[int] = Query(50, ge=1, le=500, description="返回记录数量限制"),
    db: Session = Depends(get_db)
):
    """
    获取问题状态变更日志
    
    - 返回指定 Issue 的状态变更历史
    - 按创建时间倒序排列
    - 默认返回最近 50 条记录
    """
    from crud.issue_status_log import get_status_logs_by_issue_id
    from schemas.issue_status_log import IssueStatusLogResponse
    
    issue = get_issue_by_id(db, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{issue_id}"
        )
    
    try:
        logs = get_status_logs_by_issue_id(db, issue_id, limit=limit)
        return IssueStatusLogListResponse(
            total=len(logs),
            items=[IssueStatusLogResponse.model_validate(log) for log in logs]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取状态日志失败：{str(e)}"
        )
