"""
Checklist 模块 Pydantic Schema 定义
AutoCraft 检查清单管理 - Pydantic v2 数据验证模型
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# 枚举定义
# ============================================================================

class ChecklistCategory(str, Enum):
    """检查清单分类枚举"""
    CODE_REVIEW = "代码审查"
    DOCUMENT_REVIEW = "文档审查"
    SECURITY_REVIEW = "安全审查"
    OTHER = "其他"


# ============================================================================
# 基础模型
# ============================================================================

class ChecklistBase(BaseModel):
    """Checklist 基础模型"""
    name: str = Field(..., max_length=100, description="清单名称")
    description: Optional[str] = Field(None, description="清单描述")
    category: ChecklistCategory = Field(..., description="清单分类")
    items: str = Field(default='[]', description="检查项（JSON 数组）")


# ============================================================================
# 请求模型
# ============================================================================

class ChecklistCreate(ChecklistBase):
    """创建 Checklist 请求模型"""
    checklist_id: str = Field(..., max_length=50, description="清单 ID，如 'api-design', 'code-quality'")


class ChecklistUpdate(BaseModel):
    """更新 Checklist 请求模型（所有字段可选）"""
    name: Optional[str] = Field(None, max_length=100, description="清单名称")
    description: Optional[str] = Field(None, description="清单描述")
    category: Optional[ChecklistCategory] = Field(None, description="清单分类")
    items: Optional[str] = Field(None, description="检查项（JSON 数组）")


# ============================================================================
# 响应模型
# ============================================================================

class ChecklistResponse(ChecklistBase):
    """Checklist 响应模型"""
    checklist_id: str = Field(..., description="清单 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class ChecklistListResponse(BaseModel):
    """Checklist 列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: List[ChecklistResponse] = Field(..., description="Checklist 列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class ChecklistDetailResponse(BaseModel):
    """Checklist 详情响应模型"""
    data: ChecklistResponse = Field(..., description="Checklist 详情")


# ============================================================================
# 查询参数模型
# ============================================================================

class ChecklistFilter(BaseModel):
    """Checklist 筛选条件模型"""
    page: int = Field(default=1, ge=1, le=1000, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    category: Optional[ChecklistCategory] = Field(None, description="分类筛选")
    keyword: Optional[str] = Field(None, description="关键字搜索（名称/描述）")


# ============================================================================
# 通用响应模型
# ============================================================================

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="消息内容")
