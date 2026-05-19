"""
Knowledge Base 数据模型
AutoCraft 知识库系统 - 知识库数据模型定义
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
    Boolean,
    event,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

# 使用 database.py 的 Base，确保表能被正确创建
from database import Base




class KnowledgeBase(Base):
    """
    Knowledge Base 知识库模型
    
    用于存储和管理从 Issue 中提取的知识条目，支持知识复用和经验传承。
    每个知识条目关联一个 Issue，包含问题描述、解决方案、经验总结等信息。
    
    Attributes:
        id: 主键，自增整数
        issue_id: 关联的 Issue ID，外键关联 issues 表，唯一约束
        issue_no: 问题编号，便于查询和展示
        title: 知识条目标题
        description: 问题描述
        category: 知识分类
        solution: 解决方案
        solution_process: 解决过程
        root_cause: 根本原因
        solution_approach: 解决方法
        lessons_learned: 经验总结
        prevention_measures: 预防措施
        is_featured: 是否精选
        view_count: 浏览次数
        reference_count: 引用次数
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "knowledge_base"

    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键 ID",
    )

    # 外键关联（唯一约束）
    issue_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="关联的 Issue ID",
    )

    # 问题编号
    issue_no: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="问题编号",
    )

    # 基本信息
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

    # 分类
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="分类",
    )

    # 解决方案相关信息
    solution: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解决方案",
    )
    solution_process: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解决过程",
    )
    root_cause: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="根本原因",
    )
    solution_approach: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解决方法",
    )

    # 经验总结
    lessons_learned: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="经验总结",
    )
    prevention_measures: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="预防措施",
    )

    # 统计字段
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="是否精选",
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="浏览次数",
    )
    reference_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="引用次数",
    )

    # 审计字段
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
        Index("ix_knowledge_base_category_featured", "category", "is_featured"),
        Index("ix_knowledge_base_created_at_featured", "created_at", "is_featured"),
        Index("ix_knowledge_base_view_count_featured", "view_count", "is_featured"),
        {"comment": "Knowledge Base 知识库表"},
    )


# 更新时间触发器事件监听器
@event.listens_for(KnowledgeBase, "before_update")
def receive_before_update(mapper, connection, target):
    """
    Knowledge Base 更新前事件监听器
    
    在更新知识库记录时自动更新 updated_at 字段为当前时间。
    这是 SQLAlchemy 2.0 中实现自动更新时间戳的推荐方式。
    
    Args:
        mapper: SQLAlchemy mapper 对象
        connection: 数据库连接对象
        target: 被更新的 KnowledgeBase 实例
    """
    target.updated_at = datetime.now()
