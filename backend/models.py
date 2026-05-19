"""
数据库模型定义
AutoCraft 流程执行系统 - 数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class ProjectProfile(Base):
    """项目档案表 - 存储项目模板和实例的基本信息"""
    __tablename__ = "project_profiles"

    profile_id = Column(String(50), primary_key=True, comment="项目档案 ID")
    profile_type = Column(String(20), nullable=False, comment="档案类型：template=模板，instance=实例")
    profile_name = Column(String(100), nullable=False, comment="项目名称")
    project_type = Column(String(50), nullable=True, comment="项目类型")
    description = Column(Text, nullable=True, comment="项目描述")
    tech_stack = Column(String(200), nullable=True, comment="技术栈")
    root_path = Column(String(500), nullable=True, comment="项目根路径")
    status = Column(String(20), nullable=False, default='active', comment="状态")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    phases = relationship("ProjectPhase", back_populates="profile", cascade="all, delete-orphan")
    work_plans = relationship("WorkPlan", back_populates="profile", cascade="all, delete-orphan")


class ProjectPhase(Base):
    """项目阶段表 - 定义项目的各个阶段"""
    __tablename__ = "project_phases"

    phase_record_id = Column(String(50), primary_key=True, comment="阶段记录 ID")
    profile_id = Column(String(50), ForeignKey("project_profiles.profile_id"), nullable=False, comment="项目档案 ID")
    phase_id = Column(String(50), nullable=False, comment="阶段 ID")
    phase_name = Column(String(100), nullable=False, comment="阶段名称")
    phase_order = Column(Integer, nullable=False, comment="阶段顺序")
    status = Column(String(20), nullable=False, default='pending', comment="状态")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    profile = relationship("ProjectProfile", back_populates="phases")
    work_plans = relationship("WorkPlan", back_populates="phase", cascade="all, delete-orphan")


class WorkPlan(Base):
    """工作计划表 - 具体的工作计划"""
    __tablename__ = "work_plans"

    plan_id = Column(String(50), primary_key=True, comment="计划 ID")
    profile_id = Column(String(50), ForeignKey("project_profiles.profile_id"), nullable=False, comment="项目档案 ID")
    phase_record_id = Column(String(50), ForeignKey("project_phases.phase_record_id"), nullable=True, comment="阶段记录 ID")
    plan_name = Column(String(100), nullable=False, comment="计划名称")
    description = Column(Text, nullable=True, comment="计划描述")
    status = Column(String(20), nullable=False, default='pending', comment="状态")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    profile = relationship("ProjectProfile", back_populates="work_plans")
    phase = relationship("ProjectPhase", back_populates="work_plans")
    tasks = relationship("Task", back_populates="work_plan", cascade="all, delete-orphan")


class AgentProfile(Base):
    """Agent 档案表 - 定义 Agent 的能力和配置"""
    __tablename__ = "agent_profiles"

    agent_id = Column(String(50), primary_key=True, comment="Agent ID")
    name = Column(String(100), nullable=False, comment="Agent 名称")
    position = Column(String(100), nullable=False, comment="职位/角色")
    responsibilities = Column(Text, nullable=True, comment="职责列表（JSON 数组）")
    capabilities = Column(Text, nullable=True, comment="能力列表（JSON 数组）")
    skills = Column(Text, nullable=True, comment="技能（JSON）")
    prompt_template = Column(Text, nullable=True, comment="提示词模板")
    model = Column(String(50), nullable=False, comment="使用的模型")
    timeout_seconds = Column(Integer, nullable=False, default=300, comment="超时时间（秒）")
    max_retries = Column(Integer, nullable=False, default=2, comment="最大重试次数")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    tasks = relationship("Task", back_populates="agent")


class Task(Base):
    """任务模型 - 原有的任务表，新增流程相关字段"""
    __tablename__ = "tasks"

    # 原有字段
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="自增 ID")
    task_no = Column(String(20), unique=True, index=True, nullable=False, comment="任务单号")
    task_name = Column(String(200), nullable=False, comment="任务名称")
    plan_date = Column(DateTime, nullable=True, comment="计划日期")
    plan_complete_time = Column(DateTime, nullable=True, comment="计划完成时间")
    executor = Column(String(100), nullable=True, comment="执行人")
    status = Column(String(20), nullable=False, default="新建", comment="状态")
    priority = Column(String(10), nullable=False, default="中", comment="优先级")
    execution_steps = Column(Text, nullable=True, comment="执行步骤")
    expected_result = Column(Text, nullable=True, comment="预期结果")
    execution_log = Column(Text, nullable=True, comment="执行日志")
    output_result = Column(Text, nullable=True, comment="输出结果")
    execution_date = Column(DateTime, nullable=True, comment="执行日期")
    verification_result = Column(String(20), nullable=False, default="待验证", comment="验证结论")
    verifier = Column(String(100), nullable=True, comment="验证人")
    verification_time = Column(DateTime, nullable=True, comment="验证时间")
    verification_log = Column(Text, nullable=True, comment="验证日志")
    exec_start_time = Column(DateTime, nullable=True, comment="执行开始时间")
    exec_estimated_complete = Column(DateTime, nullable=True, comment="预计执行完成时间")
    exec_complete_time = Column(DateTime, nullable=True, comment="执行完成时间")
    verify_start_time = Column(DateTime, nullable=True, comment="验证开始时间")
    verify_estimated_complete = Column(DateTime, nullable=True, comment="预计验证完成时间")
    verify_complete_time = Column(DateTime, nullable=True, comment="验证完成时间")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 新增字段 - 流程相关
    task_type = Column(String(50), nullable=True, comment="任务类型")
    plan_id = Column(String(50), ForeignKey("work_plans.plan_id"), nullable=True, comment="工作计划 ID")
    phase_record_id = Column(String(50), ForeignKey("project_phases.phase_record_id"), nullable=True, comment="阶段记录 ID")
    agent_id = Column(String(50), ForeignKey("agent_profiles.agent_id"), nullable=True, comment="Agent ID")
    locked_by = Column(String(50), nullable=True, comment="锁定者")
    locked_at = Column(DateTime, nullable=True, comment="锁定时间")
    input_data = Column(Text, nullable=True, comment="输入数据(JSON)")
    extra_data = Column(Text, nullable=True, comment="扩展数据(JSON)")

    # 关系定义
    work_plan = relationship("WorkPlan", back_populates="tasks")
    agent = relationship("AgentProfile", back_populates="tasks")
