"""
LLM工厂模块
统一管理不同LLM提供商的实例创建
"""
from langchain_openai import ChatOpenAI
from ..config import config


def create_llm(temperature: float = 0.1):
    """
    根据配置创建LLM实例
    
    Args:
        temperature: 温度参数
        
    Returns:
        配置好的LLM实例
    """
    if config.LLM_PROVIDER.lower() == "deepseek":
        # 使用DeepSeek API（兼容OpenAI格式）
        return ChatOpenAI(
            model=config.DEEPSEEK_MODEL,
            temperature=temperature,
            api_key=config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"  # DeepSeek API端点
        )
    else:
        # 默认使用OpenAI
        return ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=temperature,
            api_key=config.OPENAI_API_KEY
        )