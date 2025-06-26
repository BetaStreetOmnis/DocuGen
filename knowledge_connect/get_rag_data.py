import os
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

def get_knowledge_bases() -> List[Dict[str, Any]]:
    """
    获取所有可用的知识库列表
    
    Returns:
        List[Dict[str, Any]]: 知识库列表，每个知识库包含名称和其他信息
    """
    # 加载环境变量
    load_dotenv()
    
    # 从环境变量获取host配置
    host = os.getenv("RAG_HOST", "127.0.0.1:8024")
    
    url = f"http://{host}/kb/list"
    
    print(f"[DEBUG] 正在请求知识库列表: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"[DEBUG] 响应状态码: {response.status_code}")
        response.raise_for_status()  # 检查响应状态
        result = response.json()
        print(f"[DEBUG] 响应内容: {result}")
        if result.get("status") == "success":
            return result.get("data", [])
        return []
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 获取知识库列表失败: {str(e)}")
        print(f"[ERROR] 请求URL: {url}")
        print(f"[WARNING] RAG服务不可用，返回空列表")
        
        # 返回空列表而不是抛出异常，让应用继续运行
        # 用户仍然可以使用自定义知识库功能
        return []

def get_rag_data(kb_name: str, query: str, top_k: int = 5) -> dict:
    """
    从RAG系统获取知识库数据
    
    Args:
        kb_name: 知识库名称
        query: 查询内容
        top_k: 返回的最大结果数量
        
    Returns:
        dict: 返回的响应数据，格式如下:
        {
            "status": "success",
            "data": [
                {
                    "content": str,  # 文本内容
                    "score": float,  # 相似度分数
                    "metadata": {    # 元数据信息
                        "char_count": int,
                        "sentence_count": int,
                        "chunk_id": str,
                        "file_name": str,
                        "file_path": str,
                        "file_type": str,
                        "document_id": str,
                        "chunk_index": int,
                        "total_chunks": int
                    }
                }
            ]
        }
    """
    # 加载环境变量
    load_dotenv()
    
    # 从环境变量获取host配置
    host = os.getenv("RAG_HOST", "127.0.0.1:8024")
    
    url = f"http://{host}/kb/search"
    
    payload = {
        "kb_name": kb_name,
        "query": query,
        "top_k": top_k,
        "use_rerank": True,
        "remove_duplicates": True
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查响应状态
        print(2323, response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return {"error": str(e)}

def format_rag_content(rag_results: Dict[str, Any]) -> str:
    """
    将RAG检索结果格式化为可用的参考文本
    
    Args:
        rag_results: 从get_rag_data返回的结果
        
    Returns:
        str: 格式化后的参考文本
    """
    if rag_results.get("status") != "success" or "data" not in rag_results:
        return ""
    
    formatted_content = []
    for i, item in enumerate(rag_results["data"]):
        content = item.get("content", "").strip()
        if content:
            source = ""
            if "metadata" in item and "file_name" in item["metadata"]:
                source = f"(来源: {item['metadata']['file_name']})"
            
            formatted_content.append(f"参考片段 {i+1} {source}:\n{content}\n")
    
    return "\n".join(formatted_content)
