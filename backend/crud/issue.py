"""
Issue 数据库 CRUD 操作模块
AutoCraft 问题跟踪系统 - Issue 数据操作层
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from models.issue import Issue
from schemas.issue import IssueCreate, IssueUpdate, IssueFilter
from utils import generate_task_no
import random


def generate_issue_no(db: Session) -> str:
    """
    生成 Issue 编号
    格式：ISSUE-YYYYMMDD-NNNN
    NNNN 为 4 位序号，从 0001 开始，每日重置
    
    Args:
        db: 数据库会话
    
    Returns:
        生成的 Issue 编号
    """
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    prefix = f"ISSUE-{date_str}-"
    
    # 查询今日已存在的 Issue 编号
    today_issues = db.query(Issue).filter(
        Issue.issue_no.like(f"{prefix}%")
    ).all()
    
    # 计算下一个序号
    next_seq = len(today_issues) + 1
    return f"{prefix}{next_seq:04d}"


def create_issue(db: Session, issue_data: IssueCreate) -> Issue:
    """
    创建 Issue
    
    Args:
        db: 数据库会话
        issue_data: Issue 创建数据
    
    Returns:
        创建的 Issue 对象
    """
    db_issue = Issue(
        issue_no=generate_issue_no(db),
        title=issue_data.title,
        description=issue_data.description,
        category=issue_data.category.value if hasattr(issue_data.category, 'value') else str(issue_data.category),
        priority=issue_data.priority.value if hasattr(issue_data.priority, 'value') else str(issue_data.priority),
        status="新建",
        project_id=issue_data.project_id,
        stage_id=issue_data.stage_id,
        workflow_id=issue_data.workflow_id,
        created_by=issue_data.created_by,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


def get_issue_by_id(db: Session, issue_id: int) -> Optional[Issue]:
    """
    根据 Issue ID 获取 Issue
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
    
    Returns:
        Issue 对象，不存在则返回 None
    """
    return db.query(Issue).filter(Issue.id == issue_id).first()


def get_issue_by_no(db: Session, issue_no: str) -> Optional[Issue]:
    """
    根据 Issue 编号获取 Issue
    
    Args:
        db: 数据库会话
        issue_no: Issue 编号
    
    Returns:
        Issue 对象，不存在则返回 None
    """
    return db.query(Issue).filter(Issue.issue_no == issue_no).first()


def get_issues(db: Session, params: IssueFilter) -> tuple[list[Issue], int]:
    """
    获取 Issue 列表（支持分页和多字段组合搜索）
    
    Args:
        db: 数据库会话
        params: Issue 查询参数
    
    Returns:
        (Issue 列表，总记录数)
    """
    query = db.query(Issue)
    
    # 关键词搜索（标题和描述）
    if params.keyword:
        query = query.filter(
            or_(
                Issue.title.contains(params.keyword),
                Issue.description.contains(params.keyword)
            )
        )
    
    # 状态筛选
    if params.status:
        status_value = params.status.value if hasattr(params.status, 'value') else str(params.status)
        query = query.filter(Issue.status == status_value)
    
    # 分类筛选
    if params.category:
        category_value = params.category.value if hasattr(params.category, 'value') else str(params.category)
        query = query.filter(Issue.category == category_value)
    
    # 优先级筛选
    if params.priority:
        priority_value = params.priority.value if hasattr(params.priority, 'value') else str(params.priority)
        query = query.filter(Issue.priority == priority_value)
    
    # 创建人筛选
    if params.creator:
        query = query.filter(Issue.created_by.contains(params.creator))
    
    # 处理人筛选
    if params.assignee:
        query = query.filter(Issue.assignee.contains(params.assignee))
    
    # 项目 ID 筛选
    if params.project_id is not None:
        query = query.filter(Issue.project_id == params.project_id)
    
    # 阶段 ID 筛选
    if params.stage_id is not None:
        query = query.filter(Issue.stage_id == params.stage_id)
    
    # 工作流 ID 筛选
    if params.workflow_id is not None:
        query = query.filter(Issue.workflow_id == params.workflow_id)
    
    # 关联任务单号筛选
    if params.related_task_id:
        # 注意：related_task_id 在 Issue 模型中不存在，这里需要根据实际情况调整
        # 如果后续添加该字段，可以取消注释
        # query = query.filter(Issue.related_task_id == params.related_task_id)
        pass
    
    # 创建时间范围查询
    if params.created_at_from:
        query = query.filter(Issue.created_at >= params.created_at_from)
    if params.created_at_to:
        query = query.filter(Issue.created_at <= params.created_at_to)
    
    # 计算总记录数
    total = query.count()
    
    # 分页和排序（按创建时间倒序）
    offset = (params.page - 1) * params.page_size
    issues = query.order_by(desc(Issue.created_at)).offset(offset).limit(params.page_size).all()
    
    return issues, total


def update_issue(db: Session, issue: Issue, issue_update: IssueUpdate) -> Issue:
    """
    更新 Issue
    
    Args:
        db: 数据库会话
        issue: Issue 对象
        issue_update: Issue 更新数据
    
    Returns:
        更新后的 Issue 对象
    """
    update_data = issue_update.model_dump(exclude_unset=True)
    
    # 处理枚举类型的转换
    if 'category' in update_data and update_data['category'] is not None:
        update_data['category'] = update_data['category'].value if hasattr(update_data['category'], 'value') else str(update_data['category'])
    if 'priority' in update_data and update_data['priority'] is not None:
        update_data['priority'] = update_data['priority'].value if hasattr(update_data['priority'], 'value') else str(update_data['priority'])
    if 'status' in update_data and update_data['status'] is not None:
        update_data['status'] = update_data['status'].value if hasattr(update_data['status'], 'value') else str(update_data['status'])
    
    # 状态变更时自动设置时间
    new_status = update_data.get('status')
    if new_status:
        # 处理中 → 记录指派时间
        if new_status in ['处理中', 'in_progress']:
            if not issue.assigned_at:
                update_data['assigned_at'] = datetime.now()
        # 已解决 → 记录解决时间
        elif new_status in ['已解决', 'resolved']:
            if not issue.resolved_at:
                update_data['resolved_at'] = datetime.now()
        # 已关闭 → 记录关闭时间
        elif new_status in ['已关闭', 'closed']:
            if not issue.closed_at:
                update_data['closed_at'] = datetime.now()
    
    # 更新时间
    update_data['updated_at'] = datetime.now()
    
    # 更新字段
    for field, value in update_data.items():
        setattr(issue, field, value)
    
    db.commit()
    db.refresh(issue)
    return issue


def delete_issue(db: Session, issue: Issue) -> None:
    """
    删除 Issue（级联删除）
    
    Args:
        db: 数据库会话
        issue: Issue 对象
    
    Note:
        级联删除相关的 Issue 状态日志、分配日志、任务关联等
    """
    # SQLAlchemy 的 relationship 已配置级联删除
    # 这里只需删除 Issue 本身
    db.delete(issue)
    db.commit()


def issue_exists(db: Session, issue_id: int) -> bool:
    """
    检查 Issue 是否存在
    
    Args:
        db: 数据库会话
        issue_id: Issue ID
    
    Returns:
        True 如果存在，否则 False
    """
    return get_issue_by_id(db, issue_id) is not None


def issue_no_exists(db: Session, issue_no: str) -> bool:
    """
    检查 Issue 编号是否存在
    
    Args:
        db: 数据库会话
        issue_no: Issue 编号
    
    Returns:
        True 如果存在，否则 False
    """
    return get_issue_by_no(db, issue_no) is not None


def get_issues_by_project(db: Session, project_id: int, status: Optional[str] = None) -> list[Issue]:
    """
    按项目查询 Issue
    
    Args:
        db: 数据库会话
        project_id: 项目 ID
        status: 可选的状态筛选
    
    Returns:
        Issue 列表
    """
    query = db.query(Issue).filter(Issue.project_id == project_id)
    if status:
        query = query.filter(Issue.status == status)
    return query.order_by(desc(Issue.created_at)).all()


def get_issues_by_assignee(db: Session, assignee: str, status: Optional[str] = None) -> list[Issue]:
    """
    按处理人查询 Issue
    
    Args:
        db: 数据库会话
        assignee: 处理人
        status: 可选的状态筛选
    
    Returns:
        Issue 列表
    """
    query = db.query(Issue).filter(Issue.assignee == assignee)
    if status:
        query = query.filter(Issue.status == status)
    return query.order_by(desc(Issue.created_at)).all()


def assign_issue(db: Session, issue: Issue, assignee: str, due_date: Optional[datetime] = None, 
                 assign_note: Optional[str] = None) -> Issue:
    """
    分配 Issue
    
    Args:
        db: 数据库会话
        issue: Issue 对象
        assignee: 处理人
        due_date: 截止日期
        assign_note: 分配说明
    
    Returns:
        更新后的 Issue 对象
    """
    issue.assignee = assignee
    issue.assigned_at = datetime.now()
    issue.assign_note = assign_note
    issue.due_date = due_date
    issue.updated_at = datetime.now()
    
    # 如果状态是新建，自动改为处理中
    if issue.status == "新建":
        issue.status = "处理中"
    
    db.commit()
    db.refresh(issue)
    return issue


def resolve_issue(db: Session, issue: Issue, solution: str, 
                  solution_process: Optional[str] = None, 
                  resolved_by: Optional[str] = None) -> Issue:
    """
    解决 Issue
    
    Args:
        db: 数据库会话
        issue: Issue 对象
        solution: 解决方案
        solution_process: 解决过程
        resolved_by: 解决人
    
    Returns:
        更新后的 Issue 对象
    """
    issue.solution = solution
    issue.solution_process = solution_process
    issue.resolved_by = resolved_by
    issue.resolved_at = datetime.now()
    issue.status = "已解决"
    issue.updated_at = datetime.now()
    
    db.commit()
    db.refresh(issue)
    return issue


def close_issue(db: Session, issue: Issue, closed_by: str, 
                closed_reason: Optional[str] = None) -> Issue:
    """
    关闭 Issue
    
    Args:
        db: 数据库会话
        issue: Issue 对象
        closed_by: 关闭人
        closed_reason: 关闭原因
    
    Returns:
        更新后的 Issue 对象
    """
    issue.closed_by = closed_by
    issue.closed_at = datetime.now()
    issue.status = "已关闭"
    issue.updated_at = datetime.now()
    
    # 如果有状态变更，记录关闭原因
    if closed_reason:
        issue.solution_process = (issue.solution_process or "") + f"\n关闭原因：{closed_reason}"
    
    db.commit()
    db.refresh(issue)
    return issue


def get_issue_statistics(db: Session, project_id: Optional[int] = None) -> dict:
    """
    获取 Issue 统计信息
    
    Args:
        db: 数据库会话
        project_id: 可选的项目 ID
    
    Returns:
        统计信息字典
    """
    query = db.query(Issue)
    if project_id is not None:
        query = query.filter(Issue.project_id == project_id)
    
    total = query.count()
    by_status = db.query(
        Issue.status, 
        db.query(Issue).filter(
            Issue.project_id == project_id if project_id else True
        ).filter(Issue.status == Issue.status).count()
    ).group_by(Issue.status).all()
    
    return {
        "total": total,
        "by_status": dict(by_status)
    }
