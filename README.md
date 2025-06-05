# 全国景区数据分析及可视化系统后端

## 项目介绍

这是一个基于Django和Django REST Framework开发的全国景区数据分析及可视化系统后端。系统提供了景区数据管理、用户管理、收藏功能和数据分析等功能，为前端应用提供了全面的API支持。

## 技术栈

- **Python 3.x**
- **Django 5.1.6**
- **Django REST Framework**
- **MySQL** (数据库名：scenic_area)
- **Redis** (缓存)
- **SMTP** (QQ邮箱服务)
- **CORS** (跨域资源共享)

## 项目结构

```
backend/
├── admin_management/     # 管理员功能模块
│   ├── middleware.py     # 错误日志中间件
│   ├── models.py         # 管理员数据模型
│   ├── scripts/          # 管理员脚本
│   ├── serializers.py    # 数据序列化器
│   ├── urls.py           # URL路由
│   └── views.py          # 视图函数和API实现（980行）
├── scenic_data/          # 景区数据相关功能
│   ├── management/       # Django管理命令
│   ├── migrations/       # 数据库迁移文件
│   ├── models.py         # 景区数据模型（184行）
│   ├── serializers.py    # 数据序列化器（308行）
│   ├── type_level_data.json # 景区类型和级别数据
│   ├── urls.py           # URL路由（67行）
│   └── views.py          # 视图函数和API实现（2271行）
├── scripts/              # 辅助脚本
│   ├── extract_location_data.py   # 位置数据提取
│   ├── extract_type_level_data.py # 类型级别数据提取
│   ├── fix_migrations.py          # 修复迁移问题
│   ├── migrate_hierarchy_tables.py # 数据库迁移脚本
│   └── update_frontend_data.py     # 前端数据更新脚本
├── user_management/      # 用户管理相关功能
│   ├── authentication.py # 自定义认证类
│   ├── middleware.py     # 自定义中间件（包括CORS和禁用用户处理）
│   ├── models.py         # 用户数据模型（57行）
│   ├── serializers.py    # 数据序列化器（310行）
│   ├── urls.py           # URL路由（24行）
│   ├── utils.py          # 工具函数
│   └── views.py          # 视图函数和API实现（833行）
├── users/                # 用户资料和头像管理
│   ├── migrations/       # 数据库迁移文件
│   ├── models.py         # 用户资料模型
│   ├── urls.py           # URL路由
│   └── views.py          # 视图函数
├── __init__.py
├── asgi.py               # ASGI配置
├── manage.py             # Django命令行工具
├── settings.py           # 项目配置（233行）
├── urls.py               # URL路由配置（46行）
└── wsgi.py               # WSGI配置
```

## 主要功能模块

1. **景区数据管理** (`scenic_data`)
   - 景区数据的增删改查
   - 景区数据分析和可视化支持
   - 景区分类和级别管理
   - 景区位置数据管理

2. **用户管理** (`user_management`)
   - 用户认证（登录、注册、找回密码）
   - 用户收藏功能
   - 权限管理
   - 自定义认证和中间件

3. **用户资料** (`users`)
   - 用户个人信息管理
   - 头像上传和管理

4. **管理员功能** (`admin_management`)
   - 系统管理员特有功能
   - 数据审核与管理
   - 错误日志记录

5. **辅助脚本** (`scripts`)
   - 数据提取和分析
   - 数据库迁移工具
   - 前端数据更新

## 数据库配置

项目使用MySQL数据库：

- **数据库名**: `scenic_area`
- **主机**: localhost
- **端口**: 3306
- **用户**: root
- **字符集**: utf8mb4

## API接口

API接口按功能模块组织：

- `/api/` - 用户管理和景区数据接口
- `/api/users/` - 用户资料和头像接口
- `/api/admin/` - 管理员功能接口
- `/admin/` - Django管理界面

## 环境配置

### 系统要求

- Python 3.x
- MySQL 5.7+
- Redis (用于缓存)

### 安装依赖

```bash
pip install django==5.1.6
pip install djangorestframework
pip install mysqlclient
pip install redis
pip install django-cors-headers
```

### 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 管理员后台

```bash
http://localhost:8002/admin/
```

### 创建超级用户

```bash
python manage.py createsuperuser
```

### 运行开发服务器

```bash
python manage.py runserver 0.0.0.0:8002
```

## 安全提示

- 生产环境中请修改`settings.py`中的`SECRET_KEY`
- 关闭`DEBUG`模式
- 更新数据库密码和邮箱配置
- 配置适当的`ALLOWED_HOSTS`
- 启用CSRF保护

## CORS配置

系统已配置CORS以支持前端跨域请求：

- 开发环境允许所有源：`CORS_ALLOW_ALL_ORIGINS = True`
- 支持凭证请求：`CORS_ALLOW_CREDENTIALS = True`
- 配置了特定的允许头和方法
- 已配置的允许域名包括:
  - `http://localhost:8002`
  - `http://localhost:5173`
  - `http://localhost:3001`
  - `http://127.0.0.1:8002`
  - `http://127.0.0.1:5173`
  - `http://127.0.0.1:3001`

## 媒体文件

- 媒体文件存储在`media`目录下
- 通过`settings.MEDIA_URL`提供访问
- 配置：`MEDIA_URL = '/media/'`

## 邮件服务

- 系统使用QQ邮箱SMTP服务
- 邮箱: 2412311965@qq.com
- SMTP服务器: smtp.qq.com
- 端口: 587
- 用途: 找回密码和系统通知

## 部署说明

1. 设置环境变量
2. 配置静态文件收集
3. 使用Gunicorn/uWSGI作为WSGI服务器
4. 配置Nginx作为反向代理
5. 设置SSL证书
6. 启用完整的CSRF保护

-------------------------

# 全国景区数据分析及可视化系统前端

## 项目简介

这是一个基于Vue 3和TypeScript构建的全国景区数据分析及可视化系统前端项目，使用Vite作为构建工具。该项目提供景区数据的可视化展示、分析和管理功能，包括景区分布、分类、门票价格分析、评论分析和交通分析等多维度功能。

## 技术栈

- **框架**: Vue 3.5.13
- **语言**: TypeScript 5.7.2
- **构建工具**: Vite 6.2.0
- **路由管理**: Vue Router 4.5.0
- **状态管理**: Pinia 2.3.1
- **UI组件库**: Element Plus 2.5.0
- **图表库**: ECharts 5.6.0
- **HTTP客户端**: Axios 1.6.0
- **预处理器**: Sass 1.72.0
- **额外图表库**: Highcharts 12.2.0 (交通分析图表)
- **图片优化**: Vue-Lazyload 3.0.0

## 项目结构

```
src/
├── api/             # API请求相关
│   ├── admin.ts     # 管理员API
│   ├── axios.ts     # Axios实例与拦截器
│   ├── error-logger.ts # 错误日志记录
│   ├── image-proxy.ts # 图片代理服务
│   ├── index.ts     # API导出
│   └── scenic.ts    # 景区数据API
│   └── user.ts      # 用户相关API
├── assets/          # 静态资源文件
├── components/      # 可复用组件
│   ├── charts/      # 图表组件
│   │   └── BaseChart.vue # 基础图表组件
│   ├── common/      # 通用组件
│   │   ├── CardContainer.vue # 卡片容器组件
│   │   └── ScenicCard.vue # 景区卡片组件
│   ├── HelloWorld.vue # 欢迎组件
│   └── TitleUpdater.vue # 页面标题更新组件
├── layouts/         # 布局组件
│   ├── AdminLayout.vue # 管理员布局
│   └── DashboardLayout.vue # 用户仪表盘布局
├── router/          # 路由配置
│   └── index.ts     # 路由定义和守卫
├── stores/          # 状态管理
│   ├── admin.ts     # 管理员状态
│   ├── index.ts     # Store导出
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
├── style.css        # 全局样式
├── vue-router.d.ts  # Vue Router类型定义
└── shims-vue.d.ts   # Vue类型定义
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

服务器将在 http://localhost:3001 上运行

### 构建生产版本

```bash
# 构建生产版本
npm run build
# 或
yarn build
```

### 预览构建版本

```bash
# 预览构建后的版本
npm run preview
# 或
yarn preview
```

## API代理配置

开发环境已配置API代理，将以下请求转发到后端服务器：

- `/api` -> `http://localhost:8002`
- `/media` -> `http://localhost:8002`

## 项目依赖

主要依赖包括：

- vue: 3.5.13 - 前端框架核心
- pinia: 2.3.1 - 状态管理
- vue-router: 4.5.0 - 路由管理
- element-plus: 2.5.0 - UI组件库
- @element-plus/icons-vue: 2.3.1 - Element Plus图标
- axios: 1.6.0 - HTTP请求库
- echarts: 5.6.0 - 数据可视化图表
- vue-echarts: 7.0.3 - Vue的ECharts集成
- echarts-wordcloud: 2.1.0 - 词云图表
- highcharts: 12.2.0 - 交通分析图表
- vue-lazyload: 3.0.0 - 图片懒加载

## 开发依赖

- typescript: 5.7.2
- vite: 6.2.0
- vue-tsc: 2.2.4
- @vitejs/plugin-vue: 5.2.1
- sass: 1.72.0
- @types/node: 20.11.0
- @types/highcharts: 5.0.44
- @vue/tsconfig: 0.7.0

## 许可证

[添加许可证信息] 
