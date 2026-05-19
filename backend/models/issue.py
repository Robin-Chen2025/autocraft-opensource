"""
Issue 数据模型
AutoCraft 问题跟踪系统 - Issue 数据模型定义
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
    event,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

# 使用 database.py 的 Base，确保表能被正确创建
from database import Base


class Issue(Base):
    """
    Issue 问题跟踪模型
    
    用于跟踪和管理项目中的各种问题、任务和需求。
    支持完整的生命周期管理：创建、分配、解决、关闭。
    
    Attributes:
        id: 主键，自增整数
        issue_no: 问题编号，唯一标识符
        title: 问题标题
        description: 问题详细描述
        category: 问题分类
        priority: 优先级
        status: 当前状态
        project_id: 所属项目 ID，外键关联 projects 表
        stage_id: 所属阶段 ID，外键关联 stages 表
        workflow_id: 所属工作流 ID，外键关联 workflows 表
        assignee: 被指派人
        assigned_at: 指派时间
        due_date: 截止日期
        assign_note: 指派备注
        solution_process: 解决过程记录
        solution: 解决方案
        resolved_by: 解决人
        resolved_at: 解决时间
        closed_by: 关闭人
        closed_at: 关闭时间
        created_by: 创建人
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "issues"

    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键 ID",
    )

    # 基本信息
    issue_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="问题编号",
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="标题",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="描述",
    )

    # 分类和状态
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="分类",
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="优先级",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="状态",
    )

    # 外键关联
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
        comment="项目 ID",
    )
    stage_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("stages.id"),
        nullable=True,
        index=True,
        comment="阶段 ID",
    )
    workflow_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("workflows.id"),
        nullable=True,
        index=True,
        comment="工作流 ID",
    )

    # 指派信息
    assignee: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="指派人",
    )
    assigned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="指派时间",
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="截止日期",
    )
    assign_note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="指派备注",
    )

    # 解决信息
    solution_process: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解决过程",
    )
    solution: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解决方案",
    )
    resolved_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="解决人",
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="解决时间",
    )

    # 关闭信息
    closed_by: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="关闭人",
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="关闭时间",
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
        index=True,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    # 复合索引
    __table_args__ = (
        Index("ix_issues_status_category", "status", "category"),
        Index("ix_issues_project_status", "project_id", "status"),
        Index("ix_issues_assignee_status", "assignee", "status"),
        Index("ix_issues_created_at_status", "created_at", "status"),
        {"comment": "Issue 问题跟踪表"},
    )


# 更新时间触发器事件监听器
@event.listens_for(Issue, "before_update")
def receive_before_update(mapper, connection, target):
    """
    Issue 更新前事件监听器
    
    在更新 Issue 记录时自动更新 updated_at 字段为当前时间。
    这是 SQLAlchemy 2.0 中实现自动更新时间戳的推荐方式。
    
    Args:
        mapper: SQLAlchemy mapper 对象
        connection: 数据库连接对象
        target: 被更新的 Issue 实例
    """
    target.updated_at = datetime.now()
