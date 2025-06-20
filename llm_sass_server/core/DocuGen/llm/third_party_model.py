import os
import json
import requests
from typing import List, Dict, Any, Optional, Generator

class ThirdPartyLLMClient:
    """
    第三方大语言模型客户端，用于调用第三方API接口，如OpenAI、Azure OpenAI等
    """
    
    def __init__(self, base_url: str, api_key: str, organization_id: Optional[str] = None):
        """
        初始化第三方模型客户端
        
        Args:
            base_url: API服务的基础URL
            api_key: API密钥
            organization_id: 组织ID（某些服务需要）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        if organization_id:
            self.headers["OpenAI-Organization"] = organization_id
    
    def chat_completion(self, 
                        messages: List[Dict[str, str]], 
                        model: str = "gpt-3.5-turbo", 
                        temperature: float = 0.7,
                        max_tokens: int = 1000,
                        stream: bool = False) -> Dict[str, Any]:
        """
        发送聊天请求到第三方模型API
        
        Args:
            messages: 消息列表，格式与ChatGPT API相同
            model: 模型名称
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            stream: 是否使用流式响应
            
        Returns:
            模型响应
        """
        endpoint = f"{self.base_url}"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"请求失败: {str(e)}"}
    
    def stream_chat_completion(self, 
                              messages: List[Dict[str, str]], 
                              model: str = "gpt-3.5-turbo",
                              temperature: float = 0.7,
                              max_tokens: int = 1000) -> Generator[Dict[str, Any], None, None]:
        """
        流式调用第三方模型
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            
        Returns:
            生成器，逐步返回模型响应
        """
        endpoint = f"{self.base_url}"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            yield {"error": f"解析响应失败: {data}"}
        except requests.exceptions.RequestException as e:
            yield {"error": f"流式请求失败: {str(e)}"} 