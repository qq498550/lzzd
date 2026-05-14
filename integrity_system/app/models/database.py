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
    settings.database_url, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DisciplineRecord(Base):
    """违纪信息表"""
    __tablename__ = "discipline_records"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    branch_company = Column(String(200))  # 分公司
    department = Column(String(200))
    position = Column(String(200))
    processing_org = Column(String(200))  # 处理机构
    accountability_type = Column(String(200))  # 问责情况
    accountability_date = Column(Date)  # 问责时间
    has_influence_period = Column(Boolean, default=True)  # 有无影响期
    influence_end_date = Column(Date)  # 影响期截止日期
    reason = Column(Text)  # 事由
    remark = Column(Text, default="")  # 备注
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ViolationRecord(Base):
    """违规信息表"""
    __tablename__ = "violation_records"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    branch_company = Column(String(200))  # 分公司
    department = Column(String(200))
    position = Column(String(200))
    processing_org = Column(String(200))  # 处理机构
    violation_type = Column(String(200))  # 问责类型
    violation_date = Column(Date)  # 问责时间
    has_influence_period = Column(Boolean, default=True)  # 有无影响期
    influence_end_date = Column(Date)  # 影响期截止日期
    reason = Column(Text)  # 事由
    remark = Column(Text, default="")  # 备注
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PetitionReport(Base):
    """信访举报表"""
    __tablename__ = "petition_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    branch_company = Column(String(200))  # 分公司
    department = Column(String(200))  # 部门
    report_date = Column(Date)
    report_content = Column(Text)
    verification_result = Column(String(200))  # 核查结果
    organization_adoption = Column(Boolean)  # 组织是否采信
    has_influence_period = Column(Boolean, default=False)  # 有无影响期
    influence_end_date = Column(Date)  # 影响期截止日期
    remark = Column(Text, default="")  # 备注
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


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(50))  # 模块：discipline/violation/petition/template
    action = Column(String(20))  # 操作：create/update/delete
    record_id = Column(Integer)  # 操作记录的ID
    record_name = Column(String(100))  # 操作记录的主要内容（如姓名）
    description = Column(Text)  # 操作描述
    operator = Column(String(100))  # 操作人
    created_at = Column(DateTime, default=datetime.now)


def init_db():
    """初始化数据库表"""
    # 首先创建所有表
    Base.metadata.create_all(bind=engine)
    # 然后检查并更新表结构，确保新字段存在
    _upgrade_table_structure()


def _upgrade_table_structure():
    """检查并更新数据库表结构，确保所有新字段存在"""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    
    # 需要检查的表和字段
    tables_to_check = {
        'discipline_records': ['branch_company'],
        'violation_records': ['branch_company'],
        'petition_reports': ['branch_company', 'department']
    }
    
    # 需要重命名的字段（status -> remark）
    tables_to_rename = {
        'discipline_records': ('status', 'remark'),
        'violation_records': ('status', 'remark'),
        'petition_reports': ('status', 'remark')
    }
    
    with engine.connect() as conn:
        # 添加新字段
        for table_name, columns_to_add in tables_to_check.items():
            try:
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                
                for column_to_add in columns_to_add:
                    if column_to_add not in existing_columns:
                        print(f"[DB] 为表 {table_name} 添加缺失的列: {column_to_add}")
                        try:
                            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_to_add} VARCHAR(200)"))
                            conn.commit()
                            print(f"[DB] 成功添加列 {table_name}.{column_to_add}")
                        except Exception as e:
                            print(f"[DB] 添加列 {table_name}.{column_to_add} 时出错: {e}")
                            conn.rollback()
            except Exception as e:
                print(f"[DB] 检查表 {table_name} 结构时出错: {e}")
        
        # 处理 status -> remark 迁移
        for table_name, (old_col, new_col) in tables_to_rename.items():
            try:
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                
                # 如果有 status 字段且没有 remark 字段，则迁移数据
                if old_col in existing_columns and new_col not in existing_columns:
                    print(f"[DB] 迁移表 {table_name} 的 {old_col} -> {new_col}")
                    try:
                        # 添加 remark 列
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {new_col} TEXT"))
                        # 复制 status 数据到 remark
                        conn.execute(text(f"UPDATE {table_name} SET {new_col} = {old_col}"))
                        conn.commit()
                        print(f"[DB] 成功迁移 {table_name}.{old_col} -> {new_col}")
                    except Exception as e:
                        print(f"[DB] 迁移 {table_name}.{old_col} 时出错: {e}")
                        conn.rollback()
                # 如果直接有 remark 字段
                elif new_col in existing_columns:
                    print(f"[DB] 表 {table_name} 已有 {new_col} 字段")
            except Exception as e:
                print(f"[DB] 检查表 {table_name} 迁移时出错: {e}")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
