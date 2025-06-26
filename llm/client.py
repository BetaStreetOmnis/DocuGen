from typing import List, Dict, Any, Optional, Generator, Union
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(sys.path)
from llm.factory import LLMFactory
from llm.local_model import LocalLLMClient
from llm.third_party_model import ThirdPartyLLMClient
from llm.config import LLMConfig

class LLMClient:
    """
    统一的LLM调用接口类，无论是本地模型还是第三方模型都使用相同的接口
    """
    
    def __init__(self, model_type: Optional[str] = "third_party"):
        """
        初始化LLM客户端
        
        Args:
            model_type: 模型类型，"local"或"third_party"，默认使用环境变量中配置的类型
        """
        self.model_type = model_type or LLMConfig.get_model_type()
        self.client = LLMFactory.create_client(self.model_type)
        
        # 根据模型类型获取默认配置
        if self.model_type == "local":
            config = LLMConfig.get_local_model_config()
        else:
            config = LLMConfig.get_third_party_model_config()
            
        self.default_model = config["default_model"]
        self.default_temperature = config["default_temperature"]
        self.default_max_tokens = config["default_max_tokens"]
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: Optional[str] = None,
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None,
             stream: bool = False) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        统一的模型调用接口
        
        Args:
            messages: 消息列表，格式与ChatGPT API相同
            model: 模型名称，如不指定则使用配置的默认值
            temperature: 温度参数，如不指定则使用配置的默认值
            max_tokens: 最大生成token数，如不指定则使用配置的默认值
            stream: 是否使用流式响应
            
        Returns:
            如果stream=False，返回模型响应字典
            如果stream=True，返回响应生成器
        """
        # 使用传入的参数或默认值
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        if stream:
            return self.client.stream_chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            return self.client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
    
    def stream_chat(self, 
                   messages: List[Dict[str, str]], 
                   model: Optional[str] = None,
                   temperature: Optional[float] = None,
                   max_tokens: Optional[int] = None) -> Generator[Dict[str, Any], None, None]:
        """
        统一的流式模型调用接口
        
        Args:
            messages: 消息列表，格式与ChatGPT API相同
            model: 模型名称，如不指定则使用配置的默认值
            temperature: 温度参数，如不指定则使用配置的默认值
            max_tokens: 最大生成token数，如不指定则使用配置的默认值
            
        Returns:
            响应生成器
        """
        return self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
    
    def switch_model_type(self, model_type: str) -> None:
        """
        切换模型类型
        
        Args:
            model_type: 要切换的模型类型，"local"或"third_party"
        """
        if model_type not in ["local", "third_party"]:
            raise ValueError(f"不支持的模型类型: {model_type}，请使用'local'或'third_party'")
            
        if model_type != self.model_type:
            self.model_type = model_type
            self.client = LLMFactory.create_client(self.model_type)
            
            # 更新默认配置
            if self.model_type == "local":
                config = LLMConfig.get_local_model_config()
            else:
                config = LLMConfig.get_third_party_model_config()
                
            self.default_model = config["default_model"]
            self.default_temperature = config["default_temperature"]
            self.default_max_tokens = config["default_max_tokens"]



# if __name__ == "__main__":
#     client = LLMClient(model_type="third_party")
#     response = client.chat(messages=[{"role": "user", "content": "你好"}])
#     print(response)
