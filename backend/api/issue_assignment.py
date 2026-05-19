"""
Issue Assignment 问题分配 API 接口模块
AutoCraft 问题跟踪系统 - Issue Assignment RESTful API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from database import get_db
from services.issue_assignment_service import (
    IssueAssignmentService,
    IssueAssignmentValidationError,
    IssueAssignmentPermissionError
)
from schemas.issue import IssueAssignRequest, IssueResponse, MessageResponse

router = APIRouter(prefix="/issues", tags=["问题分配"])


# ============================================================================
# 依赖注入
# ============================================================================

def get_assignment_service(db: Session = Depends(get_db)) -> IssueAssignmentService:
    """
    获取 Issue 分配服务实例
    
    Args:
        db: 数据库会话
    
    Returns:
        IssueAssignmentService 实例
    """
    return IssueAssignmentService(db)


# ============================================================================
# 分配 Issue（首次分配）
# ============================================================================

@router.post("/{issue_id}/assign", response_model=MessageResponse)
def assign_issue_api(
    issue_id: int,
    request: IssueAssignRequest,
    assigned_by: str,
    service: IssueAssignmentService = Depends(get_assignment_service)
):
    """
    分配 Issue（首次分配）
    
    - 将 Issue 分配给指定处理人
    - 自动变更状态为"处理中"（如果当前状态为"新建"）
    - 自动记录分配日志
    - assigned_by: 分配操作人（从请求头或认证中获取）
    
    权限要求：
    - 项目管理员或 Issue 创建人可以分配
    """
    # 验证 Issue 是否存在（在服务层验证）
    try:
        updated_issue = service.assign_issue(
            issue_id=issue_id,
            assignee=request.assignee,
            assigned_by=assigned_by,
            due_date=request.due_date,
            assign_note=request.assign_note
        )
        
        return MessageResponse(
            message="问题分配成功",
            issue_no=updated_issue.issue_no
        )
    except IssueAssignmentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IssueAssignmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分配问题失败：{str(e)}"
        )


# ============================================================================
# 重新分配 Issue（变更处理人）
# ============================================================================

@router.put("/{issue_id}/assign", response_model=MessageResponse)
def reassign_issue_api(
    issue_id: int,
    request: IssueAssignRequest,
    assigned_by: str,
    service: IssueAssignmentService = Depends(get_assignment_service)
):
    """
    重新分配 Issue（变更处理人）
    
    - 变更 Issue 的处理人
    - 保持状态为"处理中"
    - 自动记录分配日志
    - assigned_by: 分配操作人（从请求头或认证中获取）
    
    权限要求：
    - 项目管理员或 Issue 创建人可以重新分配
    """
    # 验证 Issue 是否存在（在服务层验证）
    try:
        updated_issue = service.reassign_issue(
            issue_id=issue_id,
            new_assignee=request.assignee,
            assigned_by=assigned_by,
            due_date=request.due_date,
            assign_note=request.assign_note
        )
        
        return MessageResponse(
            message="问题重新分配成功",
            issue_no=updated_issue.issue_no
        )
    except IssueAssignmentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except IssueAssignmentPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新分配问题失败：{str(e)}"
        )


# ============================================================================
# 获取分配历史记录
# ============================================================================

@router.get("/{issue_id}/assign/logs", response_model=list)
def get_assignment_logs_api(
    issue_id: int,
    limit: Optional[int] = None,
    service: IssueAssignmentService = Depends(get_assignment_service)
):
    """
    获取 Issue 的分配历史记录
    
    - 返回分配日志列表
    - 按创建时间倒序排列
    - limit: 返回记录数量限制（可选）
    """
    try:
        logs = service.get_assignment_history(issue_id, limit)
        return [
            {
                "id": log.id,
                "issue_id": log.issue_id,
                "from_assignee": log.from_assignee,
                "to_assignee": log.to_assignee,
                "assigned_by": log.assigned_by,
                "due_date": log.due_date.isoformat() if log.due_date else None,
                "note": log.note,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分配历史失败：{str(e)}"
        )


# ============================================================================
# 取消分配
# ============================================================================

@router.delete("/{issue_id}/assign", response_model=MessageResponse)
def unassign_issue_api(
    issue_id: int,
    reason: Optional[str] = None,
    unassigned_by: str = None,
    service: IssueAssignmentService = Depends(get_assignment_service)
):
    """
    取消 Issue 分配
    
    - 清除处理人信息
    - 状态回退到"新建"
    - 自动记录分配日志
    - unassigned_by: 取消分配操作人
    - reason: 取消原因（可选）
    
    权限要求：
    - 项目管理员或 Issue 创建人可以取消分配
    """
    try:
        updated_issue = service.unassign_issue(
            issue_id=issue_id,
            unassigned_by=unassigned_by,
            reason=reason
        )
        
        return MessageResponse(
            message="问题取消分配成功",
            issue_no=updated_issue.issue_no
        )
    except IssueAssignmentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消分配失败：{str(e)}"
        )
