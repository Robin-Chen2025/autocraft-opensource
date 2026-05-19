"""
Issue Status Log 数据库 CRUD 操作模块
AutoCraft 问题跟踪系统 - Issue 状态变更日志数据操作层
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.issue_status_log import IssueStatusLog


def create_status_log(
    db: Session,
    issue_id: int,
    from_status: str,
    to_status: str,
    operator: str,
    operator_role: Optional[str] = None,
    reason: Optional[str] = None
) -> IssueStatusLog:
    """
    创建 Issue 状态变更日志
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
        from_status: 变更前的状态
        to_status: 变更后的状态
        operator: 操作人
        operator_role: 操作人角色（可选）
        reason: 变更原因（可选）
    
    Returns:
        创建的 IssueStatusLog 对象
    """
    db_status_log = IssueStatusLog(
        issue_id=issue_id,
        from_status=from_status,
        to_status=to_status,
        operator=operator,
        operator_role=operator_role,
        reason=reason,
        created_at=datetime.now()
    )
    db.add(db_status_log)
    db.commit()
    db.refresh(db_status_log)
    return db_status_log


def get_status_logs_by_issue_id(
    db: Session,
    issue_id: int,
    limit: Optional[int] = None
) -> List[IssueStatusLog]:
    """
    根据 Issue ID 获取状态变更日志列表
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
        limit: 返回记录数量限制（可选，默认返回全部）
    
    Returns:
        IssueStatusLog 列表，按创建时间倒序排列
    """
    query = db.query(IssueStatusLog).filter(
        IssueStatusLog.issue_id == issue_id
    )
    
    if limit is not None and limit > 0:
        query = query.limit(limit)
    
    return query.order_by(desc(IssueStatusLog.created_at)).all()


def get_status_log_by_id(db: Session, log_id: int) -> Optional[IssueStatusLog]:
    """
    根据日志 ID 获取状态变更日志
    
    Args:
        db: 数据库会话
        log_id: 日志 ID
    
    Returns:
        IssueStatusLog 对象，不存在则返回 None
    """
    return db.query(IssueStatusLog).filter(IssueStatusLog.id == log_id).first()


def get_status_logs_by_operator(
    db: Session,
    operator: str,
    limit: Optional[int] = None
) -> List[IssueStatusLog]:
    """
    根据操作人获取状态变更日志列表
    
    Args:
        db: 数据库会话
        operator: 操作人
        limit: 返回记录数量限制（可选，默认返回全部）
    
    Returns:
        IssueStatusLog 列表，按创建时间倒序排列
    """
    query = db.query(IssueStatusLog).filter(
        IssueStatusLog.operator == operator
    )
    
    if limit is not None and limit > 0:
        query = query.limit(limit)
    
    return query.order_by(desc(IssueStatusLog.created_at)).all()


def get_status_change_count_by_issue(
    db: Session,
    issue_id: int
) -> int:
    """
    获取指定 Issue 的状态变更次数
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
    
    Returns:
        状态变更次数
    """
    return db.query(IssueStatusLog).filter(
        IssueStatusLog.issue_id == issue_id
    ).count()


def get_latest_status_log_by_issue(
    db: Session,
    issue_id: int
) -> Optional[IssueStatusLog]:
    """
    获取指定 Issue 的最新状态变更日志
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
    
    Returns:
        最新的 IssueStatusLog 对象，不存在则返回 None
    """
    return db.query(IssueStatusLog).filter(
        IssueStatusLog.issue_id == issue_id
    ).order_by(desc(IssueStatusLog.created_at)).first()
