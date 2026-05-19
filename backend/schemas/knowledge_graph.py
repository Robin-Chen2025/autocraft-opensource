"""
知识图谱 Pydantic Schema 定义
AutoCraft 知识图谱管理系统 - 数据验证模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# 基础模型
# ============================================================================

class KnowledgeGraphNodeBase(BaseModel):
    """知识图谱节点基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="节点名称")
    description: Optional[str] = Field(None, description="节点描述")
    node_type: str = Field(..., description="节点类型：subject/semester/chapter/knowledge_point")
    order: int = Field(0, ge=0, description="排序顺序")


class KnowledgePointBase(BaseModel):
    """知识点基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="知识点名称")
    description: Optional[str] = Field(None, description="知识点描述")
    difficulty: str = Field("medium", description="难度：easy/medium/hard")
    order: int = Field(0, ge=0, description="知识点顺序")


class ChapterBase(BaseModel):
    """章节基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="章节名称")
    order: int = Field(0, ge=0, description="章节顺序")


class SemesterBase(BaseModel):
    """学期基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="学期名称")
    order: int = Field(0, ge=0, description="学期顺序")


class SubjectBase(BaseModel):
    """学科基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="学科名称")
    description: Optional[str] = Field(None, description="学科描述")


# ============================================================================
# 创建请求模型
# ============================================================================

class SubjectCreate(SubjectBase):
    """创建学科请求模型"""
    pass


class SemesterCreate(SemesterBase):
    """创建学期请求模型"""
    subject_id: int = Field(..., gt=0, description="学科ID")


class ChapterCreate(ChapterBase):
    """创建章节请求模型"""
    semester_id: int = Field(..., gt=0, description="学期ID")


class KnowledgePointCreate(KnowledgePointBase):
    """创建知识点请求模型"""
    chapter_id: int = Field(..., gt=0, description="章节ID")
    prerequisite_ids: Optional[List[int]] = Field(default_factory=list, description="前置知识点ID列表")


# ============================================================================
# 更新请求模型
# ============================================================================

class KnowledgePointUpdate(BaseModel):
    """更新知识点请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="知识点名称")
    description: Optional[str] = Field(None, description="知识点描述")
    difficulty: Optional[str] = Field(None, description="难度：easy/medium/hard")
    prerequisite_ids: Optional[List[int]] = Field(default_factory=list, description="前置知识点ID列表")


# ============================================================================
# 响应模型
# ============================================================================

class KnowledgePointResponse(KnowledgePointBase):
    """知识点响应模型"""
    id: int
    chapter_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChapterResponse(ChapterBase):
    """章节响应模型"""
    id: int
    semester_id: int
    knowledge_points: List[KnowledgePointResponse] = []
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SemesterResponse(SemesterBase):
    """学期响应模型"""
    id: int
    subject_id: int
    chapters: List[ChapterResponse] = []
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubjectResponse(SubjectBase):
    """学科响应模型"""
    id: int
    semesters: List[SemesterResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 知识图谱导入/导出模型
# ============================================================================

class KnowledgeGraphUploadRequest(BaseModel):
    """知识图谱上传请求模型"""
    content: str = Field(..., description="Markdown格式的知识图谱内容")
    subject_name: str = Field(..., min_length=1, max_length=100, description="学科名称")


class KnowledgeGraphUploadResponse(BaseModel):
    """知识图谱上传响应模型"""
    message: str
    subject_id: int
    stats: dict


class KnowledgeGraphTreeResponse(BaseModel):
    """知识图谱树形结构响应模型"""
    subjects: List[SubjectResponse] = []
    total_subjects: int = 0
    total_semesters: int = 0
    total_chapters: int = 0
    total_knowledge_points: int = 0


# ============================================================================
# 任务关联模型
# ============================================================================

class TaskKnowledgeGraphLinkRequest(BaseModel):
    """任务关联知识图谱请求模型"""
    task_id: int = Field(..., gt=0, description="任务ID")
    knowledge_point_ids: List[int] = Field(default_factory=list, description="知识点ID列表")


class TaskKnowledgeGraphLinkResponse(BaseModel):
    """任务关联知识图谱响应模型"""
    task_id: int
    knowledge_point_ids: List[int]
    linked_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 搜索/过滤模型
# ============================================================================

class KnowledgeGraphSearchFilter(BaseModel):
    """知识图谱搜索过滤模型"""
    subject_id: Optional[int] = Field(None, description="学科ID")
    semester_id: Optional[int] = Field(None, description="学期ID")
    chapter_id: Optional[int] = Field(None, description="章节ID")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    difficulty: Optional[str] = Field(None, description="难度筛选")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")