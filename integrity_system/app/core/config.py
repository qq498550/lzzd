"""
核心配置模块

使用 Pydantic 进行配置管理，支持环境变量覆盖
"""
import os
import sys
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


def get_base_dir():
    """获取应用基础目录，支持 PyInstaller 打包"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_DIR = get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")

# 确保 data 目录存在
os.makedirs(DATA_DIR, exist_ok=True)


def get_database_url():
    """获取数据库URL"""
    db_path = os.path.join(DATA_DIR, "integrity.db")
    return f"sqlite:///{db_path}"


def get_env_file_path():
    """获取 .env 文件路径"""
    return os.path.join(BASE_DIR, ".env")


def save_env_config(key: str, value: str):
    """保存配置到 .env 文件"""
    env_file = get_env_file_path()

    config_lines = []
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            config_lines = f.readlines()

    found = False
    new_lines = []
    for line in config_lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}\n")

    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # 清除 settings 缓存
    get_settings.cache_clear()


class Settings(BaseSettings):
    """应用配置类"""

    app_name: str = "廉政意见智答系统"
    app_version: str = "1.0.0"
    app_description: str = "基于规则引擎的廉政意见智能答复系统"
    debug: bool = True

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = get_database_url()

    base_dir: str = BASE_DIR
    data_dir: str = DATA_DIR
    static_dir: str = os.path.join(BASE_DIR, "static")
    templates_dir: str = os.path.join(BASE_DIR, "templates")

    log_level: str = "INFO"

    admin_username: str = "admin"
    admin_password: str = "admin123"

    class Config:
        env_file = get_env_file_path()
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例实例"""
    return Settings()


settings = get_settings()
