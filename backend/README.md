# MAI FastAPI 后端

## 快速开始

1. 建立虚拟环境并安装依赖：

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. 根据实际数据库连接修改 `.env`（可复制 `.env.example`）：

   ```env
   DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/mai_db
   BACKEND_CORS_ORIGINS=http://localhost:5173
   ```

3. 启动 FastAPI 服务：

   ```bash
   uvicorn app.main:app --reload
   ```

   首次启动会自动同步数据库表结构。

## API 概览

- `GET /api/posts`：获取所有文章。
- `GET /api/posts/{post_id}`：根据 ID 获取单篇文章。

所有返回数据均为 JSON，字段包含 `id`、`title`、`excerpt`、`content`、`tags`、`slug`、`created_at`、`updated_at`。

## 批量导入 Markdown 文章

1. 将 `.md` 文件放入 `backend/content/`（可按需自建子目录，如果使用 `--dir` 指定路径即可）。
2. 每个文件默认以 **文件名** 作为 slug；若 Markdown 第一行是 `# 标题`，会自动识别为文章标题。
3. 运行脚本导入尚未存在的文章：

   ```bash
   # 在 backend 目录下，确保虚拟环境已激活
   python scripts/import_markdown.py --dir ./content
   ```

   该脚本会：
   - 遍历目录下全部 `.md` 文件。
   - 以文件名生成 slug，判断数据库中是否已存在同名 slug。
   - 如不存在则解析 Markdown，取首段作为摘要，将正文转换成 HTML 并写入数据库。
   - 已存在的 slug 会被跳过，避免重复导入。

   自当前版本起，脚本会将 Markdown 文件复制到 `backend/content/` 并在数据库中存储其相对路径（`/content/xxx.md`）。前端在请求文章详情时会根据该路径获取原始 Markdown 并在客户端完成渲染。

可以通过 `--dir` 指定其它目录，例如 `python scripts/import_markdown.py --dir ~/Documents/posts`。

## 清理数据库中的文章

- 删除所有文章（需要双重确认）：

  ```bash
  python scripts/clear_posts.py --all --yes
  ```

- 按 slug 删除指定文章：

  ```bash
  python scripts/clear_posts.py --slug my-post-slug another-slug
  ```
