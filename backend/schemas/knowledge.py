"""
Knowledge 模块 Pydantic Schema 定义
AutoCraft 知识管理系统 - Pydantic v2 数据验证模型
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# 枚举定义
# ============================================================================

class KnowledgeType(str, Enum):
    """知识类型枚举"""
    DOCUMENT = "文档"
    TUTORIAL = "教程"
    BEST_PRACTICE = "最佳实践"
    CASE_STUDY = "案例研究"
    FAQ = "常见问题"
    REFERENCE = "参考资料"


class KnowledgeStatus(str, Enum):
    """知识状态枚举"""
    DRAFT = "草稿"
    PUBLISHED = "已发布"
    ARCHIVED = "已归档"


class KnowledgeQuality(str, Enum):
    """知识质量等级枚举"""
    NORMAL = "普通"
    FEATURED = "优质"


# ============================================================================
# 基础模型
# ============================================================================

class KnowledgeBase(BaseModel):
    """Knowledge 基础模型"""
    title: str = Field(..., max_length=200, description="知识标题")
    summary: str = Field(..., description="知识摘要")
    content: str = Field(..., description="知识内容")
    knowledge_type: KnowledgeType = Field(..., description="知识类型")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")


# ============================================================================
# 请求模型
# ============================================================================

class KnowledgeCreate(KnowledgeBase):
    """创建 Knowledge 请求模型"""
    project_id: Optional[int] = Field(None, description="项目 ID")
    category_id: Optional[int] = Field(None, description="分类 ID")
    created_by: str = Field(..., description="创建人")


class KnowledgeUpdate(BaseModel):
    """更新 Knowledge 请求模型（所有字段可选）"""
    title: Optional[str] = Field(None, max_length=200, description="知识标题")
    summary: Optional[str] = Field(None, description="知识摘要")
    content: Optional[str] = Field(None, description="知识内容")
    knowledge_type: Optional[KnowledgeType] = Field(None, description="知识类型")
    status: Optional[KnowledgeStatus] = Field(None, description="状态")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    category_id: Optional[int] = Field(None, description="分类 ID")


class KnowledgeSearchFilter(BaseModel):
    """Knowledge 搜索条件模型"""
    page: int = Field(default=1, ge=1, le=1000, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="关键字搜索（标题/摘要/内容）")
    knowledge_type: Optional[KnowledgeType] = Field(None, description="知识类型筛选")
    status: Optional[KnowledgeStatus] = Field(None, description="状态筛选")
    quality: Optional[KnowledgeQuality] = Field(None, description="质量等级筛选")
    category_id: Optional[int] = Field(None, description="分类 ID 筛选")
    project_id: Optional[int] = Field(None, description="项目 ID 筛选")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    created_by: Optional[str] = Field(None, description="创建人筛选")
    is_featured: Optional[bool] = Field(None, description="是否优质筛选")
    created_at_from: Optional[datetime] = Field(None, description="创建时间起始")
    created_at_to: Optional[datetime] = Field(None, description="创建时间结束")


class KnowledgeBaseCreate(BaseModel):
    """创建 KnowledgeBase 请求模型"""
    issue_id: int = Field(..., description="关联的 Issue ID")
    issue_no: str = Field(..., max_length=50, description="问题编号")
    title: str = Field(..., max_length=200, description="知识条目标题")
    description: Optional[str] = Field(None, description="问题描述")
    category: str = Field(..., max_length=50, description="知识分类")
    solution: Optional[str] = Field(None, description="解决方案")
    solution_process: Optional[str] = Field(None, description="解决过程")
    root_cause: Optional[str] = Field(None, description="根本原因")
    solution_approach: Optional[str] = Field(None, description="解决方法")
    lessons_learned: Optional[str] = Field(None, description="经验总结")
    prevention_measures: Optional[str] = Field(None, description="预防措施")
    is_featured: Optional[bool] = Field(default=False, description="是否精选")


class KnowledgeBaseUpdate(BaseModel):
    """更新 KnowledgeBase 请求模型（所有字段可选）"""
    issue_id: Optional[int] = Field(None, description="关联的 Issue ID")
    issue_no: Optional[str] = Field(None, max_length=50, description="问题编号")
    title: Optional[str] = Field(None, max_length=200, description="知识条目标题")
    description: Optional[str] = Field(None, description="问题描述")
    category: Optional[str] = Field(None, max_length=50, description="知识分类")
    solution: Optional[str] = Field(None, description="解决方案")
    solution_process: Optional[str] = Field(None, description="解决过程")
    root_cause: Optional[str] = Field(None, description="根本原因")
    solution_approach: Optional[str] = Field(None, description="解决方法")
    lessons_learned: Optional[str] = Field(None, description="经验总结")
    prevention_measures: Optional[str] = Field(None, description="预防措施")
    is_featured: Optional[bool] = Field(None, description="是否精选")


class KnowledgeBaseSearchFilter(BaseModel):
    """KnowledgeBase 搜索条件模型"""
    page: int = Field(default=1, ge=1, le=1000, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="关键字搜索（标题/描述/解决方案等）")
    category: Optional[str] = Field(None, description="分类筛选")
    is_featured: Optional[bool] = Field(None, description="是否精选筛选")


class KnowledgeBaseResponse(BaseModel):
    """KnowledgeBase 响应模型"""
    id: int = Field(..., description="知识 ID")
    issue_id: int = Field(..., description="关联的 Issue ID")
    issue_no: str = Field(..., max_length=50, description="问题编号")
    title: str = Field(..., max_length=200, description="知识条目标题")
    description: Optional[str] = Field(None, description="问题描述")
    category: str = Field(..., max_length=50, description="知识分类")
    solution: Optional[str] = Field(None, description="解决方案")
    solution_process: Optional[str] = Field(None, description="解决过程")
    root_cause: Optional[str] = Field(None, description="根本原因")
    solution_approach: Optional[str] = Field(None, description="解决方法")
    lessons_learned: Optional[str] = Field(None, description="经验总结")
    prevention_measures: Optional[str] = Field(None, description="预防措施")
    is_featured: bool = Field(default=False, description="是否精选")
    view_count: int = Field(default=0, description="浏览次数")
    reference_count: int = Field(default=0, description="引用次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseListResponse(BaseModel):
    """KnowledgeBase 列表响应模型（分页）"""
    total: int = Field(..., description="总记录数")
    items: List[KnowledgeBaseResponse] = Field(..., description="知识库列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class KnowledgeFeatureRequest(BaseModel):
    """标记优质 Knowledge 请求模型"""
    is_featured: bool = Field(..., description="是否标记为优质")


class KnowledgeReferenceRequest(BaseModel):
    """引用 Knowledge 请求模型"""
    reference_context: str = Field(..., description="引用上下文")
    referenced_by: str = Field(..., description="引用操作人/资源标识")


# ============================================================================
# 响应模型
# ============================================================================

class KnowledgeResponse(KnowledgeBase):
    """Knowledge 响应模型"""
    id: int = Field(..., description="Knowledge ID")
    knowledge_no: str = Field(..., description="知识编号")
    status: KnowledgeStatus = Field(..., description="状态")
    quality: KnowledgeQuality = Field(default=KnowledgeQuality.NORMAL, description="质量等级")
    is_featured: bool = Field(default=False, description="是否优质")
    featured_reason: Optional[str] = Field(None, description="标记优质理由")
    featured_at: Optional[datetime] = Field(None, description="标记优质时间")
    featured_by: Optional[str] = Field(None, description="标记优质操作人")
    project_id: Optional[int] = Field(None, description="项目 ID")
    category_id: Optional[int] = Field(None, description="分类 ID")
    category_name: Optional[str] = Field(None, description="分类名称")
    view_count: int = Field(default=0, description="浏览次数")
    like_count: int = Field(default=0, description="点赞次数")
    reference_count: int = Field(default=0, description="引用次数")
    created_by: str = Field(..., description="创建人")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    published_at: Optional[datetime] = Field(None, description="发布时间")
    archived_at: Optional[datetime] = Field(None, description="归档时间")

    model_config = ConfigDict(from_attributes=True)


class KnowledgeListResponse(BaseModel):
    """Knowledge 列表响应模型（分页）"""
    total: int = Field(..., description="总记录数")
    items: List[KnowledgeResponse] = Field(..., description="Knowledge 列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class KnowledgeDetailResponse(BaseModel):
    """Knowledge 详情响应模型"""
    data: KnowledgeResponse = Field(..., description="Knowledge 详情")


# ============================================================================
# 通用响应模型
# ============================================================================

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="消息内容")
    knowledge_no: Optional[str] = Field(None, description="知识编号")
