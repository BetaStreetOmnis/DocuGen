import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
# No need for StaticFiles or Jinja2Templates in a pure API server

# 导入功能模块
# Assuming these modules are available in the environment
from llm.client import LLMClient
# 导入用于基于模板生成文档和管理模板的类
from base_templates_generator.base_templates_generator import BaseTemplatesGenerator
# 导入用于AI生成文档大纲和全文的类
from generator_doc.generator_doc import DocumentGenerator
# 导入RAG知识库相关功能
from knowledge_connect.get_rag_data import get_rag_data

# 创建FastAPI应用 - 纯API版本
app = FastAPI(
    title="DocuGen - AI文档生成系统 (API Only)",
    description="一个强大的AI文档生成系统API，支持基于模板生成文档和AI自定义文档创建",
    version="1.0.0"
)

# 创建必要的目录
Path("downloads").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# 初始化服务
# Note: Global variables are used here, similar to app.py.
# For a production API, dependency injection might be preferred.
llm_client = LLMClient(model_type="third_party")  # 默认使用第三方模型
# BaseTemplatesGenerator 用于处理模板相关的操作（创建、列表、基于模板生成文档）
template_processor = BaseTemplatesGenerator(model_type="third_party")
# DocumentGenerator 用于处理AI生成大纲和全文的逻辑
document_generator = DocumentGenerator(model_type="third_party")

# API: 生成大纲
@app.post("/api/generate-outline")
async def generate_outline(
    topic: str = Form(...),
    key_points: Optional[str] = Form(None),
    use_rag: bool = Form(False)  # 新增参数：是否使用RAG知识库
):
    """
    根据主题和关键词生成文档大纲。
    如果启用RAG，将使用知识库内容作为参考信息。
    """
    try:
        # 如果启用RAG，获取相关知识库内容
        rag_content = None
        if use_rag:
            rag_content = get_rag_data(topic)
            
        result = document_generator.generate_outline(topic, key_points, rag_content)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 根据大纲生成完整文档
@app.post("/api/generate-fulltext")
async def generate_fulltext(
    outline: str = Form(...),
    key_points: Optional[str] = Form(None),
    use_rag: bool = Form(False)  # 新增参数：是否使用RAG知识库
):
    """
    根据大纲和关键词开始生成完整文档。
    如果启用RAG，将使用知识库内容作为参考信息。
    """
    try:
        # 如果启用RAG，获取相关知识库内容
        rag_content = None
        if use_rag:
            rag_content = get_rag_data(outline)
            
        result = document_generator.start_fulltext_generation(outline, key_points, rag_content)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 获取生成状态
@app.get("/api/generation-status/{task_id}")
async def get_generation_status(task_id: str):
    """
    获取指定任务ID的文档生成状态。
    """
    try:
        result = document_generator.get_generation_status(task_id)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 处理下一个部分
@app.post("/api/process-next-section/{task_id}")
async def process_next_section(task_id: str):
    """
    处理指定任务ID的文档生成中的下一个部分。
    """
    try:
        result = document_generator.process_next_section(task_id)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 导出为Word文档
@app.post("/api/export-word")
async def export_word(
    content: str = Form(...),
    content_type: str = Form("outline")  # outline 或 fulltext
):
    """
    将生成的大纲或全文内容导出为Word文档。
    """
    try:
        file_path = document_generator.export_to_doc(content, content_type)
        # Return the file path relative to the server's downloads directory
        # The client will need to call the /download endpoint to get the file
        filename = os.path.basename(file_path)
        return JSONResponse(content={"filename": filename})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 根据模板生成文档
@app.post("/api/generate-from-template")
async def generate_from_template(
    template_name: str = Form(...),
    data: str = Form(...),  # JSON格式的数据字符串
    use_rag: bool = Form(False)  # 新增参数：是否使用RAG知识库
):
    """
    根据指定的模板和提供的JSON数据生成文档。
    如果启用RAG，将使用知识库内容作为参考信息。
    """
    try:
        import json
        data_dict = json.loads(data)
        
        # 如果启用RAG，获取相关知识库内容
        rag_content = None
        if use_rag:
            rag_content = get_rag_data(str(data_dict))
        
        # Re-initialize template_processor for consistency with upload_template
        current_model_type = template_processor.model_type # Get current model type
        temp_processor = BaseTemplatesGenerator(model_type=current_model_type)
        
        file_path = temp_processor.generate_from_template(template_name, data_dict, rag_content)
        # Return the file path relative to the server's downloads directory
        filename = os.path.basename(file_path)
        return JSONResponse(content={"filename": filename})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 列出所有模板
@app.get("/api/templates")
async def list_templates():
    """
    列出所有可用的文档模板。
    """
    try:
        # Re-initialize template_processor for consistency
        current_model_type = template_processor.model_type # Get current model type
        temp_processor = BaseTemplatesGenerator(model_type=current_model_type)
        
        templates_list = temp_processor.list_templates()
        return JSONResponse(content={"templates": templates_list})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 文件下载路由
@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    下载指定文件名的文件（通常是生成的文档）。
    """
    file_path = os.path.join("downloads", filename)
    if os.path.exists(file_path):
        # Determine media type based on file extension
        if filename.lower().endswith(".docx"):
             media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename.lower().endswith(".pdf"):
             media_type = "application/pdf"
        else:
             media_type = "application/octet-stream" # Default for other types

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type
        )
    raise HTTPException(status_code=404, detail="文件不存在")

# 切换模型类型
@app.post("/api/switch-model")
async def switch_model(model_type: str = Form(...)):
    """
    切换AI模型类型（local或third_party）。
    """
    try:
        global llm_client, template_processor, document_generator
        
        # 验证模型类型
        if model_type not in ["local", "third_party"]:
            raise ValueError("不支持的模型类型，请使用'local'或'third_party'")
        
        # 更新所有服务的模型类型
        # Assuming switch_model_type exists and updates the internal model
        llm_client.switch_model_type(model_type)
        
        # Re-initialize generators/processors with the new model type
        template_processor = BaseTemplatesGenerator(model_type=model_type)
        document_generator = DocumentGenerator(model_type=model_type)
        
        return JSONResponse(content={"success": True, "model_type": model_type})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 上传模板
@app.post("/api/upload-template")
async def upload_template(template_name: str = Form(...), 
                         template_file: UploadFile = File(...),
                         description: str = Form("")):
    """
    上传Word文档模板文件。
    """
    try:
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        
        # 保存上传的文件
        # Ensure template_name is safe for use as a filename
        safe_template_name = "".join(c for c in template_name if c.isalnum() or c in (' ', '.', '_')).rstrip()
        if not safe_template_name:
             safe_template_name = "uploaded_template"
             
        file_path = templates_dir / f"{safe_template_name}.docx"
        
        # Read uploaded file content and write to target path
        content = await template_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Use template processor to extract variables and register template
        # Re-initialize template_processor for consistency
        current_model_type = template_processor.model_type # Get current model type
        temp_processor = BaseTemplatesGenerator(model_type=current_model_type)
        
        # Assuming register_uploaded_template handles metadata/variable extraction
        template_metadata = temp_processor.register_uploaded_template(file_path, template_name, description)
        
        # Return success info and extracted variables
        return JSONResponse(content={
            "success": True, 
            "filename": file_path.name, # Return just the filename
            "template_name": template_name, # Return the user-provided name
            "variables": template_metadata.get("variables", [])
        })
    
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

# API: 获取模板变量
@app.get("/api/get-template-variables")
async def get_template_variables(template_name: str):
    """
    获取指定模板文件中的变量列表。
    """
    try:
        # Find the actual filename based on the template_name (assuming .docx)
        # A more robust approach might store template_name -> filename mapping
        template_filename = f"{template_name}.docx" # Assuming .docx extension
        template_path = os.path.join("templates", template_filename)
        
        if not os.path.exists(template_path):
            # Try finding it case-insensitively or by iterating if needed
            # For now, stick to exact match + .docx
             return JSONResponse(
                content={"error": f"模板文件 '{template_filename}' 不存在"},
                status_code=404
            )
        
        # Use template processor to extract variables
        # Re-initialize template_processor for consistency
        current_model_type = template_processor.model_type # Get current model type
        temp_processor = BaseTemplatesGenerator(model_type=current_model_type)
        
        variables = temp_processor.extract_variables_from_template(template_path)
        
        return JSONResponse(content={"template_name": template_name, "variables": variables})
    
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

# 运行应用
if __name__ == "__main__":
    import uvicorn
    # 获取环境配置或使用默认值
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001")) # Use a different default port than the web server
    uvicorn.run("api_server:app", host=host, port=port, reload=True)
