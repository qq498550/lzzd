"""
核心配置模块

使用 Pydantic 进行配置管理，密码哈希存储在数据库中
"""
import os
import sys
import hashlib
import uuid
import base64
from functools import lru_cache
from pydantic_settings import BaseSettings


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


def get_machine_id() -> str:
    """获取机器唯一标识"""
    # 使用机器名 + 用户名 + 随机UUID 生成
    machine_info = f"{os.environ.get('COMPUTERNAME', 'default')}-{os.environ.get('USERNAME', 'user')}-{uuid.getnode()}"
    return hashlib.sha256(machine_info.encode()).hexdigest()[:32]


def get_encryption_key() -> bytes:
    """获取加密密钥（基于机器ID）"""
    machine_id = get_machine_id()
    # 使用 PBKDF2 派生加密密钥
    key = hashlib.pbkdf2_hmac('sha256', machine_id.encode(), b'integrity_system_salt', 100000)
    return key


def hash_password(password: str) -> str:
    """密码哈希（带盐）"""
    salt = uuid.uuid4().hex
    hash_val = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${base64.b64encode(hash_val).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """验证密码"""
    try:
        if '$' not in stored_hash:
            # 兼容旧格式（简单SHA256）
            return hashlib.sha256(password.encode()).hexdigest() == stored_hash
        salt, encoded_hash = stored_hash.split('$')
        hash_val = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return base64.b64decode(encoded_hash) == hash_val
    except:
        return False


def get_default_admin_hash() -> str:
    """默认管理员密码哈希（admin123）"""
    return "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"


def get_admin_password_hash_from_db() -> str:
    """从数据库获取管理员密码哈希"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(get_database_url(), connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            from app.models.database import SystemConfig
            config = db.query(SystemConfig).filter(SystemConfig.config_key == "admin_password_hash").first()
            if config and config.config_value:
                return config.config_value
        finally:
            db.close()
    except:
        pass
    return get_default_admin_hash()


def save_admin_password_hash_to_db(password_hash: str):
    """保存管理员密码哈希到数据库"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.database import SystemConfig, Base
    
    engine = create_engine(get_database_url(), connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    
    # 确保表存在
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        config = db.query(SystemConfig).filter(SystemConfig.config_key == "admin_password_hash").first()
        if config:
            config.config_value = password_hash
        else:
            config = SystemConfig(config_key="admin_password_hash", config_value=password_hash)
            db.add(config)
        db.commit()
    finally:
        db.close()


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

    class Config:
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例实例"""
    return Settings()


settings = get_settings()


def get_admin_password_hash() -> str:
    """获取管理员密码哈希"""
    return get_admin_password_hash_from_db()
