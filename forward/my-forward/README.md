# 景区数据可视化平台 (Scenic Data Visualization)

## 项目简介

这是一个基于Vue 3的景区数据可视化平台，用于展示和分析各类景区数据，包括景区分布、分类、票价、评论情感分析、交通可达性等维度的数据。该平台同时提供用户注册登录系统和管理员后台，为不同角色提供定制化的数据分析服务。

## 技术栈

- **前端框架**：Vue 3
- **类型系统**：TypeScript
- **构建工具**：Vite
- **状态管理**：Pinia
- **路由管理**：Vue Router
- **UI组件库**：Element Plus
- **图表库**：ECharts（包含词云插件echarts-wordcloud）
- **HTTP请求**：Axios
- **样式处理**：SASS

## 目录结构

```
my-forward/
├── public/                 # 静态资源目录
├── src/                    # 源代码
│   ├── api/                # API接口定义
│   │   ├── admin.ts        # 管理员相关API
│   │   ├── axios.ts        # Axios配置和拦截器
│   │   ├── index.ts        # API入口文件
│   │   ├── scenic.ts       # 景区数据相关API
│   │   └── user.ts         # 用户相关API
│   ├── assets/             # 资源文件（图片、字体等）
│   ├── components/         # 公共组件
│   ├── layouts/            # 布局组件
│   ├── router/             # 路由配置
│   │   └── index.ts        # 路由定义
│   ├── stores/             # Pinia状态管理
│   │   ├── admin.ts        # 管理员状态
│   │   ├── index.ts        # 状态管理入口
│   │   ├── scenic.ts       # 景区数据状态
│   │   └── user.ts         # 用户状态
│   ├── views/              # 页面组件
│   │   ├── admin/          # 管理员页面
│   │   ├── dashboard/      # 仪表盘页面
│   │   ├── AdminLogin.vue  # 管理员登录
│   │   ├── Login.vue       # 用户登录
│   │   └── Register.vue    # 用户注册
│   ├── App.vue             # 根组件
│   ├── main.ts             # 应用入口
│   ├── shims-vue.d.ts      # Vue类型声明
│   ├── style.css           # 全局样式
│   ├── vite-env.d.ts       # Vite环境变量类型声明
│   └── vue-router.d.ts     # Vue Router类型声明
├── .env                    # 环境变量
├── index.html              # HTML模板
├── package.json            # 项目依赖
├── tsconfig.json           # TypeScript配置
├── tsconfig.app.json       # 应用TypeScript配置
├── tsconfig.node.json      # Node环境TypeScript配置
└── vite.config.ts          # Vite配置
```

## 功能模块

### 1. 用户系统
- 用户注册
- 用户登录
- 个人中心管理

### 2. 管理员系统
- 管理员登录
- 用户管理
- 用户记录管理

### 3. 景区数据分析
- **景区基础分布分析**：地理分布、数量统计等
- **景区等级与分类分析**：不同等级、类型景区的数据对比
- **门票与开放时间分析**：票价分析、开放时间分布等
- **评论与情感分析**：用户评论分析、情感分值统计等
- **交通与可达性分析**：交通方式、可达性指标等

### 4. 数据交互功能
- 景区搜索与筛选
- 景区详情查看
- 数据可视化（图表、地图等）

## 项目特点

1. **完整的用户认证系统**：包含普通用户和管理员两种角色的登录流程，使用JWT进行身份验证
2. **多维度数据可视化**：使用ECharts实现多种图表展示，包括地图、柱状图、饼图、词云等
3. **响应式设计**：基于Element Plus组件库，提供良好的移动端和桌面端适配
4. **状态管理**：使用Pinia进行状态管理，分离数据逻辑和视图逻辑
5. **类型安全**：全项目使用TypeScript，提供类型安全保障

## 开发与构建

### 开发环境启动
```bash
npm install
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 预览生产构建
```bash
npm run preview
``` 