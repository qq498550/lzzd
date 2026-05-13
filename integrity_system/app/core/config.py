"""
核心配置模块

使用 Pydantic 进行配置管理，支持环境变量覆盖
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类
    
    Attributes:
        app_name: 应用名称
        app_version: 应用版本
        app_description: 应用描述
        debug: 调试模式开关
        host: 服务监听地址
        port: 服务监听端口
        database_url: 数据库连接 URL
        log_level: 日志级别
    """
    
    # 应用基础配置
    app_name: str = "廉政意见智答系统"
    app_version: str = "1.0.0"
    app_description: str = "基于规则引擎的廉政意见智能答复系统"
    debug: bool = True
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    database_url: str = "sqlite:///./data/integrity.db"
    
    # 路径配置
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir: str = os.path.join(base_dir, "data")
    static_dir: str = os.path.join(base_dir, "static")
    templates_dir: str = os.path.join(base_dir, "templates")
    
    # 日志配置
    log_level: str = "INFO"
    
    # 安全配置
    admin_username: str = "admin"
    admin_password: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例实例
    
    Returns:
        Settings: 配置对象实例
    """
    return Settings()


# 向后兼容的别名
settings = get_settings()
