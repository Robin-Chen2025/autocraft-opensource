"""
IssueAssignmentService 分配服务
AutoCraft 问题跟踪系统 - Issue 分配业务逻辑服务
"""
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from models.issue import Issue
from models.issue_assign_log import IssueAssignLog
from crud.issue import (
    get_issue_by_id, assign_issue as crud_assign_issue,
    update_issue as crud_update_issue
)
from crud.issue_assign_log import create_assign_log, get_assign_logs_by_issue_id
from schemas.issue import IssueUpdate


class IssueAssignmentError(Exception):
    """Issue 分配服务基础异常"""
    pass


class IssueAssignmentValidationError(IssueAssignmentError):
    """Issue 分配验证异常"""
    pass


class IssueAssignmentPermissionError(IssueAssignmentError):
    """Issue 分配权限异常"""
    pass


class IssueAssignmentService:
    """
    Issue 分配业务逻辑服务类
    
    提供 Issue 的分配、重新分配、处理人验证等功能。
    分配后自动变更状态为处理中，并记录分配日志。
    
    Attributes:
        db: 数据库会话
    """
    
    def __init__(self, db: Session):
        """
        初始化 Issue 分配服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    # =========================================================================
    # 分配 Issue - 首次分配
    # =========================================================================
    
    def assign_issue(
        self,
        issue_id: int,
        assignee: str,
        assigned_by: str,
        due_date: Optional[datetime] = None,
        assign_note: Optional[str] = None
    ) -> Issue:
        """
        分配 Issue（首次分配）
        
        功能：
        1. 验证 Issue 是否存在
        2. 验证处理人是否有效
        3. 执行分配操作
        4. 自动变更状态为"处理中"（如果当前状态为"新建"）
        5. 记录分配日志
        
        Args:
            issue_id: Issue ID
            assignee: 处理人
            assigned_by: 分配操作人
            due_date: 截止日期（可选）
            assign_note: 分配说明（可选）
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueAssignmentValidationError: Issue 不存在或验证失败
            IssueAssignmentPermissionError: 权限不足
        """
        # 验证 Issue 是否存在
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueAssignmentValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 验证处理人
        self.validate_assignee(assignee)
        
        # 检查是否允许分配（只有新建状态的 Issue 才能首次分配）
        if issue.assignee is not None and issue.assignee != "":
            raise IssueAssignmentValidationError(
                f"Issue {issue.issue_no} 已经有处理人 ({issue.assignee})，请使用 reassign_issue 方法进行重新分配"
            )
        
        # 保存旧的处理人（用于日志）
        old_assignee = issue.assignee
        
        # 执行分配操作（CRUD 层）
        updated_issue = crud_assign_issue(
            self.db, issue, assignee, due_date, assign_note
        )
        
        # 记录分配日志
        create_assign_log(
            db=self.db,
            issue_id=issue_id,
            from_assignee=old_assignee,
            to_assignee=assignee,
            assigned_by=assigned_by,
            due_date=due_date,
            note=assign_note
        )
        
        return updated_issue
    
    # =========================================================================
    # 重新分配 Issue - 变更处理人
    # =========================================================================
    
    def reassign_issue(
        self,
        issue_id: int,
        new_assignee: str,
        assigned_by: str,
        due_date: Optional[datetime] = None,
        assign_note: Optional[str] = None
    ) -> Issue:
        """
        重新分配 Issue（变更处理人）
        
        功能：
        1. 验证 Issue 是否存在
        2. 验证新处理人是否有效
        3. 执行重新分配操作
        4. 保持状态为"处理中"（如果当前状态不是"处理中"）
        5. 记录分配日志
        
        Args:
            issue_id: Issue ID
            new_assignee: 新处理人
            assigned_by: 分配操作人
            due_date: 截止日期（可选）
            assign_note: 分配说明（可选）
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueAssignmentValidationError: Issue 不存在或验证失败
            IssueAssignmentPermissionError: 权限不足
        """
        # 验证 Issue 是否存在
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueAssignmentValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 验证新处理人
        self.validate_assignee(new_assignee)
        
        # 检查是否有处理人可以被重新分配
        if issue.assignee is None or issue.assignee == "":
            raise IssueAssignmentValidationError(
                f"Issue {issue.issue_no} 尚未分配处理人，请使用 assign_issue 方法进行首次分配"
            )
        
        # 保存旧的处理人（用于日志）
        old_assignee = issue.assignee
        
        # 如果处理人没有变化，直接返回
        if old_assignee == new_assignee:
            return issue
        
        # 执行分配操作（CRUD 层会处理状态变更）
        updated_issue = crud_assign_issue(
            self.db, issue, new_assignee, due_date, assign_note
        )
        
        # 记录分配日志
        create_assign_log(
            db=self.db,
            issue_id=issue_id,
            from_assignee=old_assignee,
            to_assignee=new_assignee,
            assigned_by=assigned_by,
            due_date=due_date,
            note=assign_note
        )
        
        return updated_issue
    
    # =========================================================================
    # 验证处理人
    # =========================================================================
    
    def validate_assignee(self, assignee: Optional[str]) -> bool:
        """
        验证处理人是否有效
        
        验证规则：
        1. 处理人不能为空
        2. 处理人长度不能超过 100 字符
        3. 处理人不能只包含空白字符
        
        Args:
            assignee: 处理人
        
        Returns:
            True 如果有效
        
        Raises:
            IssueAssignmentValidationError: 验证失败时抛出
        """
        if assignee is None or not assignee.strip():
            raise IssueAssignmentValidationError("处理人不能为空")
        
        if len(assignee.strip()) > 100:
            raise IssueAssignmentValidationError("处理人长度不能超过 100 字符")
        
        return True
    
    # =========================================================================
    # 查询分配历史
    # =========================================================================
    
    def get_assignment_history(
        self,
        issue_id: int,
        limit: Optional[int] = None
    ) -> List[IssueAssignLog]:
        """
        获取 Issue 的分配历史记录
        
        Args:
            issue_id: Issue ID
            limit: 返回记录数量限制（可选，默认返回全部）
        
        Returns:
            分配日志列表，按创建时间倒序排列
        """
        return get_assign_logs_by_issue_id(self.db, issue_id, limit)
    
    # =========================================================================
    # 批量分配
    # =========================================================================
    
    def batch_assign_issues(
        self,
        issue_ids: List[int],
        assignee: str,
        assigned_by: str,
        due_date: Optional[datetime] = None,
        assign_note: Optional[str] = None
    ) -> Tuple[List[Issue], List[str]]:
        """
        批量分配 Issue
        
        功能：
        1. 批量验证 Issue 是否存在
        2. 批量验证处理人
        3. 执行批量分配
        4. 记录每条分配日志
        
        Args:
            issue_ids: Issue ID 列表
            assignee: 处理人
            assigned_by: 分配操作人
            due_date: 截止日期（可选）
            assign_note: 分配说明（可选）
        
        Returns:
            (成功分配的 Issue 列表，失败的 Issue ID 列表)
        """
        # 验证处理人
        self.validate_assignee(assignee)
        
        successful_issues = []
        failed_issue_ids = []
        
        for issue_id in issue_ids:
            try:
                # 验证 Issue 是否存在
                issue = get_issue_by_id(self.db, issue_id)
                if not issue:
                    failed_issue_ids.append(str(issue_id))
                    continue
                
                # 检查是否已有处理人
                if issue.assignee is not None and issue.assignee != "":
                    # 已有处理人，使用重新分配
                    updated_issue = self.reassign_issue(
                        issue_id=issue_id,
                        new_assignee=assignee,
                        assigned_by=assigned_by,
                        due_date=due_date,
                        assign_note=assign_note
                    )
                else:
                    # 首次分配
                    updated_issue = self.assign_issue(
                        issue_id=issue_id,
                        assignee=assignee,
                        assigned_by=assigned_by,
                        due_date=due_date,
                        assign_note=assign_note
                    )
                
                successful_issues.append(updated_issue)
                
            except Exception:
                failed_issue_ids.append(str(issue_id))
        
        return successful_issues, failed_issue_ids
    
    # =========================================================================
    # 取消分配
    # =========================================================================
    
    def unassign_issue(
        self,
        issue_id: int,
        unassigned_by: str,
        reason: Optional[str] = None
    ) -> Issue:
        """
        取消 Issue 分配
        
        功能：
        1. 验证 Issue 是否存在
        2. 清除处理人信息
        3. 状态回退到"新建"
        4. 记录分配日志
        
        Args:
            issue_id: Issue ID
            unassigned_by: 取消分配操作人
            reason: 取消原因（可选）
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueAssignmentValidationError: Issue 不存在或尚未分配
        """
        # 验证 Issue 是否存在
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueAssignmentValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 检查是否有处理人可以被取消
        if issue.assignee is None or issue.assignee == "":
            raise IssueAssignmentValidationError(
                f"Issue {issue.issue_no} 尚未分配处理人"
            )
        
        # 保存旧的处理人（用于日志）
        old_assignee = issue.assignee
        
        # 清除处理人信息
        issue.assignee = None
        issue.assigned_at = None
        issue.due_date = None
        issue.assign_note = reason
        issue.status = "新建"
        issue.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(issue)
        
        # 记录分配日志
        create_assign_log(
            db=self.db,
            issue_id=issue_id,
            from_assignee=old_assignee,
            to_assignee=None,
            assigned_by=unassigned_by,
            due_date=None,
            note=reason or "取消分配"
        )
        
        return issue


# =============================================================================
# 便捷函数
# =============================================================================

def get_issue_assignment_service(db: Session) -> IssueAssignmentService:
    """
    获取 IssueAssignmentService 实例的便捷函数
    
    Args:
        db: 数据库会话
    
    Returns:
        IssueAssignmentService 实例
    """
    return IssueAssignmentService(db)
