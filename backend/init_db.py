"""
数据库初始化脚本

创建示例项目、阶段、计划和任务数据
"""

from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Task
from models.task_v2 import TaskV2

# 创建表
Base.metadata.create_all(bind=engine)


def init_sample_data():
    """初始化示例数据"""
    db: Session = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing = db.query(Task).first()
        if existing:
            print("数据库已有数据，跳过初始化")
            return
        
        # 创建示例任务
        sample_task = Task(
            task_no="SAMPLE-001",
            task_name="示例任务",
            task_type="开发",
            status="pending",
            priority="medium",
            execution_steps="1. 分析需求\n2. 设计方案\n3. 编码实现",
            expected_result="完成功能开发",
            verification_result="待验证"
        )
        db.add(sample_task)
        db.commit()
        print("示例数据创建成功")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("开始初始化数据库...")
    init_sample_data()
    print("数据库初始化完成")
