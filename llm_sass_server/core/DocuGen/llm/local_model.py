import os
import json
import requests
from typing import List, Dict, Any, Optional, Generator

class LocalLLMClient:
    """
    本地大语言模型客户端，用于调用符合ChatGPT格式接口的本地模型，如DeepSeek等
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        初始化本地模型客户端
        
        Args:
            base_url: 本地模型服务的基础URL
            api_key: API密钥（如果本地服务需要）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def chat_completion(self, 
                        messages: List[Dict[str, str]], 
                        model: str = "deepseek-coder", 
                        temperature: float = 0.7,
                        max_tokens: int = 1000,
                        stream: bool = False) -> Dict[str, Any]:
        """
        发送聊天请求到本地模型
        
        Args:
            messages: 消息列表，格式与ChatGPT API相同
            model: 模型名称
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            stream: 是否使用流式响应
            
        Returns:
            模型响应，格式与ChatGPT API相同
        """
        endpoint = f"{self.base_url}/v1/chat/completions"
        
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
                              model: str = "deepseek-coder",
                              temperature: float = 0.7,
                              max_tokens: int = 1000) -> Generator[Dict[str, Any], None, None]:
        """
        流式调用本地模型
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            
        Returns:
            生成器，逐步返回模型响应
        """
        endpoint = f"{self.base_url}/v1/chat/completions"
        
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
