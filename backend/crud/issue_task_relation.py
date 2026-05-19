"""
Issue Task Relation 数据库 CRUD 操作模块
AutoCraft 问题跟踪系统 - Issue 与 Task 关联关系数据操作层
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.issue_task_relation import IssueTaskRelation
from models.issue import Issue
from models import Task


def create_relation(
    db: Session,
    issue_id: int,
    task_id: int,
    created_by: str
) -> Optional[IssueTaskRelation]:
    """
    创建 Issue 与 Task 的关联关系
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
        task_id: Task ID
        created_by: 创建人
    
    Returns:
        创建的 IssueTaskRelation 对象，如果关联已存在或外键不存在则返回 None
    
    Note:
        会验证 issue_id 和 task_id 是否存在，不存在则返回 None
        同一对 (issue_id, task_id) 只能创建一次关联
    """
    # 验证 Issue 是否存在
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if issue is None:
        return None
    
    # 验证 Task 是否存在
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        return None
    
    # 检查关联是否已存在
    existing = db.query(IssueTaskRelation).filter(
        IssueTaskRelation.issue_id == issue_id,
        IssueTaskRelation.task_id == task_id
    ).first()
    if existing is not None:
        return None
    
    # 创建关联关系
    db_relation = IssueTaskRelation(
        issue_id=issue_id,
        task_id=task_id,
        created_by=created_by,
        created_at=datetime.now()
    )
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


def get_relations_by_issue_id(
    db: Session,
    issue_id: int
) -> List[IssueTaskRelation]:
    """
    根据 Issue ID 获取所有关联的 Task 关系
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
    
    Returns:
        IssueTaskRelation 对象列表，按创建时间倒序排列
    """
    return db.query(IssueTaskRelation).filter(
        IssueTaskRelation.issue_id == issue_id
    ).order_by(
        desc(IssueTaskRelation.created_at)
    ).all()


def get_relations_by_task_id(
    db: Session,
    task_id: int
) -> List[IssueTaskRelation]:
    """
    根据 Task ID 获取所有关联的 Issue 关系
    
    Args:
        db: 数据库会话
        task_id: Task ID
    
    Returns:
        IssueTaskRelation 对象列表，按创建时间倒序排列
    """
    return db.query(IssueTaskRelation).filter(
        IssueTaskRelation.task_id == task_id
    ).order_by(
        desc(IssueTaskRelation.created_at)
    ).all()


def delete_relation(
    db: Session,
    issue_id: int,
    task_id: int
) -> bool:
    """
    删除 Issue 与 Task 的关联关系
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
        task_id: Task ID
    
    Returns:
        True 如果删除成功，False 如果关联不存在
    """
    relation = db.query(IssueTaskRelation).filter(
        IssueTaskRelation.issue_id == issue_id,
        IssueTaskRelation.task_id == task_id
    ).first()
    
    if relation is None:
        return False
    
    db.delete(relation)
    db.commit()
    return True


def get_relation(
    db: Session,
    issue_id: int,
    task_id: int
) -> Optional[IssueTaskRelation]:
    """
    获取单个 Issue 与 Task 的关联关系
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
        task_id: Task ID
    
    Returns:
        IssueTaskRelation 对象，如果不存在则返回 None
    """
    return db.query(IssueTaskRelation).filter(
        IssueTaskRelation.issue_id == issue_id,
        IssueTaskRelation.task_id == task_id
    ).first()


def relation_exists(
    db: Session,
    issue_id: int,
    task_id: int
) -> bool:
    """
    检查 Issue 与 Task 的关联关系是否存在
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
        task_id: Task ID
    
    Returns:
        True 如果关联存在，否则 False
    """
    return get_relation(db, issue_id, task_id) is not None
