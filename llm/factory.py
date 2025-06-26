from typing import Union, Optional

from .config import LLMConfig
from .local_model import LocalLLMClient
from .third_party_model import ThirdPartyLLMClient

class LLMFactory:
    """
    LLM工厂类，用于创建各种类型的LLM客户端
    """
    
    @staticmethod
    def create_client(model_type: Optional[str] = None) -> Union[LocalLLMClient, ThirdPartyLLMClient]:
        """
        根据配置创建LLM客户端
        
        Args:
            model_type: 模型类型，可以是"local"或"third_party"，如果为None则使用环境变量中的默认设置
            
        Returns:
            LLM客户端实例
        """
        if model_type is None:
            model_type = LLMConfig.get_model_type()
            
        if model_type == "local":
            config = LLMConfig.get_local_model_config()
            return LocalLLMClient(
                base_url=config["base_url"],
                api_key=config["api_key"]
            )
        elif model_type == "third_party":
            config = LLMConfig.get_third_party_model_config()
            
            # 确保必要的配置项存在
            if not config["base_url"] or not config["api_key"]:
                raise ValueError("第三方模型配置不完整，请检查环境变量设置")
                
            return ThirdPartyLLMClient(
                base_url=config["base_url"],
                api_key=config["api_key"],
                organization_id=config["organization_id"]
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}，请使用'local'或'third_party'") 