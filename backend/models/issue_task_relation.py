"""
Issue Task Relation 数据模型
AutoCraft 问题跟踪系统 - Issue 与 Task 关联关系模型定义
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

# 使用 database.py 的 Base，确保表能被正确创建
from database import Base




class IssueTaskRelation(Base):
    """
    Issue Task Relation 关联关系模型
    
    用于建立 Issue 与 Task 之间的关联关系。
    支持一个 Issue 关联多个 Task，一个 Task 也可以关联多个 Issue。
    
    Attributes:
        id: 主键，自增整数
        issue_id: 关联的 Issue ID，外键关联 issues 表
        task_id: 关联的 Task ID，外键关联 tasks 表
        created_by: 创建人
        created_at: 创建时间
    """
    __tablename__ = "issue_task_relations"

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
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的 Task ID",
    )

    # 审计字段
    created_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="创建人",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间",
    )

    # 约束和索引定义
    __table_args__ = (
        UniqueConstraint("issue_id", "task_id", name="uq_issue_task_relation"),
        Index("ix_issue_task_relations_issue_id", "issue_id"),
        Index("ix_issue_task_relations_task_id", "task_id"),
        Index("ix_issue_task_relations_created_at", "created_at"),
        {"comment": "Issue 与 Task 关联关系表"},
    )
