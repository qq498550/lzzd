"""
数据库模块 - 数据模型和会话管理
"""
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.core.config import settings

# 数据库引擎配置
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DisciplineRecord(Base):
    """违纪信息表"""
    __tablename__ = "discipline_records"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    department = Column(String(200))
    position = Column(String(200))
    processing_org = Column(String(200))  # 处理机构
    accountability_type = Column(String(200))  # 问责情况
    accountability_date = Column(Date)  # 问责时间
    has_influence_period = Column(Boolean, default=True)  # 有无影响期
    influence_end_date = Column(Date)  # 影响期截止日期
    reason = Column(Text)  # 事由
    status = Column(String(50), default="completed")  # 状态：completed/processing
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ViolationRecord(Base):
    """违规信息表"""
    __tablename__ = "violation_records"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    department = Column(String(200))
    position = Column(String(200))
    processing_org = Column(String(200))  # 处理机构
    violation_type = Column(String(200))  # 问责类型
    violation_date = Column(Date)  # 问责时间
    has_influence_period = Column(Boolean, default=True)  # 有无影响期
    influence_end_date = Column(Date)  # 影响期截止日期
    reason = Column(Text)  # 事由
    status = Column(String(50), default="completed")  # 状态：completed/processing
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PetitionReport(Base):
    """信访举报表"""
    __tablename__ = "petition_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    report_date = Column(Date)
    report_content = Column(Text)
    verification_result = Column(String(200))  # 核查结果
    organization_adoption = Column(Boolean)  # 组织是否采信
    status = Column(String(50), default="processing")  # processing/completed/closed
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AnswerTemplate(Base):
    """标准答复模板表"""
    __tablename__ = "answer_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_code = Column(String(20), unique=True, index=True)  # 模板编号 T1-T8
    template_name = Column(String(100))  # 模板名称
    scenario_type = Column(String(100))  # 适用场景
    matter_type = Column(String(100))  # 事项类型：干部选拔任用/表彰奖励等
    template_content = Column(Text)  # 模板内容（含变量占位符）
    priority = Column(Integer, default=0)  # 优先级
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class QueryLog(Base):
    """查询日志表"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query_name = Column(String(100))
    matter_type = Column(String(100))
    result_template = Column(String(20))
    conclusion = Column(String(200))
    query_time = Column(DateTime, default=datetime.now)
    operator = Column(String(100))


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
