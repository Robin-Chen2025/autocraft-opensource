"""
Issue Summary 问题总结 API 接口模块
AutoCraft 问题跟踪系统 - Issue Summary RESTful API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from crud.issue_summary import (
    create_summary,
    get_summary_by_issue_id,
    update_summary,
    summary_exists
)
from schemas.issue_summary import (
    IssueSummaryCreate,
    IssueSummaryUpdate,
    IssueSummaryResponse,
    IssueSummaryDetailResponse,
    MessageResponse
)
from models.issue_summary import IssueSummary

router = APIRouter(prefix="/issues", tags=["问题总结"])


# ============================================================================
# 权限校验工具函数
# ============================================================================

def validate_summary_not_exists(issue_id: int, db: Session) -> None:
    """
    校验 Issue 是否已有总结
    
    Args:
        issue_id: Issue ID
        db: 数据库会话
    
    Raises:
        HTTPException: 如果已有总结
    """
    if summary_exists(db, issue_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"问题 {issue_id} 已有总结，请使用 PUT 方法编辑总结"
        )


def validate_summary_exists(issue_id: int, db: Session) -> IssueSummary:
    """
    校验 Issue 是否有总结
    
    Args:
        issue_id: Issue ID
        db: 数据库会话
    
    Returns:
        IssueSummary 对象
    
    Raises:
        HTTPException: 如果没有总结
    """
    summary = get_summary_by_issue_id(db, issue_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"问题 {issue_id} 暂无总结，请先使用 POST 方法创建总结"
        )
    return summary


def validate_summary_data(summary_data: IssueSummaryCreate) -> None:
    """
    校验总结数据的完整性
    
    Args:
        summary_data: IssueSummaryCreate 对象
    
    Raises:
        HTTPException: 如果数据不完整
    """
    # 至少需要一个字段有内容
    if not any([
        summary_data.root_cause,
        summary_data.solution_approach,
        summary_data.lessons_learned,
        summary_data.prevention_measures
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="总结内容不能为空，请至少提供根因、解决思路、经验教训或预防措施中的一项"
        )


# ============================================================================
# 提交总结（POST）
# ============================================================================

@router.post("/{id}/summary", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def submit_summary(
    id: int,
    summary_data: IssueSummaryCreate,
    db: Session = Depends(get_db)
):
    """
    提交 Issue 问题总结
    
    - 校验 Issue 是否存在总结（不能重复创建）
    - 校验总结数据完整性（至少需要一个字段有内容）
    - 创建问题总结记录
    - 记录根因、解决思路、经验教训、预防措施、相关资源
    """
    # 1. 校验是否已有总结
    validate_summary_not_exists(id, db)
    
    # 2. 校验总结数据
    validate_summary_data(summary_data)
    
    # 3. 创建总结
    try:
        summary = create_summary(db, summary_data)
        
        return MessageResponse(
            message="问题总结创建成功",
            issue_no=f"ISSUE-{id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建问题总结失败：{str(e)}"
        )


# ============================================================================
# 编辑总结（PUT）
# ============================================================================

@router.put("/{id}/summary", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def update_summary_api(
    id: int,
    summary_update: IssueSummaryUpdate,
    db: Session = Depends(get_db)
):
    """
    编辑 Issue 问题总结
    
    - 校验 Issue 是否有总结（没有则不能编辑）
    - 校验总结数据完整性
    - 更新问题总结记录
    - 保留原总结时间，更新修改时间
    """
    # 1. 校验总结是否存在
    summary = validate_summary_exists(id, db)
    
    # 2. 校验更新数据（至少需要一个字段）
    update_data = summary_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新内容不能为空"
        )
    
    # 3. 更新总结
    try:
        update_summary(db, summary, summary_update)
        
        return MessageResponse(
            message="问题总结更新成功",
            issue_no=f"ISSUE-{id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新问题总结失败：{str(e)}"
        )


# ============================================================================
# 获取总结（GET）
# ============================================================================

@router.get("/{id}/summary", response_model=IssueSummaryDetailResponse, status_code=status.HTTP_200_OK)
def get_summary_api(
    id: int,
    db: Session = Depends(get_db)
):
    """
    获取 Issue 问题总结
    
    - 校验 Issue 是否有总结
    - 返回完整的总结信息
    - 包含根因、解决思路、经验教训、预防措施、相关资源
    """
    # 1. 校验总结是否存在
    summary = validate_summary_exists(id, db)
    
    # 2. 返回总结详情
    try:
        return IssueSummaryDetailResponse(
            data=IssueSummaryResponse.model_validate(summary)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取问题总结失败：{str(e)}"
        )
