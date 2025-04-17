# 全国景区数据分析及可视化系统前端

## 项目简介

这是一个基于Vue 3和TypeScript构建的全国景区数据分析及可视化系统前端项目，使用Vite作为构建工具。该项目旨在提供景区数据的可视化展示、分析和管理功能。

## 技术栈

- **框架**: Vue 3
- **语言**: TypeScript
- **构建工具**: Vite
- **路由管理**: Vue Router
- **状态管理**: Pinia (推测)
- **图表库**: Highcharts, ECharts (wordcloud)
- **HTTP客户端**: Axios
- **数据库连接**: MySQL (通过后端API)

## 项目结构

```
src/
├── api/        # API请求相关
├── assets/     # 静态资源文件
├── components/ # 可复用组件
├── layouts/    # 布局组件
├── router/     # 路由配置
├── stores/     # 状态管理
├── views/      # 页面视图
│   ├── admin/      # 管理员相关页面
│   ├── dashboard/  # 仪表盘相关页面
│   ├── Login.vue   # 登录页面
│   ├── Register.vue # 注册页面
│   ├── AdminLogin.vue # 管理员登录
│   ├── ForgotPassword.vue # 忘记密码
│   └── ResetPassword.vue  # 重置密码
├── App.vue     # 根组件
├── main.ts     # 应用入口
└── style.css   # 全局样式
```

## 功能特点

- 用户认证系统（登录、注册、密码重置）
- 管理员专用入口
- 数据可视化仪表盘
- 响应式设计
- 页面过渡动画

## 开发环境设置

### 前提条件

- Node.js (推荐v16+)
- npm 或 yarn

### 安装

```bash
# 安装依赖
npm install
# 或
yarn install
```

### 开发服务器

```bash
# 启动开发服务器
npm run dev
# 或
yarn dev
```

服务器将在 http://localhost:3000 上运行

### 构建生产版本

```bash
# 构建生产版本
npm run build
# 或
yarn build
```

## API代理配置

开发环境已配置API代理，将以下请求转发到后端服务器：

- `/api` -> `http://localhost:8000`
- `/media` -> `http://localhost:8000`

## 项目依赖

主要依赖包括：
- axios: API请求
- highcharts: 数据可视化图表
- echarts-wordcloud: 词云图表

## 许可证

[添加许可证信息] 