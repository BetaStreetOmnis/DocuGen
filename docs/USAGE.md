# DocuGen 使用引导

本引导覆盖：环境配置 → 启动服务 → 连接知识库（可选）→ 上传模板 → 生成与下载。

## 1. 启动前准备

- Python：3.8+（建议使用虚拟环境）
- Node（可选）：18+（仅在开发/重建前端时需要）

建议使用虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置 `.env`

项目使用 `.env` 读取配置，推荐从示例复制：

```bash
cp .env.example .env
```

常用配置项：

- `APP_HOST` / `APP_PORT`：DocuGen 监听地址与端口（访问地址一般是 `http://127.0.0.1:${APP_PORT}`）。
- `DEFAULT_LLM_TYPE`：`local` 或 `third_party`。
- `THIRD_PARTY_LLM_BASE_URL` / `THIRD_PARTY_LLM_API_KEY` / `THIRD_PARTY_LLM_DEFAULT_MODEL`：第三方模型配置（OpenAI 兼容接口）。
- `LOCAL_LLM_BASE_URL`：本地模型（OpenAI 兼容接口）地址。
- `RAG_HOST`：EasyRAG 服务地址（形如 `127.0.0.1:8024`，无需带协议）。
- （可选）`AUTH_REQUIRED`：是否对 `/api`（除 `/api/auth/*`）启用鉴权；启用后需要先登录获取 token。
- （可选）`AUTH_ALLOW_REGISTER`：是否开放注册接口 `/api/auth/register`。
- （可选）`AUTH_REGISTER_CAPTCHA_REQUIRED`：注册是否需要验证码（本地生成）。

## 3. 启动 DocuGen

安装依赖后直接启动：

```bash
python app.py
```

启动成功后访问：

- Web：`http://127.0.0.1:${APP_PORT}`（以 `.env` 为准）
- 接口文档：`http://127.0.0.1:${APP_PORT}/docs`

如果页面是空白或资源 404，说明缺少前端构建产物，可执行一次：

```bash
cd frontend
npm install
npm run build
```

## 4. （可选）连接知识库：EasyRAG

DocuGen 通过 `RAG_HOST` 对接 EasyRAG（示例：`127.0.0.1:8024`），主要用到：

- `GET http://{RAG_HOST}/kb/list`：列出知识库
- `POST http://{RAG_HOST}/kb/search`：检索片段

快速自检：

```bash
curl -sS "http://127.0.0.1:8024/kb/list"
```

如果你暂时没有 EasyRAG，也可以在生成时关闭 RAG，直接粘贴“自定义参考内容”完成生成流程。

## 5. 模板生成工作流（推荐）

1. 打开首页 `http://127.0.0.1:${APP_PORT}`，进入「上传模版」上传你的 DOCX 模板。
2. 模板中用占位符声明变量（两种格式都支持）：
   - `【项目名称】`、`【日期】`
   - `{{项目名称}}`、`{{日期}}`
3. 上传后系统会自动提取变量；进入生成页填写变量值（可手填，也可让 AI 结合 RAG/自定义参考内容生成）。
4. 点击生成后会得到一个文件名，下载地址为：`/download/{filename}`。

## 6. 常见问题

- **看不到知识库列表**：确认 EasyRAG 已启动，且 `.env` 中 `RAG_HOST` 指向正确；也可先关闭 RAG 使用自定义参考内容。
- **端口冲突**：修改 `.env` 中 `APP_PORT` 后重启。
- **启用鉴权后接口报 401**：先在页面登录（或调用 `/api/auth/login`）获取 token，再访问受保护接口。
