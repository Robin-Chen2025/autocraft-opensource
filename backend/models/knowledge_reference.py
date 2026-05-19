"""
Knowledge Reference 知识引用数据模型
AutoCraft 知识库系统 - 知识引用关系数据模型定义
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




class KnowledgeReference(Base):
    """
    Knowledge Reference 知识引用关系模型
    
    用于记录知识库条目之间的引用关系，追踪知识条目的复用情况和关联关系。
    每个引用记录表示一个知识条目被另一个条目所引用，包含引用上下文信息。
    
    Attributes:
        id: 主键，自增整数
        knowledge_id: 被引用的知识条目 ID，外键关联 knowledge_base 表
        referenced_by: 引用者的标识（可以是 issue_id 或其他资源 ID）
        reference_context: 引用上下文，描述引用的具体场景或内容
        created_at: 创建时间
    """
    __tablename__ = "knowledge_references"

    # 主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键 ID",
    )

    # 外键关联（被引用的知识条目）
    knowledge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        nullable=False,
        comment="被引用的知识条目 ID",
    )

    # 引用者标识
    referenced_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="引用者标识（如 issue_id 或其他资源 ID）",
    )

    # 引用上下文
    reference_context: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="引用上下文",
    )

    # 审计字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间",
    )

    # 索引定义
    __table_args__ = (
        Index("ix_knowledge_references_knowledge_id", "knowledge_id"),
        Index("ix_knowledge_references_referenced_by", "referenced_by"),
        {"comment": "Knowledge Reference 知识引用关系表"},
    )


# 创建时间触发器事件监听器
@event.listens_for(KnowledgeReference, "before_insert")
def receive_before_insert(mapper, connection, target):
    """
    Knowledge Reference 插入前事件监听器
    
    在插入知识引用记录时确保 created_at 字段设置为当前时间。
    这是 SQLAlchemy 2.0 中实现自动创建时间戳的推荐方式。
    
    Args:
        mapper: SQLAlchemy mapper 对象
        connection: 数据库连接对象
        target: 被插入的 KnowledgeReference 实例
    """
    if target.created_at is None:
        target.created_at = datetime.now()
