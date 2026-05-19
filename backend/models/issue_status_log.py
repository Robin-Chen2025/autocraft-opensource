"""
Issue Status Log 数据模型
AutoCraft 问题跟踪系统 - Issue 状态变更日志模型定义
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




class IssueStatusLog(Base):
    """
    Issue Status Log 状态变更日志模型
    
    用于记录 Issue 状态变更的完整历史，支持状态流转追踪和审计。
    每次状态变更都会创建一条新记录。
    
    Attributes:
        id: 主键，自增整数
        issue_id: 关联的 Issue ID，外键关联 issues 表
        from_status: 变更前的状态
        to_status: 变更后的状态
        operator: 操作人
        operator_role: 操作人角色
        reason: 变更原因
        created_at: 创建时间
    """
    __tablename__ = "issue_status_logs"

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

    # 状态变更字段
    from_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="变更前的状态",
    )
    to_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="变更后的状态",
    )

    # 操作人信息
    operator: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="操作人",
    )
    operator_role: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="操作人角色",
    )

    # 变更原因
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="变更原因",
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
        Index("ix_issue_status_logs_issue_id", "issue_id"),
        Index("ix_issue_status_logs_created_at", "created_at"),
        Index("ix_issue_status_logs_operator", "operator"),
        Index("ix_issue_status_logs_issue_created", "issue_id", "created_at"),
        {"comment": "Issue 状态变更日志表"},
    )
