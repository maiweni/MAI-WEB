# MAI-WEB 前端

使用 Vue 3、Vite 和 Tailwind CSS 构建的单页应用，提供博客首页、文章列表、文章详情、关于与联系等页面。文章数据与正文通过调用后端接口获取，并在客户端完成 Markdown 渲染与代码高亮。支持登录、注册、会员分层访问控制。

## 关键特性
- **客户端路由**：`vue-router` 管理首页 (`/`)、博客列表 (`/blog`)、文章详情 (`/blog/:slug`) 等路由。
- **文章渲染**：`markdown-it` 解析 Markdown，`highlight.js` 提供 GitHub Dark 主题代码高亮。
- **Tailwind CSS**：`tailwind.config.js` 自定义主题，配合 `style.css` 与组件内 class 快速构建布局。
- **服务封装**：`src/services/api.js` 统一处理接口请求、环境变量及错误提示。
- **组件化布局**：`SiteNav`、`SiteFooter`、`BlogGrid` 等组件复用导航、文章卡片等 UI。

## 环境要求
- Node.js 18+
- npm 9+（或兼容的 pnpm/yarn）

## 安装与开发
```bash
# 安装依赖
npm install

# 启动开发服务器 (http://localhost:5173)
npm run dev

# 构建生产包
npm run build

# 预览生产包
npm run preview
```

## 环境变量
复制 `.env.example`（如存在）或在项目根目录创建 `.env`，设置后端接口地址：
```bash
VITE_API_BASE_URL=http://localhost:8000
```
未设置时默认回退到 `http://localhost:8000`。认证接口（登录/注册/会员）同样依赖该地址。

## 目录结构概览
```
src/
├── App.vue               # 根组件，组合导航、页脚与 RouterView
├── main.js               # 应用入口，注册路由与全局样式
├── router/index.js       # 前端路由定义
├── components/           # 公共组件（导航、页脚、文章列表等）
├── views/                # 页面视图（Home、Blog、PostDetail、About、Contact）
├── services/api.js       # 后端请求封装（文章列表、详情）
└── style.css             # Tailwind 基础样式与自定义样式
```

## 与后端的联动
- 列表页调用 `GET /api/posts` 获取文章元信息（标题、摘要、标签、`content_path`、`visibility` 等）。
- 详情页调用 `GET /api/posts/slug/{slug}` 获取单篇文章正文（需登录；会员文章需会员身份），后端直接返回 `content` 字段。
- 认证：`/api/auth/register`、`/api/auth/login`、`/api/auth/me`、`/api/auth/upgrade`，Token 保存在浏览器 `localStorage`。
- 未登录访问受限文章时，前端会跳转到 `/login?redirect=当前页`，登录/注册成功后返回原页。
- 为避免跨域问题，请确保后端 `.env` 中 `BACKEND_CORS_ORIGINS` 包含前端地址。

## 发布与部署
1. 执行 `npm run build` 生成 `dist/`。
2. 将 `dist/` 内容部署到任意静态托管服务（Nginx、Vercel、Netlify 等）。
3. 更新部署环境中的 `VITE_API_BASE_URL`（可通过 `.env.production` 或环境变量注入）。
