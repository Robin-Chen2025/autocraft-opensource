"""
KnowledgeService 业务逻辑层
AutoCraft 知识库系统 - Knowledge 业务逻辑服务
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.knowledge_base import KnowledgeBase
from models.knowledge_reference import KnowledgeReference
from schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseSearchFilter,
    KnowledgeFeatureRequest, KnowledgeReferenceRequest
)
from crud import (
    create_knowledge, get_knowledge_by_id, get_knowledge_by_issue_id,
    get_knowledge_by_issue_no, search_knowledge, update_knowledge,
    mark_as_featured, increment_view_count, delete_knowledge,
    create_reference, get_references_by_knowledge_id
)


class KnowledgeServiceError(Exception):
    """Knowledge 服务基础异常"""
    pass


class KnowledgeValidationError(KnowledgeServiceError):
    """Knowledge 验证异常"""
    pass


class KnowledgePermissionError(KnowledgeServiceError):
    """Knowledge 权限异常"""
    pass


class KnowledgeService:
    """
    Knowledge 业务逻辑服务类
    
    提供 Knowledge 的完整业务逻辑处理，包括：
    - 知识搜索（全文搜索）
    - 知识详情（自动增加浏览量）
    - 标记精选
    - 记录引用
    
    Attributes:
        db: 数据库会话
    """
    
    def __init__(self, db: Session):
        """
        初始化 Knowledge 服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    # =========================================================================
    # 搜索知识 - 全文搜索（支持分页和排序）
    # =========================================================================
    
    def search_knowledge(
        self,
        params: KnowledgeBaseSearchFilter,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[KnowledgeBase], int]:
        """
        搜索知识条目（全文搜索，支持分页和排序）
        
        搜索功能：
        1. 关键词搜索（标题、描述、解决方案、经验总结等）
        2. 分类筛选
        3. 是否精选筛选
        4. 支持多种排序方式
        5. 分页支持
        
        Args:
            params: 搜索参数
            sort_by: 排序字段（created_at, view_count, reference_count, title）
            sort_order: 排序顺序（asc, desc）
        
        Returns:
            (KnowledgeBase 列表，总记录数)
        
        Raises:
            KnowledgeValidationError: 参数验证失败时抛出
        """
        # 验证分页参数
        if params.page < 1:
            raise KnowledgeValidationError("页码必须大于 0")
        
        if params.page_size < 1 or params.page_size > 100:
            raise KnowledgeValidationError("每页数量必须在 1-100 之间")
        
        # 验证排序字段
        valid_sort_fields = ["created_at", "view_count", "reference_count", "title", "updated_at"]
        if sort_by not in valid_sort_fields:
            raise KnowledgeValidationError(
                f"无效的排序字段：{sort_by}，有效值为：{', '.join(valid_sort_fields)}"
            )
        
        # 验证排序顺序
        if sort_order not in ["asc", "desc"]:
            raise KnowledgeValidationError(
                f"无效的排序顺序：{sort_order}，有效值为：asc, desc"
            )
        
        # 调用 CRUD 层搜索
        knowledge_list, total = search_knowledge(self.db, params)
        
        # 如果需要自定义排序（CRUD 层默认按 created_at 倒序）
        if sort_by != "created_at" or sort_order != "desc":
            # 重新查询并应用排序
            query = self.db.query(KnowledgeBase)
            
            # 应用筛选条件
            if params.keyword:
                from sqlalchemy import or_
                query = query.filter(
                    or_(
                        KnowledgeBase.title.contains(params.keyword),
                        KnowledgeBase.description.contains(params.keyword),
                        KnowledgeBase.solution.contains(params.keyword),
                        KnowledgeBase.solution_process.contains(params.keyword),
                        KnowledgeBase.root_cause.contains(params.keyword),
                        KnowledgeBase.solution_approach.contains(params.keyword),
                        KnowledgeBase.lessons_learned.contains(params.keyword),
                        KnowledgeBase.prevention_measures.contains(params.keyword)
                    )
                )
            
            if params.category:
                query = query.filter(KnowledgeBase.category == params.category)
            
            if params.is_featured is not None:
                query = query.filter(KnowledgeBase.is_featured == params.is_featured)
            
            # 应用排序
            sort_field = getattr(KnowledgeBase, sort_by, KnowledgeBase.created_at)
            if sort_order == "desc":
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(sort_field)
            
            # 应用分页
            offset = (params.page - 1) * params.page_size
            knowledge_list = query.offset(offset).limit(params.page_size).all()
            total = query.count()
        
        return knowledge_list, total
    
    # =========================================================================
    # 获取知识详情 - 自动增加浏览量
    # =========================================================================
    
    def get_knowledge_detail(
        self,
        knowledge_id: int,
        auto_increment_view: bool = True
    ) -> Optional[KnowledgeBase]:
        """
        获取知识详情（自动增加浏览量）
        
        Args:
            knowledge_id: 知识 ID
            auto_increment_view: 是否自动增加浏览量（默认 True）
        
        Returns:
            KnowledgeBase 对象，不存在则返回 None
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        # 获取知识条目
        knowledge = get_knowledge_by_id(self.db, knowledge_id)
        
        if not knowledge:
            raise KnowledgeValidationError(f"知识条目 (ID={knowledge_id}) 不存在")
        
        # 自动增加浏览量
        if auto_increment_view:
            knowledge = increment_view_count(self.db, knowledge)
        
        return knowledge
    
    def get_knowledge_detail_by_issue_id(
        self,
        issue_id: int,
        auto_increment_view: bool = True
    ) -> Optional[KnowledgeBase]:
        """
        根据 Issue ID 获取知识详情（自动增加浏览量）
        
        Args:
            issue_id: Issue ID
            auto_increment_view: 是否自动增加浏览量（默认 True）
        
        Returns:
            KnowledgeBase 对象，不存在则返回 None
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        # 获取知识条目
        knowledge = get_knowledge_by_issue_id(self.db, issue_id)
        
        if not knowledge:
            raise KnowledgeValidationError(f"知识条目 (Issue ID={issue_id}) 不存在")
        
        # 自动增加浏览量
        if auto_increment_view:
            knowledge = increment_view_count(self.db, knowledge)
        
        return knowledge
    
    def get_knowledge_detail_by_issue_no(
        self,
        issue_no: str,
        auto_increment_view: bool = True
    ) -> Optional[KnowledgeBase]:
        """
        根据 Issue 编号获取知识详情（自动增加浏览量）
        
        Args:
            issue_no: Issue 编号
            auto_increment_view: 是否自动增加浏览量（默认 True）
        
        Returns:
            KnowledgeBase 对象，不存在则返回 None
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        # 获取知识条目
        knowledge = get_knowledge_by_issue_no(self.db, issue_no)
        
        if not knowledge:
            raise KnowledgeValidationError(f"知识条目 (Issue No={issue_no}) 不存在")
        
        # 自动增加浏览量
        if auto_increment_view:
            knowledge = increment_view_count(self.db, knowledge)
        
        return knowledge
    
    # =========================================================================
    # 标记精选
    # =========================================================================
    
    def mark_featured(
        self,
        knowledge_id: int,
        is_featured: bool,
        operated_by: str,
        featured_reason: Optional[str] = None
    ) -> KnowledgeBase:
        """
        标记知识条目为精选
        
        Args:
            knowledge_id: 知识 ID
            is_featured: 是否精选
            operated_by: 操作人
            featured_reason: 标记理由（可选）
        
        Returns:
            更新后的 KnowledgeBase 对象
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        # 获取知识条目
        knowledge = get_knowledge_by_id(self.db, knowledge_id)
        
        if not knowledge:
            raise KnowledgeValidationError(f"知识条目 (ID={knowledge_id}) 不存在")
        
        # 标记精选
        updated_knowledge = mark_as_featured(self.db, knowledge, is_featured, operated_by)
        
        return updated_knowledge
    
    def mark_featured_by_request(
        self,
        knowledge_id: int,
        request: KnowledgeFeatureRequest
    ) -> KnowledgeBase:
        """
        根据请求对象标记知识条目为精选（便捷方法）
        
        Args:
            knowledge_id: 知识 ID
            request: KnowledgeFeatureRequest 对象
        
        Returns:
            更新后的 KnowledgeBase 对象
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        return self.mark_featured(
            knowledge_id=knowledge_id,
            is_featured=request.is_featured,
            operated_by=request.operated_by,
            featured_reason=request.featured_reason
        )
    
    # =========================================================================
    # 记录引用
    # =========================================================================
    
    def record_reference(
        self,
        knowledge_id: int,
        referenced_by: str,
        reference_context: Optional[str] = None
    ) -> KnowledgeReference:
        """
        记录知识引用
        
        Args:
            knowledge_id: 知识 ID
            referenced_by: 引用者标识（如 issue_id 或其他资源 ID）
            reference_context: 引用上下文，描述引用的具体场景或内容
        
        Returns:
            创建的 KnowledgeReference 对象
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        # 检查知识条目是否存在
        knowledge = get_knowledge_by_id(self.db, knowledge_id)
        
        if not knowledge:
            raise KnowledgeValidationError(f"知识条目 (ID={knowledge_id}) 不存在")
        
        # 创建引用记录（CRUD 层会自动更新 reference_count）
        reference = create_reference(
            db=self.db,
            knowledge_id=knowledge_id,
            referenced_by=referenced_by,
            reference_context=reference_context
        )
        
        return reference
    
    def record_reference_by_request(
        self,
        knowledge_id: int,
        request: KnowledgeReferenceRequest
    ) -> KnowledgeReference:
        """
        根据请求对象记录知识引用（便捷方法）
        
        Args:
            knowledge_id: 知识 ID
            request: KnowledgeReferenceRequest 对象
        
        Returns:
            创建的 KnowledgeReference 对象
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        return self.record_reference(
            knowledge_id=knowledge_id,
            referenced_by=request.referenced_by,
            reference_context=f"{request.reference_type}:{request.reference_id}:{request.reference_name}"
        )
    
    def get_references(
        self,
        knowledge_id: int,
        limit: int = 100
    ) -> List[KnowledgeReference]:
        """
        获取知识条目的引用记录列表
        
        Args:
            knowledge_id: 知识 ID
            limit: 返回数量限制
        
        Returns:
            KnowledgeReference 对象列表
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        # 检查知识条目是否存在
        if not get_knowledge_by_id(self.db, knowledge_id):
            raise KnowledgeValidationError(f"知识条目 (ID={knowledge_id}) 不存在")
        
        return get_references_by_knowledge_id(self.db, knowledge_id, limit)
    
    # =========================================================================
    # 创建和更新知识
    # =========================================================================
    
    def create_knowledge_with_validation(
        self,
        knowledge_data: KnowledgeBaseCreate
    ) -> KnowledgeBase:
        """
        创建知识条目（带数据验证）
        
        验证规则：
        1. 标题不能为空且长度不超过 200 字符
        2. 分类不能为空
        3. Issue ID 和 Issue 编号必须有效
        
        Args:
            knowledge_data: KnowledgeBaseCreate 对象
        
        Returns:
            创建的 KnowledgeBase 对象
        
        Raises:
            KnowledgeValidationError: 验证失败时抛出
        """
        # 验证标题
        if not knowledge_data.title or not knowledge_data.title.strip():
            raise KnowledgeValidationError("知识标题不能为空")
        
        if len(knowledge_data.title.strip()) > 200:
            raise KnowledgeValidationError("知识标题长度不能超过 200 字符")
        
        # 验证分类
        if not knowledge_data.category or not knowledge_data.category.strip():
            raise KnowledgeValidationError("知识分类不能为空")
        
        if len(knowledge_data.category.strip()) > 50:
            raise KnowledgeValidationError("知识分类长度不能超过 50 字符")
        
        # 验证 Issue 编号
        if not knowledge_data.issue_no or not knowledge_data.issue_no.strip():
            raise KnowledgeValidationError("Issue 编号不能为空")
        
        if len(knowledge_data.issue_no.strip()) > 50:
            raise KnowledgeValidationError("Issue 编号长度不能超过 50 字符")
        
        # 验证描述（如果提供）
        if knowledge_data.description and len(knowledge_data.description) > 10000:
            raise KnowledgeValidationError("问题描述长度不能超过 10000 字符")
        
        # 调用 CRUD 层创建
        return create_knowledge(self.db, knowledge_data)
    
    def update_knowledge_with_validation(
        self,
        knowledge_id: int,
        knowledge_update: KnowledgeBaseUpdate
    ) -> KnowledgeBase:
        """
        更新知识条目（带数据验证）
        
        Args:
            knowledge_id: 知识 ID
            knowledge_update: KnowledgeBaseUpdate 对象
        
        Returns:
            更新后的 KnowledgeBase 对象
        
        Raises:
            KnowledgeValidationError: 验证失败或知识不存在时抛出
        """
        # 获取知识条目
        knowledge = get_knowledge_by_id(self.db, knowledge_id)
        
        if not knowledge:
            raise KnowledgeValidationError(f"知识条目 (ID={knowledge_id}) 不存在")
        
        # 验证更新数据
        self._validate_knowledge_update(knowledge_update)
        
        # 执行更新
        return update_knowledge(self.db, knowledge, knowledge_update)
    
    def _validate_knowledge_update(
        self,
        knowledge_update: KnowledgeBaseUpdate
    ) -> None:
        """
        验证知识更新数据
        
        Args:
            knowledge_update: KnowledgeBaseUpdate 对象
        
        Raises:
            KnowledgeValidationError: 验证失败时抛出
        """
        # 验证标题（如果提供）
        if knowledge_update.title is not None:
            if not knowledge_update.title.strip():
                raise KnowledgeValidationError("知识标题不能为空")
            if len(knowledge_update.title) > 200:
                raise KnowledgeValidationError("知识标题长度不能超过 200 字符")
        
        # 验证分类（如果提供）
        if knowledge_update.category is not None:
            if not knowledge_update.category.strip():
                raise KnowledgeValidationError("知识分类不能为空")
            if len(knowledge_update.category) > 50:
                raise KnowledgeValidationError("知识分类长度不能超过 50 字符")
        
        # 验证描述（如果提供）
        if knowledge_update.description is not None and len(knowledge_update.description) > 10000:
            raise KnowledgeValidationError("问题描述长度不能超过 10000 字符")
    
    # =========================================================================
    # 删除知识
    # =========================================================================
    
    def delete_knowledge_with_check(
        self,
        knowledge_id: int,
        operator: str
    ) -> Dict[str, Any]:
        """
        删除知识条目（带检查）
        
        Args:
            knowledge_id: 知识 ID
            operator: 操作人
        
        Returns:
            删除结果信息
        
        Raises:
            KnowledgeValidationError: 知识不存在时抛出
        """
        # 获取知识条目
        knowledge = get_knowledge_by_id(self.db, knowledge_id)
        
        if not knowledge:
            raise KnowledgeValidationError(f"知识条目 (ID={knowledge_id}) 不存在")
        
        # 获取引用记录数量（用于返回信息）
        references = get_references_by_knowledge_id(self.db, knowledge_id, limit=1)
        reference_count = len(references)
        
        # 如果有很多引用，可以给出警告（这里简化处理）
        # 实际项目中可以考虑阻止删除或软删除
        
        # 删除知识条目
        delete_knowledge(self.db, knowledge)
        
        return {
            "success": True,
            "message": f"知识条目 (ID={knowledge_id}) 已删除",
            "reference_count": reference_count,
            "operator": operator
        }
    
    # =========================================================================
    # 查询方法 - 业务层封装
    # =========================================================================
    
    def get_knowledge_by_id(self, knowledge_id: int) -> Optional[KnowledgeBase]:
        """
        根据 ID 获取知识条目（不增加浏览量）
        
        Args:
            knowledge_id: 知识 ID
        
        Returns:
            KnowledgeBase 对象，不存在则返回 None
        """
        return get_knowledge_by_id(self.db, knowledge_id)
    
    def get_featured_knowledge(self, category: Optional[str] = None, limit: int = 10) -> List[KnowledgeBase]:
        """
        获取精选知识条目
        
        Args:
            category: 可选的分类筛选
            limit: 返回数量限制
        
        Returns:
            精选知识条目列表
        """
        from crud import get_featured_knowledge
        return get_featured_knowledge(self.db, category, limit)
    
    def get_popular_knowledge(self, limit: int = 10) -> List[KnowledgeBase]:
        """
        获取热门知识条目（按浏览次数排序）
        
        Args:
            limit: 返回数量限制
        
        Returns:
            热门知识条目列表
        """
        from crud import get_popular_knowledge
        return get_popular_knowledge(self.db, limit)
    
    def get_knowledge_by_category(self, category: str, limit: int = 100) -> List[KnowledgeBase]:
        """
        按分类获取知识条目
        
        Args:
            category: 分类
            limit: 返回数量限制
        
        Returns:
            知识条目列表
        """
        from crud import get_knowledge_by_category
        return get_knowledge_by_category(self.db, category, None)[:limit]


# =============================================================================
# 便捷函数（可选）
# =============================================================================

def get_knowledge_service(db: Session) -> KnowledgeService:
    """
    获取 KnowledgeService 实例的便捷函数
    
    Args:
        db: 数据库会话
    
    Returns:
        KnowledgeService 实例
    """
    return KnowledgeService(db)
