<div align="center">

# DocuGen 🖋️

✨ **AI智能文档生成系统** ✨

*让知识库变成你的专属写作助手*

</div>

<p align="center">
  <a href="124.132.152.75:8080/" target="_blank">
    <img alt="Live Demo" src="https://img.shields.io/badge/🚀_在线体验-brightgreen.svg"/>
  </a>
  <a href="https://github.com/BetaStreetOmnis/EasyRAG">
    <img alt="Knowledge Base" src="https://img.shields.io/badge/📚_知识库-EasyRAG-blue.svg"/>
  </a>
  <a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/python-3.8+-blue.svg">
  </a>
</p>

---

## 🎯 这是什么？

**DocuGen** = 你的知识库 + AI大模型 = 自动生成专业文档

上传你的资料 → 选择模板 → 一键生成文档，就这么简单！

![主界面](docs/images/index.png)

## ⚡ 快速开始

### 1️⃣ 准备知识库（使用 EasyRAG）

先去 [EasyRAG](https://github.com/BetaStreetOmnis/EasyRAG) 上传你的文档资料：

- 📄 支持 PDF、Word、Markdown 等格式
- 🔍 自动建立向量索引，智能检索
- 🌐 在线体验：http://easyrag.net/static/index.html

![知识库问答](docs/images/qa.png)

### 2️⃣ 启动 DocuGen 服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

### 3️⃣ 开始生成文档

访问 http://127.0.0.1:8080，选择知识库和模板，开始创作！

![文档生成器](docs/images/document_generator.png)

## 🎨 模板功能

### 智能模板生成
系统内置多种文档模板，也支持自定义：

![模板生成器1](docs/images/template_generator1.png)

### 模板效果预览
生成的文档格式专业，内容准确：

![模板生成器3](docs/images/template_generator3.png)

## 🏗️ 系统架构

![系统架构图](docs/images/diagram_1750905171.png)

- **DocuGen**：负责文档生成和模板管理
- **EasyRAG**：负责知识库管理和智能检索  
- **LLM服务**：提供AI写作能力

## 📋 配置说明

在 `.env` 文件中配置：

```bash
# LLM配置
LLM_API_URL=你的大模型API地址
LLM_API_KEY=你的API密钥

# EasyRAG配置  
EASYRAG_API_URL=http://127.0.0.1:8000
```

## ❓ 常见问题

**Q: 看不到我的知识库？**  
A: 确保 EasyRAG 服务正在运行，检查配置中的 API 地址。

**Q: 生成内容不准确？**  
A: 优化知识库内容质量，使用更强的 LLM 模型。

**Q: 支持哪些文档格式？**  
A: 取决于 EasyRAG 的支持，详见其[项目文档](https://github.com/BetaStreetOmnis/EasyRAG)。

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

[🚀 在线体验](http://170.106.72.96:8080/) • [📚 知识库项目](https://github.com/BetaStreetOmnis/EasyRAG)

</div>
