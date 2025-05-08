# 全国景区数据分析及可视化系统前端

## 项目简介

这是一个基于Vue 3和TypeScript构建的全国景区数据分析及可视化系统前端项目，使用Vite作为构建工具。该项目提供景区数据的可视化展示、分析和管理功能，包括景区分布、分类、门票价格分析、评论分析和交通分析等多维度功能。

## 技术栈

- **框架**: Vue 3
- **语言**: TypeScript
- **构建工具**: Vite
- **路由管理**: Vue Router 4
- **状态管理**: Pinia
- **UI组件库**: Element Plus
- **图表库**: ECharts
- **HTTP客户端**: Axios
- **预处理器**: Sass

## 项目结构

```
src/
├── api/             # API请求相关
│   ├── admin.ts     # 管理员API
│   ├── axios.ts     # Axios实例与拦截器
│   ├── error-logger.ts # 错误日志记录
│   ├── image-proxy.ts # 图片代理服务
│   ├── scenic.ts    # 景区数据API
│   └── user.ts      # 用户相关API
├── assets/          # 静态资源文件
├── components/      # 可复用组件
│   ├── charts/      # 图表组件
│   │   └── BaseChart.vue # 基础图表组件
│   └── common/      # 通用组件
│       ├── CardContainer.vue # 卡片容器组件
│       └── ScenicCard.vue # 景区卡片组件
├── layouts/         # 布局组件
│   ├── AdminLayout.vue # 管理员布局
│   └── DashboardLayout.vue # 用户仪表盘布局
├── router/          # 路由配置
├── stores/          # 状态管理
│   ├── admin.ts     # 管理员状态
│   ├── scenic.ts    # 景区数据状态
│   └── user.ts      # 用户状态
├── views/           # 页面视图
│   ├── admin/       # 管理员相关页面
│   │   ├── ErrorLogs.vue    # 错误日志管理
│   │   ├── UserRecords.vue  # 用户记录管理
│   │   └── Users.vue        # 用户管理
│   ├── dashboard/   # 仪表盘相关页面
│   │   ├── CommentAnalysis.vue      # 评论分析
│   │   ├── Home.vue                 # 首页
│   │   ├── Profile.vue              # 个人中心
│   │   ├── ScenicClassification.vue # 景区分类分析
│   │   ├── ScenicDetail.vue         # 景区详情
│   │   ├── ScenicDistribution.vue   # 景区分布分析
│   │   ├── Search.vue               # 搜索页面
│   │   ├── TicketAnalysis.vue       # 门票分析
│   │   └── Transportation.vue       # 交通分析
│   ├── AdminLogin.vue     # 管理员登录
│   ├── ForgotPassword.vue # 忘记密码
│   ├── Login.vue          # 用户登录
│   ├── Register.vue       # 用户注册
│   └── ResetPassword.vue  # 重置密码
├── App.vue          # 根组件
├── main.ts          # 应用入口
└── style.css        # 全局样式
```

## 功能特点

- **用户系统**：登录、注册、密码重置、个人资料管理
- **管理员系统**：用户管理、操作记录查看、错误日志查看
- **景区分析**：
  - 景区地理分布可视化
  - 景区等级与分类分析
  - 门票价格与开放时间分析
  - 游客评论与情感分析
  - 交通与可达性分析
- **搜索功能**：多条件筛选和搜索景区
- **景区详情**：查看单个景区的详细信息
- **响应式设计**：适配不同屏幕尺寸
- **路由守卫**：基于权限的访问控制

## 开发环境设置

### 前提条件

- Node.js (v16+)
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

- `/api` -> `http://localhost:8001`
- `/media` -> `http://localhost:8001`

## 项目依赖

主要依赖包括：
- axios: API请求
- echarts: 数据可视化图表
- highcharts: 依赖轮图（交通方式）
- echarts-wordcloud: 词云图表
- element-plus: UI组件库
- pinia: 状态管理
- vue-router: 路由管理
- vue-echarts: Vue的ECharts集成
- vue-lazyload: 图片懒加载

## 许可证

[添加许可证信息] 