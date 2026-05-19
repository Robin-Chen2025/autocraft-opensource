"""
层级状态更新逻辑

当任务状态变更时，自动向上更新计划、阶段、项目的状态

状态更新规则：
1. 任务全部完成 → 计划完成
2. 计划全部完成 → 阶段完成
3. 阶段全部完成 → 项目完成
"""
from datetime import datetime
from sqlalchemy.orm import Session
from models import Task, WorkPlan, ProjectPhase, ProjectProfile


def update_plan_status(db: Session, plan_id: str) -> str:
    """更新工作计划状态"""
    plan = db.query(WorkPlan).filter(WorkPlan.plan_id == plan_id).first()
    if not plan:
        return None
    
    # 获取该计划的所有任务
    tasks = db.query(Task).filter(Task.plan_id == plan_id).all()
    if not tasks:
        return plan.status
    
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status in ['completed', '已完成'])
    
    # 更新规则
    if completed == total:
        new_status = 'completed'
    elif completed > 0:
        new_status = 'in_progress'
    else:
        new_status = 'pending'
    
    if plan.status != new_status:
        plan.status = new_status
        plan.updated_at = datetime.now()
        db.commit()
    
    # 级联更新阶段状态
    if plan.phase_record_id:
        update_phase_status(db, plan.phase_record_id)
    
    return new_status


def update_phase_status(db: Session, phase_record_id: str) -> str:
    """更新阶段状态"""
    phase = db.query(ProjectPhase).filter(
        ProjectPhase.phase_record_id == phase_record_id
    ).first()
    if not phase:
        return None
    
    # 获取该阶段下的所有计划
    plans = db.query(WorkPlan).filter(
        WorkPlan.phase_record_id == phase_record_id
    ).all()
    
    if not plans:
        return phase.status
    
    total = len(plans)
    completed = sum(1 for p in plans if p.status in ['completed', '已完成'])
    in_progress = sum(1 for p in plans if p.status in ['in_progress', '进行中'])
    
    # 更新规则
    if completed == total:
        new_status = 'completed'
    elif completed > 0 or in_progress > 0:
        new_status = 'in_progress'
    else:
        new_status = 'pending'
    
    if phase.status != new_status:
        phase.status = new_status
        phase.updated_at = datetime.now()
        db.commit()
    
    # 级联更新项目状态
    if phase.profile_id:
        update_profile_status(db, phase.profile_id)
    
    return new_status


def update_profile_status(db: Session, profile_id: str) -> str:
    """更新项目状态"""
    profile = db.query(ProjectProfile).filter(
        ProjectProfile.profile_id == profile_id
    ).first()
    if not profile:
        return None
    
    # 获取该项目下的所有阶段
    phases = db.query(ProjectPhase).filter(
        ProjectPhase.profile_id == profile_id
    ).all()
    
    if not phases:
        return profile.status
    
    total = len(phases)
    completed = sum(1 for p in phases if p.status in ['completed', '已完成'])
    in_progress = sum(1 for p in phases if p.status in ['in_progress', '进行中'])
    
    # 更新规则
    if completed == total:
        new_status = 'completed'
    elif completed > 0 or in_progress > 0:
        new_status = 'in_progress'
    else:
        new_status = 'pending'
    
    if profile.status != new_status:
        profile.status = new_status
        profile.updated_at = datetime.now()
        db.commit()
    
    return new_status


def update_status_from_task(db: Session, task_no: str) -> dict:
    """
    从任务状态变更开始，级联更新上层状态
    
    返回各层更新后的状态
    """
    task = db.query(Task).filter(Task.task_no == task_no).first()
    if not task:
        return {}
    
    result = {'task_status': task.status}
    
    # 更新计划状态
    if task.plan_id:
        plan_status = update_plan_status(db, task.plan_id)
        result['plan_status'] = plan_status
    
    return result
