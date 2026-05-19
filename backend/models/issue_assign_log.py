"""
Issue Assign Log 数据模型
AutoCraft 问题跟踪系统 - Issue 指派变更日志模型定义
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

# 使用 database.py 的 Base，确保表能被正确创建
from database import Base




class IssueAssignLog(Base):
    """
    Issue Assign Log 指派变更日志模型
    
    用于记录 Issue 指派变更的完整历史，支持指派流转追踪和审计。
    每次指派变更都会创建一条新记录。
    
    Attributes:
        id: 主键，自增整数
        issue_id: 关联的 Issue ID，外键关联 issues 表
        from_assignee: 变更前的被指派人
        to_assignee: 变更后的被指派人
        assigned_by: 指派操作人
        due_date: 截止日期
        note: 指派备注
        created_at: 创建时间
    """
    __tablename__ = "issue_assign_logs"

    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键 ID",
    )

    # 外键关联
    issue_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的 Issue ID",
    )

    # 指派变更字段
    from_assignee: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="变更前的被指派人",
    )
    to_assignee: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="变更后的被指派人",
    )

    # 指派操作人
    assigned_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="指派操作人",
    )

    # 截止日期
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="截止日期",
    )

    # 指派备注
    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="指派备注",
    )

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间",
    )

    # 索引定义
    __table_args__ = (
        Index("ix_issue_assign_logs_issue_id", "issue_id"),
        Index("ix_issue_assign_logs_to_assignee", "to_assignee"),
        Index("ix_issue_assign_logs_created_at", "created_at"),
        Index("ix_issue_assign_logs_issue_created", "issue_id", "created_at"),
        {"comment": "Issue 指派变更日志表"},
    )
