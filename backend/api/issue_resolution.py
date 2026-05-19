"""
Issue 解决 API 接口模块
AutoCraft 问题跟踪系统 - Issue Resolution RESTful API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from crud.issue import (
    get_issue_by_id,
    resolve_issue,
    update_issue
)
from schemas.issue import (
    IssueResolveRequest,
    MessageResponse
)
from models.issue import Issue

router = APIRouter(prefix="/issues", tags=["问题解决"])


# ============================================================================
# 权限校验工具函数
# ============================================================================

def validate_issue_status_for_resolve(issue: Issue) -> None:
    """
    校验 Issue 状态是否允许解决
    
    Args:
        issue: Issue 对象
    
    Raises:
        HTTPException: 如果状态不允许解决
    """
    # 只有"处理中"状态的 Issue 才能被解决
    if issue.status not in ["处理中", "in_progress"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"当前状态（{issue.status}）不允许解决问题，只有'处理中'状态的问题可以被解决"
        )


def validate_issue_assignee(issue: Issue, current_user: str) -> None:
    """
    校验当前用户是否有权解决该 Issue
    
    Args:
        issue: Issue 对象
        current_user: 当前用户
    
    Raises:
        HTTPException: 如果用户无权解决
    """
    # 如果 Issue 已指派，只有被指派人可以解决
    if issue.assignee and issue.assignee != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"您无权解决该问题，该问题已指派给 {issue.assignee} 处理"
        )


def validate_resolution_data(solution: str, solution_process: Optional[str] = None) -> None:
    """
    校验解决数据的完整性
    
    Args:
        solution: 解决方案
        solution_process: 解决过程
    
    Raises:
        HTTPException: 如果数据不完整
    """
    if not solution or not solution.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="解决方案不能为空"
        )
    
    if len(solution) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="解决方案内容过短，请至少提供 10 个字符的详细描述"
        )


# ============================================================================
# 提交解决（POST）
# ============================================================================

@router.post("/{id}/resolve", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def submit_resolution(
    id: int,
    resolution_data: IssueResolveRequest,
    db: Session = Depends(get_db)
):
    """
    提交 Issue 解决方案
    
    - 校验 Issue 是否存在
    - 校验 Issue 状态（必须为"处理中"）
    - 校验权限（只有被指派人或创建人可以解决）
    - 校验解决数据完整性
    - 更新 Issue 状态为"已解决"
    - 记录解决过程、解决方案、解决人、解决时间
    """
    # 1. 校验 Issue 是否存在
    issue = get_issue_by_id(db, id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{id}"
        )
    
    # 2. 校验 Issue 状态
    validate_issue_status_for_resolve(issue)
    
    # 3. 校验权限（被指派人或创建人）
    current_user = resolution_data.resolved_by
    if issue.assignee and issue.assignee != current_user and issue.created_by != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"您无权解决该问题，该问题已指派给 {issue.assignee} 处理，或由 {issue.created_by} 创建"
        )
    
    # 4. 校验解决数据
    validate_resolution_data(resolution_data.solution, resolution_data.solution_process)
    
    # 5. 执行解决操作
    try:
        resolve_issue(
            db=db,
            issue=issue,
            solution=resolution_data.solution,
            solution_process=resolution_data.solution_process,
            resolved_by=resolution_data.resolved_by
        )
        
        return MessageResponse(
            message="问题已成功解决",
            issue_no=issue.issue_no
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解决问题失败：{str(e)}"
        )


# ============================================================================
# 编辑解决（PUT）
# ============================================================================

@router.put("/{id}/resolve", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def update_resolution(
    id: int,
    resolution_data: IssueResolveRequest,
    db: Session = Depends(get_db)
):
    """
    编辑 Issue 解决方案
    
    - 校验 Issue 是否存在
    - 校验 Issue 状态（必须为"已解决"）
    - 校验权限（只有原解决人或被指派人可以编辑）
    - 校验解决数据完整性
    - 更新解决方案和解决过程
    - 保留原解决时间
    """
    # 1. 校验 Issue 是否存在
    issue = get_issue_by_id(db, id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题不存在：{id}"
        )
    
    # 2. 校验 Issue 状态（必须已解决才能编辑解决方案）
    if issue.status not in ["已解决", "resolved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"当前状态（{issue.status}）不允许编辑解决方案，只有'已解决'状态的问题可以编辑解决方案"
        )
    
    # 3. 校验权限（原解决人或被指派人）
    current_user = resolution_data.resolved_by
    if issue.resolved_by and issue.resolved_by != current_user:
        if issue.assignee and issue.assignee != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"您无权编辑该问题的解决方案，该问题由 {issue.resolved_by} 解决"
            )
    
    # 4. 校验解决数据
    validate_resolution_data(resolution_data.solution, resolution_data.solution_process)
    
    # 5. 执行更新操作（保留原解决时间）
    try:
        from datetime import datetime
        
        # 保存原解决时间
        original_resolved_at = issue.resolved_at
        
        # 更新解决方案和过程
        issue.solution = resolution_data.solution
        issue.solution_process = resolution_data.solution_process
        issue.resolved_by = resolution_data.resolved_by
        issue.resolved_at = original_resolved_at  # 保留原解决时间
        issue.updated_at = datetime.now()
        
        db.commit()
        db.refresh(issue)
        
        return MessageResponse(
            message="问题解决方案已更新",
            issue_no=issue.issue_no
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新解决方案失败：{str(e)}"
        )
