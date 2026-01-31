"""
配置管理模块
"""
import os
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config(BaseModel):
    """应用配置类"""
    
    # LLM配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai 或 deepseek
    
    # 数据库配置
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 文件处理配置
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    SUPPORTED_FILE_TYPES: list = [
        ".txt", ".pdf", ".docx", ".json", ".csv", ".xml"
    ]
    
    # 工作流配置
    CHECKPOINTER_ENABLED: bool = os.getenv("CHECKPOINTER_ENABLED", "False").lower() == "true"

# 全局配置实例
config = Config()