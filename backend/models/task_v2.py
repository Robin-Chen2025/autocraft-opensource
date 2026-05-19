"""
FlowTicket v2 任务模型
基于现有tasks表扩展，支持FlowTicket v2功能
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class TaskV2(Base):
    """FlowTicket v2 任务模型"""
    __tablename__ = "tasks_v2"
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="自增ID")
    task_no = Column(String(20), unique=True, index=True, nullable=False, comment="任务单号")
    task_name = Column(String(200), nullable=False, comment="任务名称")
    
    # FlowTicket v2 新增字段
    task_type = Column(String(50), nullable=True, comment="任务类型")
    plan_id = Column(String(50), nullable=True, comment="工作计划ID")
    
    # 状态字段（v2标准）
    status = Column(String(30), nullable=False, default="pending", comment="任务状态")
    
    # JSON字段
    input_data = Column(Text, nullable=True, comment="输入数据（JSON格式）")
    extra_data = Column(Text, nullable=True, comment="额外数据（JSON格式）")
    execution_log = Column(Text, nullable=True, comment="执行日志（JSON格式）")
    verification_log = Column(Text, nullable=True, comment="验证日志（JSON格式）")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 锁定字段
    locked_by = Column(String(50), nullable=True, comment="锁定者")
    locked_at = Column(DateTime, nullable=True, comment="锁定时间")
    
    def __repr__(self):
        return f"<TaskV2(id={self.id}, task_no='{self.task_no}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "id": self.id,
            "task_no": self.task_no,
            "task_name": self.task_name,
            "task_type": self.task_type,
            "plan_id": self.plan_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 处理JSON字段
        json_fields = ["input_data", "extra_data", "execution_log", "verification_log"]
        for field in json_fields:
            value = getattr(self, field)
            if value:
                try:
                    result[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[field] = value
            else:
                result[field] = None
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskV2':
        """从字典创建实例"""
        task = cls()
        
        # 基本字段
        task.task_no = data.get("task_no", "")
        task.task_name = data.get("task_name", "")
        task.task_type = data.get("task_type")
        task.plan_id = data.get("plan_id")
        task.status = data.get("status", "pending")
        
        # 处理JSON字段
        json_fields = ["input_data", "extra_data", "execution_log", "verification_log"]
        for field in json_fields:
            value = data.get(field)
            if value:
                if isinstance(value, (dict, list)):
                    setattr(task, field, json.dumps(value, ensure_ascii=False))
                else:
                    setattr(task, field, value)
        
        return task


class FlowTicketInstance(Base):
    """FlowTicket实例模型"""
    __tablename__ = "flowticket_instances"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="自增ID")
    flowticket_id = Column(String(100), unique=True, nullable=False, comment="FlowTicket实例ID")
    plan_id = Column(String(50), nullable=False, comment="工作计划ID")
    status = Column(String(20), nullable=False, default="running", comment="状态")
    current_task_id = Column(Integer, nullable=True, comment="当前任务ID")
    execution_log = Column(Text, nullable=True, comment="执行日志（JSON格式）")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def __repr__(self):
        return f"<FlowTicketInstance(id={self.id}, flowticket_id='{self.flowticket_id}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "id": self.id,
            "flowticket_id": self.flowticket_id,
            "plan_id": self.plan_id,
            "status": self.status,
            "current_task_id": self.current_task_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if self.execution_log:
            try:
                result["execution_log"] = json.loads(self.execution_log)
            except (json.JSONDecodeError, TypeError):
                result["execution_log"] = self.execution_log
        
        return result


class FlowTicketLog(Base):
    """FlowTicket日志模型"""
    __tablename__ = "flowticket_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="自增ID")
    flowticket_id = Column(String(100), nullable=False, comment="FlowTicket实例ID")
    task_id = Column(Integer, nullable=True, comment="任务ID")
    log_type = Column(String(50), nullable=False, comment="日志类型")
    content = Column(Text, nullable=False, comment="日志内容（JSON格式）")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    
    # 索引
    __table_args__ = (
        Index('idx_flowticket_logs_flowticket_id', 'flowticket_id'),
        Index('idx_flowticket_logs_task_id', 'task_id'),
        Index('idx_flowticket_logs_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<FlowTicketLog(id={self.id}, flowticket_id='{self.flowticket_id}', log_type='{self.log_type}')>"
