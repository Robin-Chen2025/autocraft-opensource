"""
Checklist 数据模型
AutoCraft 检查清单管理 - Checklist 数据模型定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    event,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

# 使用 database.py 的 Base，确保表能被正确创建
from database import Base


class Checklist(Base):
    """
    Checklist 检查清单模型
    
    用于存储各种审查清单，支持代码审查、文档审查、安全审查等场景。
    基于 Reviewer 模式：分离审查标准与流程。
    
    Attributes:
        checklist_id: 清单ID，主键，如 "api-design", "code-quality"
        name: 清单名称
        description: 清单描述
        category: 分类（代码审查/文档审查/安全审查）
        items: 检查项（JSON数组）
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "checklists"

    # 主键 - 清单ID（使用语义化ID而非自增ID）
    checklist_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="清单ID，如 'api-design', 'code-quality'",
    )

    # 基本信息
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="清单名称",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="清单描述",
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="分类：代码审查/文档审查/安全审查",
    )

    # 检查项（JSON格式存储）
    # 格式示例：
    # [
    #   {"id": "001", "category": "结构完整性", "description": "包含接口路径和HTTP方法", "level": "Error"},
    #   {"id": "002", "category": "命名规范", "description": "URL使用kebab-case", "level": "Warning"}
    # ]
    items: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default='[]',
        comment="检查项（JSON数组）",
    )

    # 审计字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )

    __table_args__ = (
        {"comment": "Checklist 检查清单表"},
    )


# 更新时间触发器事件监听器
@event.listens_for(Checklist, "before_update")
def receive_before_update(mapper, connection, target):
    """
    Checklist 更新前事件监听器
    
    在更新 Checklist 记录时自动更新 updated_at 字段为当前时间。
    
    Args:
        mapper: SQLAlchemy mapper 对象
        connection: 数据库连接对象
        target: 被更新的 Checklist 实例
    """
    target.updated_at = datetime.now()
