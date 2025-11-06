# MAI-WEB

一个基于 Vue 3 + Tailwind CSS 的博客前端与 FastAPI 异步后端组成的个人内容站点。后端负责管理与分发 Markdown 文章数据，前端负责渲染首页、博客列表、文章详情等页面，并在客户端完成 Markdown 与代码高亮。

## 功能亮点
- **内容管理**：数据库保存文章元数据与 Markdown 源文件路径，可通过脚本批量导入或清理。
- **Markdown 前端渲染**：文章正文在浏览器端解析，支持 GitHub Dark 代码高亮主题。
- **现代前端技术栈**：Vite 构建、Vue Router 页面切换、Tailwind CSS 快速样式编写。
- **异步后端接口**：FastAPI + SQLAlchemy Async 提供 RESTful API，并挂载静态目录供前端读取 Markdown。

## 技术栈
- 前端：Vue 3、Vite、Tailwind CSS、Vue Router、markdown-it、highlight.js
- 后端：FastAPI、SQLAlchemy 2.0（异步）、aiomysql、Pydantic Settings
- 数据库：MySQL（也可替换为其他 SQLAlchemy 支持的异步驱动）

## 目录结构
```
├── front/               # 前端应用源码
│   └── src/
│       ├── views/       # 页面视图（首页、博客、详情等）
│       ├── components/  # 公共组件（导航、页脚、文章列表等）
│       └── services/    # API 请求封装
├── backend/             # 后端应用源码
│   ├── app/             # FastAPI 应用、数据库模型、接口等
│   ├── content/         # Markdown 正文文件（启动时自动创建）
│   └── scripts/         # 数据导入、清理脚本
└── README.md            # 项目说明（当前文件）
```

## 快速开始

### 1. 克隆仓库
```bash
git clone <your-repo-url>
cd MAI-WEB
```

### 2. 启动后端
详见 `backend/README.md`，核心步骤：
1. 创建虚拟环境并安装依赖。
2. 配置 `.env`（数据库连接、CORS 来源等）。
3. 运行 `uvicorn app.main:app --reload`。

后端默认监听 `http://localhost:8000`，并暴露 `/api/posts`、`/api/posts/{post_id}`、`/api/posts/slug/{slug}` 等接口，同时提供 `/content/*` 静态资源读取 Markdown。

### 3. 启动前端
详见 `front/README.md`，核心步骤：
1. 安装 Node.js 依赖。
2. 配置 `VITE_API_BASE_URL` 指向后端地址。
3. 运行 `npm run dev` 并访问 `http://localhost:5173`。

## 内容导入与维护
- Markdown 文件建议统一放在 `backend/content/`，前端通过后端返回的 `content_path` 请求原文。
- 使用 `python scripts/import_markdown.py --dir <目录>` 批量导入文章，脚本会自动生成 slug、摘要并写入数据库。
- 使用 `python scripts/clear_posts.py --slug <slug...>` 或 `--all --yes` 管理已有文章。

## 部署建议
- 前后端可分别部署：后端运行在 WSGI/ASGI 兼容环境（如 Uvicorn + Gunicorn + Supervisor）；前端通过 `npm run build` 后静态托管。
- 更新 `BACKEND_CORS_ORIGINS` 与 `VITE_API_BASE_URL` 以匹配生产域名。
- 数据库建议使用托管 MySQL 并定期备份 `posts` 表及 Markdown 原文目录。

## 常见问题
- **跨域访问失败**：检查 `.env` 中 `BACKEND_CORS_ORIGINS` 是否包含前端地址。
- **文章正文 404**：确认导入脚本是否成功写入 Markdown 文件，或 `content_path` 是否指向已存在的文件。
- **代码高亮不生效**：确保前端安装依赖后重新构建，且高亮样式 `highlight.js/styles/github-dark.css` 已被正确引入。
