import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
import uvicorn

# 导入功能模块
from llm.client import LLMClient
from base_templates_generator.base_templates_generator import BaseTemplatesGenerator
from generator_doc.generator_doc import DocumentGenerator

# 创建FastAPI应用
app = FastAPI(
    title="DocuGen - AI文档生成系统",
    description="一个强大的AI文档生成系统，支持模板生成和自定义文档创建",
    version="1.0.0"
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板目录
templates = Jinja2Templates(directory="web_templates")

# 创建必要的目录
Path("downloads").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)
Path("web_templates").mkdir(exist_ok=True)
Path("static/html").mkdir(exist_ok=True)

# 初始化服务
llm_client = LLMClient(model_type="third_party")  # 默认使用第三方模型
template_generator = BaseTemplatesGenerator(model_type="third_party")
document_generator = DocumentGenerator(model_type="third_party")

# 首页路由 - 支持静态HTML和模板
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # 检查静态HTML是否存在
    static_html_path = Path("static/html/index.html")
    if static_html_path.exists():
        return FileResponse(static_html_path)
    # 使用模板
    return templates.TemplateResponse("index.html", {"request": request})

# 文档模板生成页面 - 支持静态HTML和模板
@app.get("/template-generator", response_class=HTMLResponse)
async def template_generator_page(request: Request):
    # 检查静态HTML是否存在
    static_html_path = Path("static/html/template_generator.html")
    if static_html_path.exists():
        return FileResponse(static_html_path)
    # 使用模板
    templates_list = template_generator.list_templates()
    return templates.TemplateResponse("template_generator.html", {
        "request": request,
        "templates": templates_list
    })

# 文档生成页面 - 支持静态HTML和模板
@app.get("/document-generator", response_class=HTMLResponse)
async def document_generator_page(request: Request):
    # 检查静态HTML是否存在
    static_html_path = Path("static/html/document_generator.html")
    if static_html_path.exists():
        return FileResponse(static_html_path)
    # 使用模板
    return templates.TemplateResponse("document_generator.html", {"request": request})

# API: 生成大纲
@app.post("/api/generate-outline")
async def generate_outline(
    topic: str = Form(...),
    key_points: Optional[str] = Form(None)
):
    try:
        result = document_generator.generate_outline(topic, key_points)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 根据大纲生成完整文档
@app.post("/api/generate-fulltext")
async def generate_fulltext(
    outline: str = Form(...),
    key_points: Optional[str] = Form(None)
):
    try:
        result = document_generator.start_fulltext_generation(outline, key_points)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 获取生成状态
@app.get("/api/generation-status/{task_id}")
async def get_generation_status(task_id: str):
    try:
        result = document_generator.get_generation_status(task_id)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 处理下一个部分
@app.post("/api/process-next-section/{task_id}")
async def process_next_section(task_id: str):
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
    try:
        file_path = document_generator.export_to_doc(content, content_type)
        return JSONResponse(content={"file_path": file_path})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 创建模板
@app.post("/api/create-template")
async def create_template(
    template_name: str = Form(...),
    description: str = Form(...)
):
    try:
        file_path = template_generator.generate_template_with_ai(template_name, description)
        return JSONResponse(content={"file_path": file_path, "template_name": template_name})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 根据模板生成文档
@app.post("/api/generate-from-template")
async def generate_from_template(
    template_name: str = Form(...),
    data: str = Form(...)  # JSON格式的数据
):
    try:
        import json
        data_dict = json.loads(data)
        file_path = template_generator.generate_from_template(template_name, data_dict)
        return JSONResponse(content={"file_path": file_path})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 列出所有模板
@app.get("/api/templates")
async def list_templates():
    try:
        templates_list = template_generator.list_templates()
        return JSONResponse(content={"templates": templates_list})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 文件下载路由
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("downloads", filename)
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    raise HTTPException(status_code=404, detail="文件不存在")

# 切换模型类型
@app.post("/api/switch-model")
async def switch_model(model_type: str = Form(...)):
    try:
        global llm_client, template_generator, document_generator
        
        # 验证模型类型
        if model_type not in ["local", "third_party"]:
            raise ValueError("不支持的模型类型，请使用'local'或'third_party'")
        
        # 更新所有服务的模型类型
        llm_client.switch_model_type(model_type)
        
        # 重新初始化生成器
        template_generator = BaseTemplatesGenerator(model_type=model_type)
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
    上传Word文档模板
    """
    try:
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        
        # 保存上传的文件
        file_path = templates_dir / f"{template_name}.docx"
        
        # 读取上传的文件内容并写入目标路径
        content = await template_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 使用模板生成器提取变量并注册模板
        template_generator = BaseTemplatesGenerator()
        template_metadata = template_generator.register_uploaded_template(file_path)
        
        # 返回成功信息和文件路径
        return {
            "success": True, 
            "file_path": str(file_path),
            "variables": template_metadata.get("variables", [])
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# API: 获取模板变量
@app.get("/api/get-template-variables")
async def get_template_variables(template_name: str):
    """
    获取模板变量
    """
    try:
        template_path = os.path.join("templates", f"{template_name}.docx")
        if not os.path.exists(template_path):
            return JSONResponse(
                content={"error": f"模板 '{template_name}' 不存在"}, 
                status_code=404
            )
        
        # 使用模板生成器提取变量
        template_generator = BaseTemplatesGenerator()
        variables = template_generator.extract_variables_from_template(template_path)
        
        return {"variables": variables}
    
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

# 运行应用
if __name__ == "__main__":
    # 获取环境配置或使用默认值
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8080"))
    uvicorn.run("app:app", host=host, port=port, reload=True) 