# DocuGen Vue Workspace

Vue 3 + Vite 前端，用于模板上传、变量提取、AI 填充与文档生成（对接 FastAPI 后端）。

## 开发

```bash
cd frontend
npm install
npm run dev
```

- 默认通过 Vite 代理将 `/api`、`/download` 指向 `http://127.0.0.1:8080`（见 `vite.config.js`）。如需更换后端地址，可在 `.env` 中设置 `VITE_API_BASE=http://your-host:8080`。
- 依赖：Node 18+、npm。

## 主要页面
- 模板上传：DOCX，名称/描述 + 文件，自动注册模板。
- 变量提取：从占位符（【变量】或 `{{变量}}`）提取变量并展示可编辑表单。
- AI 填充：可选开启 RAG，选择知识库或提供自定义片段。
 - 文档生成：提交变量，调用 `/api/generate-from-template`，返回文件名，可从 `/download/{filename}` 获取。
