"""
Issue Summary 数据库 CRUD 操作模块
AutoCraft 问题总结系统 - Issue Summary 数据操作层
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.issue_summary import IssueSummary
from schemas.issue_summary import IssueSummaryCreate, IssueSummaryUpdate


def create_summary(db: Session, summary_data: IssueSummaryCreate) -> Optional[IssueSummary]:
    """
    创建 Issue Summary

    Args:
        db: 数据库会话
        summary_data: Issue Summary 创建数据

    Returns:
        创建的 Issue Summary 对象，如果该 Issue 已有总结则返回 None

    Note:
        每个 Issue 只能有一个总结，如果已存在则返回 None
    """
    # 检查该 Issue 是否已有总结
    existing_summary = db.query(IssueSummary).filter(
        IssueSummary.issue_id == summary_data.issue_id
    ).first()

    if existing_summary:
        return None

    db_summary = IssueSummary(
        issue_id=summary_data.issue_id,
        root_cause=summary_data.root_cause,
        solution_approach=summary_data.solution_approach,
        lessons_learned=summary_data.lessons_learned,
        prevention_measures=summary_data.prevention_measures,
        related_resources=summary_data.related_resources,
        summarized_by=summary_data.summarized_by,
        summarized_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary


def get_summary_by_issue_id(db: Session, issue_id: int) -> Optional[IssueSummary]:
    """
    根据 Issue ID 获取 Issue Summary

    Args:
        db: 数据库会话
        issue_id: Issue ID

    Returns:
        Issue Summary 对象，不存在则返回 None
    """
    return db.query(IssueSummary).filter(IssueSummary.issue_id == issue_id).first()


def get_summary_by_id(db: Session, summary_id: int) -> Optional[IssueSummary]:
    """
    根据 Summary ID 获取 Issue Summary

    Args:
        db: 数据库会话
        summary_id: Summary ID

    Returns:
        Issue Summary 对象，不存在则返回 None
    """
    return db.query(IssueSummary).filter(IssueSummary.id == summary_id).first()


def update_summary(db: Session, summary: IssueSummary, summary_update: IssueSummaryUpdate) -> IssueSummary:
    """
    更新 Issue Summary

    Args:
        db: 数据库会话
        summary: Issue Summary 对象
        summary_update: Issue Summary 更新数据

    Returns:
        更新后的 Issue Summary 对象
    """
    update_data = summary_update.model_dump(exclude_unset=True)

    # 更新时间
    update_data['updated_at'] = datetime.now()

    # 更新字段
    for field, value in update_data.items():
        setattr(summary, field, value)

    db.commit()
    db.refresh(summary)
    return summary


def delete_summary(db: Session, summary: IssueSummary) -> None:
    """
    删除 Issue Summary

    Args:
        db: 数据库会话
        summary: Issue Summary 对象
    """
    db.delete(summary)
    db.commit()


def summary_exists(db: Session, issue_id: int) -> bool:
    """
    检查 Issue 是否已有总结

    Args:
        db: 数据库会话
        issue_id: Issue ID

    Returns:
        True 如果已有总结，否则 False
    """
    return get_summary_by_issue_id(db, issue_id) is not None


def get_summaries_by_project(db: Session, project_id: int) -> list[IssueSummary]:
    """
    按项目查询 Issue Summary

    Args:
        db: 数据库会话
        project_id: 项目 ID

    Returns:
        Issue Summary 列表
    """
    from models.issue import Issue
    return db.query(IssueSummary).join(Issue).filter(
        Issue.project_id == project_id
    ).order_by(desc(IssueSummary.summarized_at)).all()


def get_summaries_by_summarizer(db: Session, summarized_by: str) -> list[IssueSummary]:
    """
    按总结人查询 Issue Summary

    Args:
        db: 数据库会话
        summarized_by: 总结人

    Returns:
        Issue Summary 列表
    """
    return db.query(IssueSummary).filter(
        IssueSummary.summarized_by == summarized_by
    ).order_by(desc(IssueSummary.summarized_at)).all()
