"""
IssueResolutionService 解决服务
AutoCraft 问题跟踪系统 - Issue 解决业务逻辑服务
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from models.issue import Issue
from models.issue_status_log import IssueStatusLog
from crud.issue import (
    get_issue_by_id, update_issue as crud_update_issue,
    resolve_issue as crud_resolve_issue
)
from schemas.issue import IssueUpdate


class IssueResolutionError(Exception):
    """Issue 解决服务基础异常"""
    pass


class IssueResolutionValidationError(IssueResolutionError):
    """Issue 解决验证异常"""
    pass


class IssueResolutionPermissionError(IssueResolutionError):
    """Issue 解决权限异常"""
    pass


class IssueResolutionStatusError(IssueResolutionError):
    """Issue 解决状态异常"""
    pass


class IssueResolutionService:
    """
    Issue 解决业务逻辑服务类
    
    提供 Issue 的解决、编辑解决方案、验证等功能。
    只有处理中状态的 Issue 才能提交解决，提交后自动变更为已解决状态。
    
    Attributes:
        db: 数据库会话
    """
    
    # 允许提交解决的状态
    ALLOWED_RESOLUTION_STATUSES = ["处理中"]
    
    # 允许编辑解决方案的状态
    ALLOWED_EDIT_STATUSES = ["已解决"]
    
    def __init__(self, db: Session):
        """
        初始化 Issue 解决服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    # =========================================================================
    # 提交解决方案 - 解决 Issue
    # =========================================================================
    
    def submit_solution(
        self,
        issue_id: int,
        solution: str,
        resolved_by: str,
        solution_process: Optional[str] = None
    ) -> Issue:
        """
        提交解决方案（解决 Issue）
        
        功能：
        1. 验证 Issue 是否存在
        2. 验证 Issue 状态是否为"处理中"
        3. 验证解决方案数据
        4. 执行解决操作
        5. 自动变更状态为"已解决"
        6. 记录解决信息
        
        Args:
            issue_id: Issue ID
            solution: 解决方案（必填）
            resolved_by: 解决人
            solution_process: 解决过程（可选）
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueResolutionValidationError: Issue 不存在或验证失败
            IssueResolutionStatusError: 状态不允许提交解决
            IssueResolutionPermissionError: 权限不足
        """
        # 验证 Issue 是否存在
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueResolutionValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 验证 Issue 状态
        self._validate_resolution_status(issue)
        
        # 验证解决方案数据
        self.validate_solution(solution, resolved_by)
        
        # 执行解决操作（CRUD 层）
        updated_issue = crud_resolve_issue(
            self.db, issue, solution, solution_process, resolved_by
        )
        
        # 创建状态变更日志
        self._create_resolution_status_log(issue_id, resolved_by)
        
        return updated_issue
    
    # =========================================================================
    # 编辑解决方案 - 修改已解决的 Issue
    # =========================================================================
    
    def edit_solution(
        self,
        issue_id: int,
        solution: str,
        edited_by: str,
        solution_process: Optional[str] = None,
        edit_reason: Optional[str] = None
    ) -> Issue:
        """
        编辑解决方案（修改已解决的 Issue）
        
        功能：
        1. 验证 Issue 是否存在
        2. 验证 Issue 状态是否为"已解决"
        3. 验证解决方案数据
        4. 更新解决方案
        5. 记录编辑原因
        
        Args:
            issue_id: Issue ID
            solution: 新的解决方案
            edited_by: 编辑人
            solution_process: 解决过程（可选）
            edit_reason: 编辑原因（可选）
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueResolutionValidationError: Issue 不存在或验证失败
            IssueResolutionStatusError: 状态不允许编辑解决方案
        """
        # 验证 Issue 是否存在
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueResolutionValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 验证 Issue 状态
        self._validate_edit_status(issue)
        
        # 验证解决方案数据
        self.validate_solution(solution, edited_by)
        
        # 更新解决方案
        issue.solution = solution
        if solution_process is not None:
            issue.solution_process = solution_process
        
        # 如果有编辑原因，追加到解决过程中
        if edit_reason:
            if issue.solution_process:
                issue.solution_process = f"{issue.solution_process}\n编辑原因：{edit_reason}"
            else:
                issue.solution_process = f"编辑原因：{edit_reason}"
        
        issue.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(issue)
        
        return issue
    
    # =========================================================================
    # 验证解决方案
    # =========================================================================
    
    def validate_solution(self, solution: Optional[str], resolved_by: Optional[str]) -> bool:
        """
        验证解决方案数据
        
        验证规则：
        1. 解决方案不能为空
        2. 解决方案长度不能超过 10000 字符
        3. 解决人不能为空
        4. 解决人长度不能超过 100 字符
        
        Args:
            solution: 解决方案
            resolved_by: 解决人
        
        Returns:
            True 如果验证通过
        
        Raises:
            IssueResolutionValidationError: 验证失败时抛出
        """
        # 验证解决方案
        if solution is None or not solution.strip():
            raise IssueResolutionValidationError("解决方案不能为空")
        
        if len(solution.strip()) > 10000:
            raise IssueResolutionValidationError("解决方案长度不能超过 10000 字符")
        
        # 验证解决人
        if resolved_by is None or not resolved_by.strip():
            raise IssueResolutionValidationError("解决人不能为空")
        
        if len(resolved_by.strip()) > 100:
            raise IssueResolutionValidationError("解决人长度不能超过 100 字符")
        
        return True
    
    # =========================================================================
    # 状态验证
    # =========================================================================
    
    def _validate_resolution_status(self, issue: Issue) -> None:
        """
        验证 Issue 状态是否允许提交解决
        
        只有"处理中"状态的 Issue 才能提交解决。
        
        Args:
            issue: Issue 对象
        
        Raises:
            IssueResolutionStatusError: 状态不允许时抛出
        """
        if issue.status not in self.ALLOWED_RESOLUTION_STATUSES:
            allowed_msg = "、".join(self.ALLOWED_RESOLUTION_STATUSES)
            raise IssueResolutionStatusError(
                f"当前状态 '{issue.status}' 不允许提交解决。"
                f"只有状态为 {allowed_msg} 的 Issue 才能提交解决。"
            )
    
    def _validate_edit_status(self, issue: Issue) -> None:
        """
        验证 Issue 状态是否允许编辑解决方案
        
        只有"已解决"状态的 Issue 才能编辑解决方案。
        
        Args:
            issue: Issue 对象
        
        Raises:
            IssueResolutionStatusError: 状态不允许时抛出
        """
        if issue.status not in self.ALLOWED_EDIT_STATUSES:
            allowed_msg = "、".join(self.ALLOWED_EDIT_STATUSES)
            raise IssueResolutionStatusError(
                f"当前状态 '{issue.status}' 不允许编辑解决方案。"
                f"只有状态为 {allowed_msg} 的 Issue 才能编辑解决方案。"
            )
    
    # =========================================================================
    # 日志记录
    # =========================================================================
    
    def _create_resolution_status_log(
        self,
        issue_id: int,
        operator: str,
        operator_role: Optional[str] = None
    ) -> None:
        """
        创建解决时的状态变更日志
        
        Args:
            issue_id: Issue ID
            operator: 操作人
            operator_role: 操作人角色（可选）
        """
        try:
            from crud.issue_status_log import create_status_log
            create_status_log(
                db=self.db,
                issue_id=issue_id,
                from_status="处理中",
                to_status="已解决",
                operator=operator,
                operator_role=operator_role,
                reason="提交解决方案"
            )
        except Exception:
            # 日志记录失败不影响主流程
            pass
    
    # =========================================================================
    # 查询方法
    # =========================================================================
    
    def get_resolution_history(
        self,
        issue_id: int,
        limit: Optional[int] = None
    ) -> List[IssueStatusLog]:
        """
        获取 Issue 的解决历史记录
        
        Args:
            issue_id: Issue ID
            limit: 返回记录数量限制（可选）
        
        Returns:
            状态变更日志列表
        """
        try:
            from crud.issue_status_log import get_status_logs_by_issue_id
            return get_status_logs_by_issue_id(self.db, issue_id, limit)
        except Exception:
            return []
    
    def can_submit_solution(self, issue_id: int) -> bool:
        """
        检查 Issue 是否可以提交解决方案
        
        Args:
            issue_id: Issue ID
        
        Returns:
            True 如果可以提交，否则 False
        """
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            return False
        return issue.status in self.ALLOWED_RESOLUTION_STATUSES
    
    def can_edit_solution(self, issue_id: int) -> bool:
        """
        检查 Issue 是否可以编辑解决方案
        
        Args:
            issue_id: Issue ID
        
        Returns:
            True 如果可以编辑，否则 False
        """
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            return False
        return issue.status in self.ALLOWED_EDIT_STATUSES


# =============================================================================
# 便捷函数
# =============================================================================

def get_issue_resolution_service(db: Session) -> IssueResolutionService:
    """
    获取 IssueResolutionService 实例的便捷函数
    
    Args:
        db: 数据库会话
    
    Returns:
        IssueResolutionService 实例
    """
    return IssueResolutionService(db)
