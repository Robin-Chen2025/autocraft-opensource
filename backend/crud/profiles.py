"""
项目档案 CRUD 操作模块
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models import ProjectProfile, ProjectPhase
from schemas import ProfileCreate, ProfileUpdate


def get_profiles(
    db: Session,
    profile_type: Optional[str] = None,
    status: Optional[str] = None,
    name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    获取项目档案列表（支持筛选和分页）
    
    Args:
        db: 数据库会话
        profile_type: 档案类型筛选（template/instance）
        status: 状态筛选
        name: 项目名称模糊搜索
        start_date: 创建时间起始
        end_date: 创建时间结束
        skip: 跳过记录数
        limit: 返回记录数限制
        
    Returns:
        tuple: (总记录数，档案列表)
    """
    # 构建基础查询
    query = db.query(ProjectProfile)
    
    # 添加筛选条件
    filters = []
    
    if profile_type:
        filters.append(ProjectProfile.profile_type == profile_type)
    
    if status:
        filters.append(ProjectProfile.status == status)
    
    if name:
        filters.append(ProjectProfile.profile_name.like(f"%{name}%"))
    
    if start_date:
        filters.append(ProjectProfile.created_at >= start_date)
    
    if end_date:
        filters.append(ProjectProfile.created_at <= end_date)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    profiles = query.order_by(ProjectProfile.created_at.desc()).offset(skip).limit(limit).all()
    
    return total, profiles


def get_profile(db: Session, profile_id: str):
    """
    获取单个项目档案详情
    
    Args:
        db: 数据库会话
        profile_id: 项目档案 ID
        
    Returns:
        ProjectProfile or None
    """
    return db.query(ProjectProfile).filter(
        ProjectProfile.profile_id == profile_id
    ).first()


def create_profile(db: Session, profile_data: ProfileCreate):
    """
    创建项目档案（支持从模板复制阶段）
    
    Args:
        db: 数据库会话
        profile_data: 档案创建数据
        
    Returns:
        ProjectProfile: 创建的档案对象
    """
    import uuid
    
    # 生成或验证 profile_id
    if profile_data.profile_id:
        profile_id = profile_data.profile_id
    else:
        profile_id = f"profile_{uuid.uuid4().hex[:16]}"
    
    # 创建档案
    db_profile = ProjectProfile(
        profile_id=profile_id,
        profile_type=profile_data.profile_type,
        profile_name=profile_data.profile_name,
        project_type=profile_data.project_type,
        description=profile_data.description,
        tech_stack=profile_data.tech_stack,
        root_path=profile_data.root_path,
        status=profile_data.status
    )
    
    db.add(db_profile)
    
    # 如果从模板复制，复制阶段
    if profile_data.template_profile_id:
        template_profile = get_profile(db, profile_data.template_profile_id)
        if template_profile:
            # 复制阶段
            for template_phase in template_profile.phases:
                new_phase = ProjectPhase(
                    phase_record_id=f"phase_{uuid.uuid4().hex[:16]}",
                    profile_id=profile_id,
                    phase_id=template_phase.phase_id,
                    phase_name=template_phase.phase_name,
                    phase_order=template_phase.phase_order,
                    status='pending'
                )
                db.add(new_phase)
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile


def update_profile(db: Session, profile_id: str, profile_data: ProfileUpdate):
    """
    更新项目档案
    
    Args:
        db: 数据库会话
        profile_id: 项目档案 ID
        profile_data: 档案更新数据
        
    Returns:
        ProjectProfile or None
    """
    db_profile = get_profile(db, profile_id)
    if not db_profile:
        return None
    
    # 只更新提供的字段
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db.commit()
    db.refresh(db_profile)
    
    return db_profile


def delete_profile(db: Session, profile_id: str):
    """
    删除项目档案（级联删除相关阶段、计划）
    
    Args:
        db: 数据库会话
        profile_id: 项目档案 ID
        
    Returns:
        bool: 是否删除成功
    """
    db_profile = get_profile(db, profile_id)
    if not db_profile:
        return False
    
    db.delete(db_profile)
    db.commit()
    
    return True


def get_profile_phases(db: Session, profile_id: str):
    """
    获取项目的阶段列表
    
    Args:
        db: 数据库会话
        profile_id: 项目档案 ID
        
    Returns:
        list[ProjectPhase]: 阶段列表
    """
    return db.query(ProjectPhase).filter(
        ProjectPhase.profile_id == profile_id
    ).order_by(ProjectPhase.phase_order).all()


def create_phase(db: Session, profile_id: str, phase_data) -> str:
    """创建项目阶段"""
    import uuid
    
    # 使用 profile_id 的前8位 + phase_id 生成唯一ID
    short_profile = profile_id.replace("profile_", "")[:8]
    phase_record_id = f"{short_profile}-{phase_data.phase_id}"
    
    phase = ProjectPhase(
        phase_record_id=phase_record_id,
        profile_id=profile_id,
        phase_id=phase_data.phase_id,
        phase_name=phase_data.phase_name,
        phase_order=phase_data.phase_order,
        status=phase_data.status
    )
    db.add(phase)
    db.commit()
    db.refresh(phase)
    return phase.phase_record_id


def get_phase(db: Session, phase_record_id: str):
    """获取单个阶段"""
    return db.query(ProjectPhase).filter(
        ProjectPhase.phase_record_id == phase_record_id
    ).first()


def update_phase(db: Session, phase_record_id: str, update_data: dict):
    """更新阶段"""
    phase = db.query(ProjectPhase).filter(
        ProjectPhase.phase_record_id == phase_record_id
    ).first()
    if not phase:
        return None
    
    for key, value in update_data.items():
        setattr(phase, key, value)
    phase.updated_at = datetime.now()
    db.commit()
    db.refresh(phase)
    return phase


def delete_phase(db: Session, phase_record_id: str):
    """删除阶段"""
    phase = db.query(ProjectPhase).filter(
        ProjectPhase.phase_record_id == phase_record_id
    ).first()
    if not phase:
        return False
    
    # 删除关联的计划和任务
    from models import WorkPlan, Task
    plans = db.query(WorkPlan).filter(WorkPlan.phase_record_id == phase_record_id).all()
    for plan in plans:
        tasks = db.query(Task).filter(Task.plan_id == plan.plan_id).all()
        for task in tasks:
            db.delete(task)
        db.delete(plan)
    
    db.delete(phase)
    db.commit()
    return True
