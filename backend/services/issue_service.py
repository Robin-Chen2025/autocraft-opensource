"""
IssueService 业务逻辑层
AutoCraft 问题跟踪系统 - Issue 业务逻辑服务
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.issue import Issue
from models.issue_status_log import IssueStatusLog
from models.issue_assign_log import IssueAssignLog
from schemas.issue import IssueCreate, IssueUpdate, IssueStatus, IssueFilter
from crud import (
    create_issue, get_issue_by_id, get_issue_by_no, get_issues, update_issue,
    delete_issue, create_status_log, create_assign_log
)


class IssueServiceError(Exception):
    """Issue 服务基础异常"""
    pass


class IssueValidationError(IssueServiceError):
    """Issue 验证异常"""
    pass


class IssuePermissionError(IssueServiceError):
    """Issue 权限异常"""
    pass


class IssueStatusTransitionError(IssueServiceError):
    """Issue 状态流转异常"""
    pass


class IssueService:
    """
    Issue 业务逻辑服务类
    
    提供 Issue 的完整业务逻辑处理，包括：
    - 创建时的数据验证
    - 更新时的权限检查
    - 状态流转规则校验
    - 删除时的级联处理
    
    Attributes:
        db: 数据库会话
    """
    
    # 状态流转规则定义
    # key: 当前状态，value: 允许流转到的目标状态列表
    STATUS_TRANSITIONS = {
        "新建": ["处理中"],
        "处理中": ["已解决", "新建"],  # 支持重新打开
        "已解决": ["已关闭", "处理中"],  # 已解决可以重新打开
        "已关闭": ["处理中"],  # 已关闭可以重新打开
    }
    
    # 允许重新打开的状态（可以流转到"新建"或"处理中"）
    REOPEN_ALLOWED_STATUSES = ["已解决", "已关闭"]
    
    def __init__(self, db: Session):
        """
        初始化 Issue 服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    # =========================================================================
    # 创建 Issue - 带数据验证
    # =========================================================================
    
    def create_issue_with_validation(self, issue_data: IssueCreate) -> Issue:
        """
        创建 Issue（带数据验证）
        
        验证规则：
        1. 标题不能为空且长度不超过 100 字符
        2. 分类和优先级必须有效
        3. 项目必须存在（通过 project_id 验证）
        4. 初始状态自动设置为"新建"
        
        Args:
            issue_data: Issue 创建数据
        
        Returns:
            创建的 Issue 对象
        
        Raises:
            IssueValidationError: 验证失败时抛出
        """
        # 验证标题
        if not issue_data.title or not issue_data.title.strip():
            raise IssueValidationError("问题标题不能为空")
        
        if len(issue_data.title.strip()) > 100:
            raise IssueValidationError("问题标题长度不能超过 100 字符")
        
        # 验证描述（如果提供）
        if issue_data.description and len(issue_data.description) > 10000:
            raise IssueValidationError("问题描述长度不能超过 10000 字符")
        
        # 验证项目 ID
        if issue_data.project_id <= 0:
            raise IssueValidationError("项目 ID 必须为正整数")
        
        # 验证阶段 ID（如果提供）
        if issue_data.stage_id is not None and issue_data.stage_id <= 0:
            raise IssueValidationError("阶段 ID 必须为正整数")
        
        # 验证工作流 ID（如果提供）
        if issue_data.workflow_id is not None and issue_data.workflow_id <= 0:
            raise IssueValidationError("工作流 ID 必须为正整数")
        
        # 验证创建人
        if not issue_data.created_by or not issue_data.created_by.strip():
            raise IssueValidationError("创建人不能为空")
        
        # 调用 CRUD 层创建
        return create_issue(self.db, issue_data)
    
    # =========================================================================
    # 更新 Issue - 带权限检查
    # =========================================================================
    
    def update_issue_with_permission_check(
        self,
        issue_id: int,
        issue_update: IssueUpdate,
        current_user: str,
        allowed_roles: Optional[List[str]] = None
    ) -> Issue:
        """
        更新 Issue（带权限检查）
        
        权限规则：
        1. 创建人可以更新
        2. 当前处理人可以更新
        3. 指定角色的用户可以更新（默认：admin, manager）
        4. 状态变更需要通过 change_status 方法
        
        Args:
            issue_id: Issue ID
            issue_update: Issue 更新数据
            current_user: 当前用户
            allowed_roles: 允许更新的角色列表（默认：["admin", "manager"]）
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssuePermissionError: 权限不足时抛出
            IssueValidationError: 验证失败时抛出
        """
        if allowed_roles is None:
            allowed_roles = ["admin", "manager"]
        
        # 获取 Issue
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 检查权限
        if not self._has_update_permission(issue, current_user, allowed_roles):
            raise IssuePermissionError(
                f"用户 {current_user} 没有权限更新 Issue {issue.issue_no}"
            )
        
        # 如果尝试更新状态，提示使用 change_status 方法
        if issue_update.status is not None:
            status_value = issue_update.status.value if hasattr(issue_update.status, 'value') else str(issue_update.status)
            if status_value != issue.status:
                raise IssueValidationError(
                    "状态变更请使用 change_status 方法，不要直接更新 status 字段"
                )
        
        # 验证更新数据
        self._validate_issue_update(issue_update)
        
        # 执行更新
        return update_issue(self.db, issue, issue_update)
    
    def _has_update_permission(
        self,
        issue: Issue,
        current_user: str,
        allowed_roles: List[str]
    ) -> bool:
        """
        检查用户是否有更新权限
        
        Args:
            issue: Issue 对象
            current_user: 当前用户
            allowed_roles: 允许的角色列表
        
        Returns:
            True 如果有权限，否则 False
        """
        # 创建人可以更新
        if issue.created_by == current_user:
            return True
        
        # 当前处理人可以更新
        if issue.assignee == current_user:
            return True
        
        # 检查角色（这里简化处理，实际项目中应该从用户服务获取角色）
        # 假设 current_user 格式为 "role:username" 或通过其他方式判断角色
        for role in allowed_roles:
            if current_user.startswith(f"{role}:") or current_user == role:
                return True
        
        return False
    
    def _validate_issue_update(self, issue_update: IssueUpdate) -> None:
        """
        验证 Issue 更新数据
        
        Args:
            issue_update: Issue 更新数据
        
        Raises:
            IssueValidationError: 验证失败时抛出
        """
        # 验证标题（如果提供）
        if issue_update.title is not None:
            if not issue_update.title.strip():
                raise IssueValidationError("问题标题不能为空")
            if len(issue_update.title) > 100:
                raise IssueValidationError("问题标题长度不能超过 100 字符")
        
        # 验证描述（如果提供）
        if issue_update.description is not None and len(issue_update.description) > 10000:
            raise IssueValidationError("问题描述长度不能超过 10000 字符")
        
        # 验证处理人（如果提供）
        if issue_update.assignee is not None and len(issue_update.assignee) > 100:
            raise IssueValidationError("处理人长度不能超过 100 字符")
    
    # =========================================================================
    # 状态变更 - 带流转规则校验
    # =========================================================================
    
    def change_status(
        self,
        issue_id: int,
        new_status: IssueStatus | str,
        operator: str,
        reason: Optional[str] = None,
        operator_role: Optional[str] = None
    ) -> Issue:
        """
        变更 Issue 状态（带流转规则校验）
        
        状态流转规则：
        - 新建 -> 处理中
        - 处理中 -> 已解决
        - 已解决 -> 已关闭
        - 已解决/已关闭 -> 处理中（重新打开）
        - 处理中 -> 新建（重新打开）
        
        Args:
            issue_id: Issue ID
            new_status: 新状态
            operator: 操作人
            reason: 变更原因（可选）
            operator_role: 操作人角色（可选）
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueValidationError: Issue 不存在或状态无效
            IssueStatusTransitionError: 状态流转不合法时抛出
        """
        # 获取 Issue
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 转换新状态为字符串
        new_status_str = new_status.value if hasattr(new_status, 'value') else str(new_status)
        
        # 验证状态值有效性
        valid_statuses = ["新建", "处理中", "已解决", "已关闭"]
        if new_status_str not in valid_statuses:
            raise IssueValidationError(
                f"无效的状态值：{new_status_str}，有效值为：{', '.join(valid_statuses)}"
            )
        
        # 如果状态没有变化，直接返回
        if issue.status == new_status_str:
            return issue
        
        # 校验状态流转规则
        self._validate_status_transition(issue.status, new_status_str)
        
        # 保存旧状态用于日志
        old_status = issue.status
        
        # 执行状态更新
        update_data = IssueUpdate(status=new_status)
        updated_issue = update_issue(self.db, issue, update_data)
        
        # 创建状态变更日志
        create_status_log(
            db=self.db,
            issue_id=issue_id,
            from_status=old_status,
            to_status=new_status_str,
            operator=operator,
            operator_role=operator_role,
            reason=reason
        )
        
        # 如果重新打开，清除相关字段
        if self._is_reopen_operation(old_status, new_status_str):
            if new_status_str in ["新建", "处理中"]:
                # 重新打开时清除解决和关闭信息
                updated_issue.resolved_by = None
                updated_issue.resolved_at = None
                updated_issue.closed_by = None
                updated_issue.closed_at = None
                updated_issue.solution = None
                self.db.commit()
                self.db.refresh(updated_issue)
        
        return updated_issue
    
    def _validate_status_transition(self, from_status: str, to_status: str) -> None:
        """
        验证状态流转是否合法
        
        Args:
            from_status: 当前状态
            to_status: 目标状态
        
        Raises:
            IssueStatusTransitionError: 流转不合法时抛出
        """
        allowed_transitions = self.STATUS_TRANSITIONS.get(from_status, [])
        
        if to_status not in allowed_transitions:
            # 构建错误信息
            allowed_msg = " -> ".join(allowed_transitions) if allowed_transitions else "无允许的操作"
            raise IssueStatusTransitionError(
                f"状态流转不合法：不能从 '{from_status}' 流转到 '{to_status}'。"
                f"允许的流转：{from_status} -> {allowed_msg}"
            )
    
    def _is_reopen_operation(self, from_status: str, to_status: str) -> bool:
        """
        判断是否是重新打开操作
        
        Args:
            from_status: 当前状态
            to_status: 目标状态
        
        Returns:
            True 如果是重新打开操作，否则 False
        """
        return from_status in self.REOPEN_ALLOWED_STATUSES or (
            from_status == "处理中" and to_status == "新建"
        )
    
    def reopen_issue(
        self,
        issue_id: int,
        operator: str,
        reason: Optional[str] = None,
        operator_role: Optional[str] = None
    ) -> Issue:
        """
        重新打开 Issue（便捷方法）
        
        自动判断目标状态：
        - 已解决/已关闭 -> 处理中
        - 处理中 -> 新建（如果需要退回）
        
        Args:
            issue_id: Issue ID
            operator: 操作人
            reason: 重新打开原因
            operator_role: 操作人角色
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueValidationError: Issue 不存在或不允许重新打开
            IssueStatusTransitionError: 状态流转不合法
        """
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 判断目标状态
        if issue.status in ["已解决", "已关闭"]:
            target_status = "处理中"
        elif issue.status == "处理中":
            target_status = "新建"
        else:
            raise IssueStatusTransitionError(
                f"当前状态 '{issue.status}' 不允许重新打开操作"
            )
        
        return self.change_status(
            issue_id=issue_id,
            new_status=target_status,
            operator=operator,
            reason=reason or "重新打开 Issue",
            operator_role=operator_role
        )
    
    # =========================================================================
    # 删除 Issue - 带级联处理
    # =========================================================================
    
    def delete_issue_with_cascade(
        self,
        issue_id: int,
        operator: str,
        soft_delete: bool = False
    ) -> Dict[str, Any]:
        """
        删除 Issue（带级联处理）
        
        级联删除：
        1. Issue 状态日志
        2. Issue 分配日志
        3. Issue 任务关联
        4. Issue 摘要
        
        Args:
            issue_id: Issue ID
            operator: 操作人
            soft_delete: 是否软删除（默认 False，硬删除）
        
        Returns:
            删除结果信息
        
        Raises:
            IssueValidationError: Issue 不存在
        """
        # 获取 Issue
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueValidationError(f"Issue (ID={issue_id}) 不存在")
        
        issue_no = issue.issue_no
        
        # 统计关联数据
        cascade_info = self._get_cascade_info(issue_id)
        
        if soft_delete:
            # 软删除：标记状态为已删除（需要模型支持 deleted 字段）
            # 这里简化处理，实际项目中应该添加 deleted 字段和 deleted_at 字段
            update_data = IssueUpdate(status="已删除")
            update_issue(self.db, issue, update_data)
            
            return {
                "success": True,
                "message": f"Issue {issue_no} 已软删除",
                "issue_no": issue_no,
                "cascade_count": cascade_info["total"],
                "cascade_details": cascade_info
            }
        else:
            # 硬删除：直接删除 Issue，SQLAlchemy 会自动级联删除关联数据
            delete_issue(self.db, issue)
            
            return {
                "success": True,
                "message": f"Issue {issue_no} 及其关联数据已删除",
                "issue_no": issue_no,
                "cascade_count": cascade_info["total"],
                "cascade_details": cascade_info
            }
    
    def _get_cascade_info(self, issue_id: int) -> Dict[str, Any]:
        """
        获取级联关联数据信息
        
        Args:
            issue_id: Issue ID
        
        Returns:
            关联数据信息字典
        """
        # 查询状态日志数量
        status_logs_count = self.db.query(IssueStatusLog).filter(
            IssueStatusLog.issue_id == issue_id
        ).count()
        
        # 查询分配日志数量
        assign_logs_count = self.db.query(IssueAssignLog).filter(
            IssueAssignLog.issue_id == issue_id
        ).count()
        
        # 查询任务关联数量（如果表存在）
        try:
            from models.issue_task_relation import IssueTaskRelation
            task_relations_count = self.db.query(IssueTaskRelation).filter(
                IssueTaskRelation.issue_id == issue_id
            ).count()
        except Exception:
            task_relations_count = 0
        
        return {
            "status_logs": status_logs_count,
            "assign_logs": assign_logs_count,
            "task_relations": task_relations_count,
            "total": status_logs_count + assign_logs_count + task_relations_count
        }
    
    # =========================================================================
    # 查询方法 - 业务层封装
    # =========================================================================
    
    def get_issue_detail(self, issue_id: int) -> Optional[Issue]:
        """
        获取 Issue 详情
        
        Args:
            issue_id: Issue ID
        
        Returns:
            Issue 对象，不存在则返回 None
        """
        return get_issue_by_id(self.db, issue_id)
    
    def get_issue_by_no(self, issue_no: str) -> Optional[Issue]:
        """
        根据编号获取 Issue
        
        Args:
            issue_no: Issue 编号
        
        Returns:
            Issue 对象，不存在则返回 None
        """
        return get_issue_by_no(self.db, issue_no)
    
    def get_issues_list(
        self,
        params: IssueFilter
    ) -> tuple[List[Issue], int]:
        """
        获取 Issue 列表
        
        Args:
            params: 查询参数
        
        Returns:
            (Issue 列表，总记录数)
        """
        return get_issues(self.db, params)
    
    def get_issue_status_history(self, issue_id: int, limit: int = 10) -> List[IssueStatusLog]:
        """
        获取 Issue 状态变更历史
        
        Args:
            issue_id: Issue ID
            limit: 返回记录数量限制
        
        Returns:
            状态变更日志列表
        """
        return create_status_log.__globals__.get('get_status_logs_by_issue_id', lambda *args: [])(
            self.db, issue_id, limit
        ) if hasattr(create_status_log, '__globals__') else []
    
    def assign_issue(
        self,
        issue_id: int,
        assignee: str,
        assigned_by: str,
        due_date: Optional[datetime] = None,
        assign_note: Optional[str] = None
    ) -> Issue:
        """
        分配 Issue（带日志记录）
        
        Args:
            issue_id: Issue ID
            assignee: 处理人
            assigned_by: 分配操作人
            due_date: 截止日期
            assign_note: 分配说明
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueValidationError: Issue 不存在
        """
        issue = get_issue_by_id(self.db, issue_id)
        if not issue:
            raise IssueValidationError(f"Issue (ID={issue_id}) 不存在")
        
        # 保存旧的处理人
        old_assignee = issue.assignee
        
        # 导入 CRUD 的 assign_issue 函数
        from crud.issue import assign_issue as crud_assign_issue
        updated_issue = crud_assign_issue(
            self.db, issue, assignee, due_date, assign_note
        )
        
        # 创建分配日志
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
    
    def resolve_issue(
        self,
        issue_id: int,
        solution: str,
        resolved_by: str,
        solution_process: Optional[str] = None
    ) -> Issue:
        """
        解决 Issue（带状态流转）
        
        Args:
            issue_id: Issue ID
            solution: 解决方案
            resolved_by: 解决人
            solution_process: 解决过程
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueValidationError: Issue 不存在
            IssueStatusTransitionError: 状态流转不合法
        """
        # 先变更状态到"已解决"
        issue = self.change_status(
            issue_id=issue_id,
            new_status="已解决",
            operator=resolved_by,
            reason="解决问题"
        )
        
        # 更新解决方案信息
        from crud.issue import resolve_issue as crud_resolve_issue
        updated_issue = crud_resolve_issue(
            self.db, issue, solution, solution_process, resolved_by
        )
        
        return updated_issue
    
    def close_issue(
        self,
        issue_id: int,
        closed_by: str,
        closed_reason: Optional[str] = None
    ) -> Issue:
        """
        关闭 Issue（带状态流转）
        
        Args:
            issue_id: Issue ID
            closed_by: 关闭人
            closed_reason: 关闭原因
        
        Returns:
            更新后的 Issue 对象
        
        Raises:
            IssueValidationError: Issue 不存在
            IssueStatusTransitionError: 状态流转不合法
        """
        # 先变更状态到"已关闭"
        issue = self.change_status(
            issue_id=issue_id,
            new_status="已关闭",
            operator=closed_by,
            reason=closed_reason or "关闭 Issue"
        )
        
        # 更新关闭信息
        from crud.issue import close_issue as crud_close_issue
        updated_issue = crud_close_issue(
            self.db, issue, closed_by, closed_reason
        )
        
        return updated_issue


# =============================================================================
# 便捷函数（可选）
# =============================================================================

def get_issue_service(db: Session) -> IssueService:
    """
    获取 IssueService 实例的便捷函数
    
    Args:
        db: 数据库会话
    
    Returns:
        IssueService 实例
    """
    return IssueService(db)
