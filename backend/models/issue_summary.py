"""
Issue Summary 数据模型
AutoCraft 问题总结系统 - Issue 总结数据模型定义
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
    UniqueConstraint,
    Index,
    event,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

# 使用 database.py 的 Base，确保表能被正确创建
from database import Base




class IssueSummary(Base):
    """
    Issue Summary 问题总结模型
    
    用于存储 Issue 的总结信息，包括根本原因、解决方案、经验教训和预防措施。
    每个 Issue 只能有一个总结记录。
    
    Attributes:
        id: 主键，自增整数
        issue_id: Issue ID，外键关联 issues 表
        root_cause: 根本原因分析
        solution_approach: 解决方案方法
        lessons_learned: 经验教训
        prevention_measures: 预防措施
        related_resources: 相关资源链接
        summarized_by: 总结人
        summarized_at: 总结时间
        updated_at: 更新时间
    """
    __tablename__ = "issue_summaries"

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
        ForeignKey("issues.id"),
        nullable=False,
        index=True,
        comment="Issue ID",
    )

    # 总结内容
    root_cause: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="根本原因",
    )
    solution_approach: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解决方案方法",
    )
    lessons_learned: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="经验教训",
    )
    prevention_measures: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="预防措施",
    )
    related_resources: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="相关资源",
    )

    # 审计字段
    summarized_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="总结人",
    )
    summarized_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="总结时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    # 唯一约束：每个 issue_id 只能有一个总结
    __table_args__ = (
        UniqueConstraint("issue_id", name="uq_issue_summaries_issue_id"),
        Index("ix_issue_summaries_summarized_at", "summarized_at"),
        {"comment": "Issue 问题总结表"},
    )


# 更新时间触发器事件监听器
@event.listens_for(IssueSummary, "before_update")
def receive_before_update(mapper, connection, target):
    """
    IssueSummary 更新前事件监听器
    
    在更新 IssueSummary 记录时自动更新 updated_at 字段为当前时间。
    这是 SQLAlchemy 2.0 中实现自动更新时间戳的推荐方式。
    
    Args:
        mapper: SQLAlchemy mapper 对象
        connection: 数据库连接对象
        target: 被更新的 IssueSummary 实例
    """
    target.updated_at = datetime.now()
