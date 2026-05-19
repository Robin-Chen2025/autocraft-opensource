"""
IssueSummary 模块 Pydantic Schema 定义
AutoCraft 问题总结系统 - Pydantic v2 数据验证模型
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# 嵌套模型：相关资源
# ============================================================================

class RelatedResource(BaseModel):
    """相关资源嵌套模型"""
    resource_type: str = Field(..., description="资源类型，如：task, document, commit 等")
    resource_id: str = Field(..., description="资源 ID")
    resource_name: str = Field(..., description="资源名称")
    resource_url: Optional[str] = Field(None, description="资源 URL 链接")
    description: Optional[str] = Field(None, description="资源描述")


# ============================================================================
# 基础模型
# ============================================================================

class IssueSummaryBase(BaseModel):
    """IssueSummary 基础模型"""
    root_cause: Optional[str] = Field(None, description="根本原因")
    solution_approach: Optional[str] = Field(None, description="解决方案方法")
    lessons_learned: Optional[str] = Field(None, description="经验教训")
    prevention_measures: Optional[str] = Field(None, description="预防措施")
    related_resources: Any = Field(default_factory=list, description="相关资源列表（JSON 格式）")


# ============================================================================
# 请求模型
# ============================================================================

class IssueSummaryCreate(IssueSummaryBase):
    """创建 IssueSummary 请求模型"""
    issue_id: int = Field(..., description="关联的 Issue ID")
    summarized_by: str = Field(..., description="总结人")


class IssueSummaryUpdate(BaseModel):
    """更新 IssueSummary 请求模型（所有字段可选）"""
    root_cause: Optional[str] = Field(None, description="根本原因")
    solution_approach: Optional[str] = Field(None, description="解决方案方法")
    lessons_learned: Optional[str] = Field(None, description="经验教训")
    prevention_measures: Optional[str] = Field(None, description="预防措施")
    related_resources: Optional[Any] = Field(None, description="相关资源列表（JSON 格式）")


# ============================================================================
# 响应模型
# ============================================================================

class IssueSummaryResponse(IssueSummaryBase):
    """IssueSummary 响应模型"""
    id: int = Field(..., description="IssueSummary ID")
    issue_id: int = Field(..., description="关联的 Issue ID")
    summarized_by: str = Field(..., description="总结人")
    summarized_at: datetime = Field(..., description="总结时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class IssueSummaryListResponse(BaseModel):
    """IssueSummary 列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: List[IssueSummaryResponse] = Field(..., description="IssueSummary 列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class IssueSummaryDetailResponse(BaseModel):
    """IssueSummary 详情响应模型"""
    data: IssueSummaryResponse = Field(..., description="IssueSummary 详情")


class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="响应消息")
    issue_no: Optional[str] = Field(None, description="问题编号")
