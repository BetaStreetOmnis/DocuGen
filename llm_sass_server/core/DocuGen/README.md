# DocuGen - AI文档生成系统

DocuGen是一个强大的AI驱动文档生成系统，支持智能文档创建和模板生成，可以无缝切换本地模型和第三方模型。

## 功能特点

- **AI文档生成**：根据主题和关键点自动生成文档大纲和完整内容
- **智能模板创建**：使用AI根据描述自动创建文档模板
- **模板填充**：使用JSON数据填充文档模板生成自定义文档
- **Word导出**：将生成的内容以专业格式导出为Word文档
- **模型切换**：支持在本地模型和第三方云端模型之间灵活切换

## 安装说明

1. 克隆仓库
```bash
git clone https://github.com/yourusername/docugen.git
cd docugen
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 创建并配置环境变量文件
```bash
cp .env.example .env
```
然后编辑`.env`文件，设置你的模型配置信息。

## 运行应用

```bash
python app.py
```

应用将在 http://localhost:8080 启动。

## 模型配置

DocuGen支持两种模型类型：

1. **本地模型**：运行在本地的AI模型，适合注重数据隐私的场景
   - 可通过设置`LOCAL_LLM_BASE_URL`和其他相关环境变量配置

2. **第三方模型**：如OpenAI、Azure OpenAI等云端模型
   - 可通过设置`THIRD_PARTY_LLM_BASE_URL`、`THIRD_PARTY_LLM_API_KEY`等环境变量配置

## 目录结构

- `/llm`：AI模型接口实现
- `/base_templates_generator`：文档模板生成器
- `/generator_doc`：文档生成器
- `/static`：Web前端静态资源
- `/web_templates`：Web页面模板
- `/templates`：生成的文档模板
- `/downloads`：生成的文档下载目录

## 技术栈

- 后端：Python, FastAPI
- 前端：HTML, CSS, JavaScript, Bootstrap, jQuery
- AI：自定义LLM接口，支持本地和第三方模型
- 文档：python-docx

## 贡献

欢迎提交问题和功能请求！

## 许可

MIT 