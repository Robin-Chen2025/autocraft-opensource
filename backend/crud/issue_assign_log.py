"""
Issue Assign Log 数据库 CRUD 操作模块
AutoCraft 问题跟踪系统 - Issue 指派变更日志数据操作层
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.issue_assign_log import IssueAssignLog


def create_assign_log(
    db: Session,
    issue_id: int,
    from_assignee: Optional[str],
    to_assignee: Optional[str],
    assigned_by: str,
    due_date: Optional[datetime] = None,
    note: Optional[str] = None
) -> IssueAssignLog:
    """
    创建 Issue 指派变更日志
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
        from_assignee: 变更前的被指派人（首次分配时为 None）
        to_assignee: 变更后的被指派人
        assigned_by: 指派操作人
        due_date: 截止日期（可选）
        note: 指派备注（可选）
    
    Returns:
        创建的 IssueAssignLog 对象
    """
    db_assign_log = IssueAssignLog(
        issue_id=issue_id,
        from_assignee=from_assignee,
        to_assignee=to_assignee,
        assigned_by=assigned_by,
        due_date=due_date,
        note=note,
        created_at=datetime.now()
    )
    db.add(db_assign_log)
    db.commit()
    db.refresh(db_assign_log)
    return db_assign_log


def get_assign_logs_by_issue_id(
    db: Session,
    issue_id: int,
    limit: Optional[int] = None
) -> List[IssueAssignLog]:
    """
    根据 Issue ID 获取指派变更日志列表
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
        limit: 返回记录数量限制（可选，默认返回全部）
    
    Returns:
        IssueAssignLog 列表，按创建时间倒序排列
    """
    query = db.query(IssueAssignLog).filter(
        IssueAssignLog.issue_id == issue_id
    )
    
    if limit is not None and limit > 0:
        query = query.limit(limit)
    
    return query.order_by(desc(IssueAssignLog.created_at)).all()
