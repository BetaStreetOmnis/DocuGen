import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMConfig:
    """LLM配置管理类，用于从环境变量中读取配置"""
    
    @staticmethod
    def get_local_model_config() -> Dict[str, Any]:
        """获取本地模型配置
        
        Returns:
            包含本地模型配置的字典
        """
        return {
            "base_url": os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:8000"),
            "api_key": os.getenv("LOCAL_LLM_API_KEY", None),
            "default_model": os.getenv("LOCAL_LLM_DEFAULT_MODEL", "deepseek-coder"),
            "default_temperature": float(os.getenv("LOCAL_LLM_DEFAULT_TEMPERATURE", "0.7")),
            "default_max_tokens": int(os.getenv("LOCAL_LLM_DEFAULT_MAX_TOKENS", "1000")),
        }
    
    @staticmethod
    def get_third_party_model_config() -> Dict[str, Any]:
        """获取第三方模型配置
        
        Returns:
            包含第三方模型配置的字典
        """
        return {
            "base_url": os.getenv("THIRD_PARTY_LLM_BASE_URL"),
            "api_key": os.getenv("THIRD_PARTY_LLM_API_KEY"),
            "default_model": os.getenv("THIRD_PARTY_LLM_DEFAULT_MODEL", "gpt-3.5-turbo"),
            "default_temperature": float(os.getenv("THIRD_PARTY_LLM_DEFAULT_TEMPERATURE", "0.7")),
            "default_max_tokens": int(os.getenv("THIRD_PARTY_LLM_DEFAULT_MAX_TOKENS", "1000")),
            "organization_id": os.getenv("THIRD_PARTY_LLM_ORGANIZATION_ID", None),
        }
    
    @staticmethod
    def get_model_type() -> str:
        """获取默认使用的模型类型
        
        Returns:
            模型类型："local"或"third_party"
        """
        return os.getenv("DEFAULT_LLM_TYPE", "local") 