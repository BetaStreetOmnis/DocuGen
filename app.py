import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
import uvicorn
import json
import asyncio

# 导入功能模块
from llm.client import LLMClient
from base_templates_generator.base_templates_generator import BaseTemplatesGenerator
from generator_doc.generator_doc import DocumentGenerator
from knowledge_connect.get_rag_data import get_rag_data, get_knowledge_bases, format_rag_content

# 创建FastAPI应用
app = FastAPI(
    title="DocuGen - AI文档生成系统",
    description="一个强大的AI文档生成系统，支持基于用户上传模板生成文档和AI自定义文档创建",
    version="1.0.0"
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 创建必要的目录
Path("downloads").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)
Path("static/html").mkdir(exist_ok=True)

# 初始化服务
# 默认使用第三方模型
llm_client = LLMClient(model_type="third_party")
# BaseTemplatesGenerator 用于处理模板相关的操作（上传、列表、基于模板生成文档、提取变量）
template_generator = BaseTemplatesGenerator(model_type="third_party")
# DocumentGenerator 用于处理AI生成大纲和全文的逻辑
document_generator = DocumentGenerator(model_type="third_party")

# 页面路由
@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    return FileResponse("static/html/index.html")

@app.get("/qa", response_class=HTMLResponse)
async def qa():
    """智能问答页面"""
    return FileResponse("static/html/qa.html")

@app.get("/document-generator", response_class=HTMLResponse)
async def document_generator_page():
    """文档生成页面"""
    return FileResponse("static/html/document_generator.html")

@app.get("/template-generator", response_class=HTMLResponse)
async def template_generator_page():
    """模板生成页面"""
    return FileResponse("static/html/template_generator.html")

@app.get("/platform", response_class=HTMLResponse)
async def platform_dashboard():
    """ToB平台主页"""
    return FileResponse("static/html/platform_dashboard.html")

@app.get("/data-input", response_class=HTMLResponse)
async def data_input_page():
    """数据写入页面"""
    return FileResponse("static/html/data_input.html")

@app.get("/knowledge-base", response_class=HTMLResponse)
async def knowledge_base_page():
    """知识库页面"""
    return FileResponse("static/html/knowledge_base.html")

@app.get("/applications", response_class=HTMLResponse)
async def applications_page():
    """智能应用页面"""
    return FileResponse("static/html/applications.html")

@app.get("/qa", response_class=HTMLResponse)
async def qa_page():
    return FileResponse("static/html/qa.html")

# API: 生成大纲
import traceback
@app.post("/api/generate-outline")
async def generate_outline(request: Request):
    try:
        data = await request.json()
        topic = data.get("topic")
        key_points = data.get("key_points", "")
        enable_rag = data.get("enable_rag", False)
        kb_name = data.get("kb_name", "")
        
        if not topic:
            raise HTTPException(status_code=400, detail="主题不能为空")
            
        # 如果启用了RAG，获取相关内容
        rag_content = None
        if enable_rag and kb_name:
            rag_response = get_rag_data(kb_name, topic)
            if "error" not in rag_response:
                # 使用格式化函数处理RAG结果
                rag_content = format_rag_content(rag_response)
        
        # 使用全局document_generator实例
        result = document_generator.generate_outline(topic, key_points, rag_content)
        
        return JSONResponse(content=result)
    except Exception as e:
        print(f"生成大纲时发生错误: {str(e)}")
        print(f"错误类型: {type(e)}")
        print(f"错误详情: {str(traceback.format_exc())}")
        raise HTTPException(status_code=500, detail=str(e))

# API: 根据大纲生成完整文档
@app.post("/api/generate-fulltext")
async def generate_fulltext(
    outline: str = Form(...),
    key_points: Optional[str] = Form(None)
):
    """
    根据大纲和关键词开始生成完整文档。
    """
    try:
        result = document_generator.start_fulltext_generation(outline, key_points)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/generate-fulltext-stream")
async def generate_fulltext_stream(
    outline: str = Query(...),
    key_points: str = Query(""),
    enable_rag: bool = Query(False),
    kb_name: str = Query(""),
    custom_rag_content: str = Query("")
):
    """
    流式生成完整文档内容。
    """
    async def event_generator():
        try:
            # 准备生成参数
            generation_params = {
                "outline": outline,
                "key_points": key_points,
                "enable_rag": enable_rag,
                "kb_name": kb_name,
                "custom_rag_content": custom_rag_content
            }
            
            # 发送思考状态
            yield f"data: {json.dumps({'thinking': True})}\n\n"
            
            # 构建完整的提示词
            prompt = f"请根据以下大纲生成完整的文档内容：\n\n{outline}"
            if key_points:
                prompt += f"\n\n关键要点：{key_points}"
            
            # 如果启用RAG，获取相关知识
            rag_content = ""
            if enable_rag:
                try:
                    if kb_name == "custom" and custom_rag_content:
                        rag_content = custom_rag_content
                    elif kb_name:
                        # 使用知识库检索
                        from knowledge_connect.get_rag_data import get_rag_data, format_rag_content
                        rag_response = get_rag_data(kb_name, outline)
                        rag_content = format_rag_content(rag_response)
                    
                    if rag_content:
                        prompt += f"\n\n参考资料：\n{rag_content}"
                except Exception as e:
                    print(f"RAG处理错误: {e}")
                    # 发送错误信息但继续处理
                    yield f"data: {json.dumps({'error': f'RAG处理错误: {str(e)}'})}\n\n"
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": "你是一位专业的文档撰写专家，擅长根据大纲生成完整、详细、结构清晰的文档内容。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用LLM生成内容
            full_content = ""
            try:
                for chunk in llm_client.stream_chat(messages=messages):
                    # 检查是否是错误响应
                    if isinstance(chunk, dict) and "error" in chunk:
                        print(f"LLM客户端返回错误: {chunk['error']}")
                        yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                        yield "data: [DONE]\n\n"
                        return
                    
                    # 提取响应内容
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        if "delta" in chunk["choices"][0] and "content" in chunk["choices"][0]["delta"]:
                            content = chunk["choices"][0]["delta"]["content"]
                            if content:
                                full_content += content
                                # 发送完整内容而不是增量内容
                                yield f"data: {json.dumps({'content': full_content})}\n\n"
            except Exception as stream_error:
                print(f"流式响应处理出错: {str(stream_error)}")
                yield f"data: {json.dumps({'error': f'流式响应处理出错: {str(stream_error)}'})}\n\n"
                yield "data: [DONE]\n\n"
                return
            
            # 发送完成标记
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

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
        # 返回相对于服务器下载目录的文件名
        # 客户端需要调用 /download 端点来获取文件
        filename = os.path.basename(file_path)
        return JSONResponse(content={"filename": filename})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# API: 根据模板生成文档
@app.post("/api/generate-from-template")
async def generate_from_template(
    template_name: str = Form(...),
    data: str = Form(...)  # JSON格式的数据字符串
):
    """
    根据指定的模板和提供的JSON数据生成文档。
    """
    try:
        import json
        data_dict = json.loads(data)
        
        # 使用全局 template_generator 实例生成文档
        file_path = template_generator.generate_from_template(template_name, data_dict)
        
        # 返回相对于服务器下载目录的文件名
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
        # 使用全局 template_generator 实例列出模板
        templates_list = template_generator.list_templates()
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
        # 根据文件扩展名确定媒体类型
        if filename.lower().endswith(".docx"):
             media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename.lower().endswith(".pdf"):
             media_type = "application/pdf"
        else:
             media_type = "application/octet-stream" # 其他类型的默认值

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
        global llm_client, template_generator, document_generator
        
        # 验证模型类型
        if model_type not in ["local", "third_party"]:
            raise ValueError("不支持的模型类型，请使用'local'或'third_party'")
        
        # 更新所有服务的模型类型
        # 假设 switch_model_type 存在并更新内部模型
        llm_client.switch_model_type(model_type)
        
        # 使用新的模型类型重新初始化生成器/处理器
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
    上传Word文档模板文件。
    """
    try:
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        
        # 确保 template_name 可以安全地用作文件名
        # 移除不允许的字符，保留字母、数字、空格、点、下划线
        safe_template_name = "".join(c for c in template_name if c.isalnum() or c in (' ', '.', '_')).rstrip()
        if not safe_template_name:
             safe_template_name = f"uploaded_template_{uuid.uuid4().hex[:8]}" # 使用UUID避免冲突

        # 确保文件扩展名是 .docx
        if not safe_template_name.lower().endswith(".docx"):
             safe_template_name += ".docx"
             
        file_path = templates_dir / safe_template_name
        
        # 读取上传的文件内容并写入目标路径
        content = await template_file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 使用全局 template_generator 实例提取变量并注册模板
        # register_uploaded_template 应该处理元数据/变量提取
        template_metadata = template_generator.register_uploaded_template(str(file_path))
        
        # 返回成功信息和提取的变量
        print({
            "success": True, 
            "filename": file_path.name, # 返回文件名
            "template_name": template_name, # 返回用户提供的名称
            "variables": template_metadata.get("variables", [])
        })
        return JSONResponse(content={
            "success": True, 
            "filename": file_path.name, # 返回文件名
            "template_name": template_name, # 返回用户提供的名称
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
        # 根据 template_name 查找实际的文件名 (假设 .docx)
        # 更健壮的方法可能需要存储 template_name -> filename 的映射
        # 尝试查找匹配 template_name 的 .docx 文件
        template_filename = None
        templates_dir = Path("templates")
        for file in templates_dir.glob("*.docx"):
            # Assuming template_name is stored/associated with the file somehow
            # A simple approach is to match the base name (without extension)
            # A better approach would be to query the registered templates list
            # For now, let's assume template_name is the base filename
            if file.stem == template_name:
                 template_filename = file.name
                 break
        
        if not template_filename:
             return JSONResponse(
                content={"error": f"模板文件 '{template_name}.docx' 不存在"}, # Or just '{template_name}'
                status_code=404
            )

        template_path = os.path.join("templates", template_filename)
        
        # 使用全局 template_generator 实例提取变量
        variables = template_generator.extract_variables_from_template(template_path)
        
        return JSONResponse(content={"template_name": template_name, "variables": variables})
    
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
# API: 处理聊天请求
@app.post("/api/chat")
async def chat(request: Request):
    """处理聊天请求"""
    try:
        data = await request.json()
        message = data.get("message")
        
        if not message:
            raise HTTPException(status_code=400, detail="消息不能为空")
            
        # 构建消息列表
        messages = [
            {"role": "user", "content": message}
        ]
        
        # 使用LLM客户端获取回复
        response = llm_client.chat(messages=messages)
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
            
        # 提取回复内容
        reply = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not reply:
            raise HTTPException(status_code=500, detail="模型返回内容为空")
            
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/stream")
async def chat_stream(
    message: str = Query(...),
    enable_rag: bool = Query(False),
    kb_name: str = Query(""),
    custom_rag_content: str = Query("")
):
    print(f"收到流式聊天请求: message={message}, enable_rag={enable_rag}, kb_name={kb_name}")
    
    async def event_generator():
        try:
            # 处理RAG逻辑，获取相关知识
            rag_content = ""
            references = []
            
            if enable_rag:
                if kb_name == "custom" and custom_rag_content:
                    rag_content = custom_rag_content
                    print(f"使用自定义知识: {custom_rag_content[:50]}...")
                    references.append({"title": "自定义知识", "content": custom_rag_content[:100] + "..."})
                elif kb_name:
                    print(f"从知识库 {kb_name} 检索相关内容...")
                    rag_response = get_rag_data(kb_name, message)
                    if "error" not in rag_response:
                        rag_content = format_rag_content(rag_response)
                        # 提取参考信息
                        if "data" in rag_response and isinstance(rag_response["data"], list):
                            for i, item in enumerate(rag_response["data"][:3]):  # 最多显示前3条参考
                                if isinstance(item, dict):
                                    # 提取标题和内容
                                    title = "未知来源"
                                    if "metadata" in item and "file_name" in item["metadata"]:
                                        title = item["metadata"]["file_name"]
                                    elif "title" in item:
                                        title = item["title"]
                                    
                                    content = item.get("content", "")
                                    if content:
                                        references.append({
                                            "title": title, 
                                            "content": content[:200] + ("..." if len(content) > 200 else "")
                                        })
                        print(f"检索到 {len(references)} 条相关参考")
            
            # 构建系统消息
            system_message = "你是一个专业的智能助手，请根据用户的问题提供准确、简洁的回答。"
            if rag_content:
                system_message += "\n\n以下是一些相关的参考信息，请在回答时参考这些信息：\n\n" + rag_content
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ]
            
            # 先发送思考中的消息
            yield f"data: {json.dumps({'content': '思考中...', 'thinking': True})}\n\n"
            
            # 调用LLM客户端获取流式响应
            print("开始调用LLM获取流式响应...")
            full_response = ""
            
            # 使用全局llm_client调用stream_chat方法
            try:
                for chunk in llm_client.stream_chat(messages=messages):
                    # 检查是否是错误响应
                    if isinstance(chunk, dict) and "error" in chunk:
                        print(f"LLM客户端返回错误: {chunk['error']}")
                        yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                        yield "data: [DONE]\n\n"
                        return
                    
                    # 提取响应内容
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        if "delta" in chunk["choices"][0] and "content" in chunk["choices"][0]["delta"]:
                            content = chunk["choices"][0]["delta"]["content"]
                            if content:
                                full_response += content
                                print(f"收到内容: {content[:20]}..." if len(content) > 20 else f"收到内容: {content}")
                                yield f"data: {json.dumps({'content': full_response})}\n\n"
            except Exception as stream_error:
                print(f"流式响应处理出错: {str(stream_error)}")
                yield f"data: {json.dumps({'error': f'流式响应处理出错: {str(stream_error)}'})}\n\n"
                yield "data: [DONE]\n\n"
                return
            
            # 发送参考信息
            if references:
                print(f"发送参考信息: {len(references)} 条")
                yield f"data: {json.dumps({'references': references})}\n\n"
            
            # 发送结束标记
            print("LLM响应完成，发送结束标记")
            yield "data: [DONE]\n\n"
        except Exception as e:
            print(f"流式响应生成出错: {str(e)}")
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# API: AI填充模板变量
@app.post("/api/ai-fill-template-variables")
async def ai_fill_template_variables(request: Request):
    """
    使用AI自动填充模板变量，支持RAG增强。
    """
    try:
        data = await request.json()
        template_name = data.get("template_name")
        enable_rag = data.get("enable_rag", False)
        kb_name = data.get("kb_name", "default")
        custom_rag_content = data.get("custom_rag_content")
        
        if not template_name:
            raise HTTPException(status_code=400, detail="模板名称不能为空")
            
        # 查找模板文件
        template_filename = None
        templates_dir = Path("templates")
        for file in templates_dir.glob("*.docx"):
            if file.stem == template_name:
                template_filename = file.name
                break
        
        if not template_filename:
            return JSONResponse(
                content={"error": f"模板文件 '{template_name}.docx' 不存在"},
                status_code=404
            )

        template_path = os.path.join("templates", template_filename)
        
        # 提取模板变量
        variables = template_generator.extract_variables_from_template(template_path)
        if not variables:
            return JSONResponse(content={"error": "未在模板中找到任何变量"}, status_code=400)
            
        # 获取模板内容用于上下文
        template_content = template_generator.get_template_content(template_path)
        
        # 使用RAG获取相关内容
        rag_content = ""
        if enable_rag:
            if kb_name == "custom" and custom_rag_content:
                rag_content = custom_rag_content
            else:
                rag_response = get_rag_data(kb_name, template_name)  # 使用模板名称作为查询
                if "error" not in rag_response:
                    rag_content = format_rag_content(rag_response)
            
        # 构建提示词
        prompt = f"""请根据以下信息，为文档模板填充变量值：

模板内容概述：
{template_content}

需要填充的变量：
{json.dumps(variables, ensure_ascii=False, indent=2)}

{"相关参考信息：" if rag_content else ""}
{rag_content if rag_content else ""}

请根据模板内容和参考信息，生成合适的变量值。返回格式为JSON对象，key为变量名，value为填充值。
注意：
1. 生成的内容要符合上下文语境
2. 保持专业性和逻辑性
3. 确保填充值与变量名语义相符
4. 如果有参考信息，优先使用参考信息中的相关内容
"""

        # 构建消息列表
        messages = [
            {"role": "system", "content": "你是一个专业的文档助手，负责帮助用户填充文档模板中的变量。"},
            {"role": "user", "content": prompt}
        ]
        
        # 使用LLM生成变量值
        response = llm_client.chat(messages=messages)
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
            
        # 提取回复内容
        reply = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not reply:
            raise HTTPException(status_code=500, detail="模型返回内容为空")
            
        # 解析返回的JSON
        try:
            variables_values = json.loads(reply)
            # 验证返回的变量是否完整
            missing_vars = [var["name"] for var in variables if var["name"] not in variables_values]
            if missing_vars:
                raise HTTPException(status_code=500, detail=f"模型未能填充以下变量: {', '.join(missing_vars)}")
                
            return JSONResponse(content={
                "success": True,
                "variables": variables_values
            })
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="模型返回的不是有效的JSON格式")
            
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

# API: 获取知识库列表
@app.get("/api/kb/list")
async def list_kb_for_app():
    """获取所有可用的知识库列表，供前端选择"""
    try:
        print(f"[INFO] 开始获取知识库列表...")
        kb_list = get_knowledge_bases()
        print(f"[INFO] 获取到知识库列表: {kb_list}")
        
        # 确保返回的是前端期望的格式
        if isinstance(kb_list, list) and all(isinstance(item, str) for item in kb_list):
            # 如果已经是字符串列表，直接返回
            print(f"[INFO] 返回字符串列表格式: {len(kb_list)} 个知识库")
            return JSONResponse(content={"success": True, "data": kb_list})
        else:
            # 如果是对象列表，转换为字符串列表
            formatted_list = []
            for kb in kb_list:
                if isinstance(kb, dict) and "name" in kb:
                    formatted_list.append(kb["name"])
                elif isinstance(kb, str):
                    formatted_list.append(kb)
                else:
                    # 如果格式不符合预期，尝试转换为字符串
                    formatted_list.append(str(kb))
            print(f"[INFO] 转换后的知识库列表: {formatted_list}")
            return JSONResponse(content={"success": True, "data": formatted_list})
    except Exception as e:
        error_msg = f"获取知识库列表失败: {str(e)}"
        print(f"[ERROR] {error_msg}")
        
        # 检查是否是连接问题
        import os
        rag_host = os.getenv("RAG_HOST", "127.0.0.1:8024")
        detailed_error = f"{error_msg}\n详细信息:\n- RAG服务地址: {rag_host}\n- 请确保RAG服务正在运行\n- 检查网络连接和防火墙设置"
        
        return JSONResponse(content={
            "success": False, 
            "error": detailed_error,
            "rag_host": rag_host,
            "suggestions": [
                "检查RAG服务是否启动",
                "验证端口8024是否开放",
                "确认网络连接正常"
            ]
        }, status_code=500)

@app.post("/api/generate-document")
async def generate_document(request: Request):
    try:
        data = await request.json()
        title = data.get("title", "")
        prompt = data.get("prompt", "")
        doc_type = data.get("doc_type", "report")
        format = data.get("format", "markdown")
        enable_rag = data.get("enable_rag", False)
        kb_name = data.get("kb_name", "")
        custom_rag_content = data.get("custom_rag_content", "")
        
        # 这里调用文档生成逻辑
        # 简单示例，实际应用中应该调用LLM
        content = f"# {title}\n\n## 简介\n\n这是一个关于{title}的{doc_type}。\n\n## 内容\n\n{prompt}\n\n## 结论\n\n这是结论部分。"
        
        return {"success": True, "data": content}
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.post("/api/generate-template")
async def generate_template(request: Request):
    try:
        data = await request.json()
        template_type = data.get("template_type", "")
        description = data.get("description", "")
        format = data.get("format", "markdown")
        enable_rag = data.get("enable_rag", False)
        kb_name = data.get("kb_name", "")
        custom_rag_content = data.get("custom_rag_content", "")
        
        # 这里调用模板生成逻辑
        # 简单示例，实际应用中应该调用LLM
        if format == "markdown":
            content = f"# {template_type.capitalize()} 模板\n\n## 简介\n\n{description}\n\n## 主要内容\n\n- 第一部分\n- 第二部分\n- 第三部分\n\n## 结论\n\n这是结论部分。"
        elif format == "html":
            content = f"<!DOCTYPE html>\n<html>\n<head>\n<title>{template_type.capitalize()} 模板</title>\n</head>\n<body>\n<h1>{template_type.capitalize()} 模板</h1>\n<h2>简介</h2>\n<p>{description}</p>\n<h2>主要内容</h2>\n<ul>\n<li>第一部分</li>\n<li>第二部分</li>\n<li>第三部分</li>\n</ul>\n<h2>结论</h2>\n<p>这是结论部分。</p>\n</body>\n</html>"
        elif format == "json":
            content = {
                "title": f"{template_type.capitalize()} 模板",
                "description": description,
                "sections": [
                    {"title": "简介", "content": description},
                    {"title": "主要内容", "items": ["第一部分", "第二部分", "第三部分"]},
                    {"title": "结论", "content": "这是结论部分。"}
                ]
            }
        else:  # text
            content = f"{template_type.capitalize()} 模板\n\n简介:\n{description}\n\n主要内容:\n- 第一部分\n- 第二部分\n- 第三部分\n\n结论:\n这是结论部分。"
        
        return {"success": True, "data": content}
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.post("/api/generate-docx")
async def generate_docx(request: Request):
    """
    将Markdown内容转换为Word文档。
    """
    try:
        data = await request.json()
        title = data.get("title", "document")
        content = data.get("content", "")
        
        if not content:
            return JSONResponse(content={"success": False, "error": "内容不能为空"}, status_code=400)
        
        # 使用document_generator的export_to_doc方法生成Word文档
        file_path = document_generator.export_to_doc(content, "fulltext")
        
        # 返回相对于服务器下载目录的文件名
        filename = os.path.basename(file_path)
        return JSONResponse(content={"success": True, "filename": filename})
        
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

# 运行应用
if __name__ == "__main__":
    import uvicorn
    # 获取环境配置或使用默认值
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8080"))
    uvicorn.run("app:app", host=host, port=port, reload=True)