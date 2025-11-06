# MAI-WEB 后端

基于 FastAPI 与 SQLAlchemy Async 的异步 REST API，负责管理文章元数据、提供文章列表/详情接口，并挂载静态目录输出 Markdown 原文。配套脚本可批量导入 Markdown 文件或清理文章记录。

## 环境要求
- Python 3.11+
- MySQL 8（或兼容的异步驱动数据库，默认使用 `mysql+aiomysql`）
- 建议使用虚拟环境管理依赖

## 安装与启动

### 1. 创建虚拟环境并安装依赖
```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量
复制 `.env.example`（若存在）到 `.env`，或直接创建 `.env`：
```env
DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/mai_db
BACKEND_CORS_ORIGINS=http://localhost:5173
```
- `DATABASE_URL` 支持任意 SQLAlchemy Async URL，例如 PostgreSQL 可切换为 `postgresql+asyncpg://...`。
- `BACKEND_CORS_ORIGINS` 支持逗号分隔多个来源。

### 3. 初始化数据库并启动服务
```bash
uvicorn app.main:app --reload
```
- 首次启动会自动创建 `posts` 表。
- 后端默认监听 `http://localhost:8000`。
- 静态目录 `backend/content/` 会在启动时自动创建并挂载为 `/content`。

## API 路由
- `GET /api/posts`：获取文章列表。
- `GET /api/posts/{post_id}`：按 ID 获取文章详情。
- `GET /api/posts/slug/{slug}`：按 slug 获取文章详情，供前端通过路径跳转。
- `/content/<filename>`：静态托管 Markdown 原文（供前端详情页拉取并解析）。

响应字段包含：
- `id`、`title`、`excerpt`、`content_path`、`tags`、`slug`、`created_at`、`updated_at`。

## 项目结构
```
app/
├── main.py        # FastAPI 入口，注册路由/CORS/静态目录
├── config.py      # 环境变量配置（Pydantic Settings）
├── database.py    # SQLAlchemy 异步引擎与会话
├── models.py      # 数据模型（Post）
├── schemas.py     # Pydantic 模型（输入/输出）
└── crud.py        # 数据库操作封装

scripts/
├── import_markdown.py  # 批量导入 Markdown
└── clear_posts.py      # 清理文章记录
```

## 管理 Markdown 与文章

### 批量导入 Markdown
```bash
python scripts/import_markdown.py --dir ./content
```
脚本行为：
- 扫描目标目录下 `.md` 文件，自动生成 slug、提取标题与摘要。
- 如数据库中已存在同名 slug，则跳过导入。
- 将 Markdown 文件复制到 `backend/content/`，并在数据库中记录 `content_path`。
- 导入完成后输出新增/跳过数量。

可通过 `--dir` 指定任意 Markdown 目录，例如：
```bash
python scripts/import_markdown.py --dir ~/Documents/posts
```

### 清理文章
- 删除所有文章（需双重确认）：
  ```bash
  python scripts/clear_posts.py --all --yes
  ```
- 按 slug 删除指定文章：
  ```bash
  python scripts/clear_posts.py --slug first-post another-post
  ```

## 部署建议
- 生产环境可使用 `uvicorn` + `gunicorn` 或 `uvicorn` 的多 worker 模式。
- 将 `.env` 中的 `DATABASE_URL` 与 `BACKEND_CORS_ORIGINS` 改为生产配置。
- 通过 Nginx/Traefik 等反向代理统一暴露 `/api` 与 `/content`。
- 定期备份数据库与 `backend/content/` 目录，以防 Markdown 原文丢失。

## 常见问题
- **数据库连接失败**：确认 MySQL 账号权限、网络连通性及 `aiomysql` 是否安装。
- **跨域请求被拒绝**：确保 `.env` 中的 `BACKEND_CORS_ORIGINS` 包含前端访问域名或端口。
- **Markdown 获取失败**：检查 `content_path` 是否指向实际存在的文件，或确认静态目录挂载是否正常。
