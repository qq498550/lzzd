"""
核心配置模块
"""
import os
from typing import Optional


class Settings:
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "廉政意见智答系统"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于规则引擎的廉政意见智能答复系统"
    DEBUG: bool = True
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/integrity.db"
    
    # 路径配置
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "templates")
    
    # 日志配置
    LOG_LEVEL: str = "INFO"


settings = Settings()
