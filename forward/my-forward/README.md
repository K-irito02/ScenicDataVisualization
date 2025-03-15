# 全国景区的数据分析及可视化系统

## 项目简介

本项目是全国景区的数据分析及可视化系统的前端部分，基于Vue3 + TypeScript + Vite + ECharts开发。系统提供景区基础分布分析、景区等级与分类分析、门票与开放时间分析、评论与情感分析、交通与可达性分析等多个数据可视化模块，以及用户登录注册、搜索与筛选、个人中心等功能。

## 技术栈

- Vue 3 + Composition API
- TypeScript
- Vite
- Pinia (状态管理)
- Vue Router (路由管理)
- ECharts (数据可视化)
- Element Plus (UI组件库)
- Axios (HTTP请求)

## 项目结构
C:\ScenicDataVisualization\forward\my-forward\src
```
src/
├── assets/             # 静态资源
│   └── vue.svg         # Vue logo
├── components/         # 公共组件
│   ├── charts/         # 图表相关组件
│   │   └── BaseChart.vue  # 基础图表组件
│   ├── common/         # 通用组件
│   │   ├── CardContainer.vue  # 卡片容器组件
│   │   └── ScenicCard.vue     # 景区卡片组件
│   └── HelloWorld.vue  # Hello World示例组件
├── layouts/            # 布局组件
│   ├── DashboardLayout.vue  # 仪表板布局
│   └── AdminLayout.vue      # 管理员布局
├── router/             # 路由配置
│   └── index.ts        # 路由定义
├── stores/             # Pinia状态管理
│   ├── index.ts        # Store入口
│   ├── user.ts         # 用户相关状态
│   └── scenic.ts       # 景区数据相关状态
├── views/              # 页面视图
│   ├── Login.vue       # 登录页
│   ├── Register.vue    # 注册页
│   ├── AdminLogin.vue  # 管理员登录页
│   ├── dashboard/      # 仪表板页面
│   │   ├── ScenicDistribution.vue    # 景区基础分布分析
│   │   ├── ScenicClassification.vue  # 景区等级与分类分析
│   │   ├── TicketAnalysis.vue        # 门票与开放时间分析
│   │   ├── CommentAnalysis.vue       # 评论与情感分析
│   │   ├── Transportation.vue        # 交通与可达性分析
│   │   ├── Search.vue                # 搜索与筛选
│   │   ├── Profile.vue               # 个人中心
│   │   └── ScenicDetail.vue          # 景区详情
│   └── admin/          # 管理后台页面
│       ├── Users.vue             # 用户管理
│       └── UserRecords.vue       # 用户记录
├── App.vue             # 根组件
├── main.ts             # 入口文件
├── style.css           # 全局样式
├── vite-env.d.ts       # Vite环境类型声明
└── shims-vue.d.ts      # Vue类型声明
```

## 已实现功能

### 1. 用户认证模块

- **用户注册**: 支持用户名、邮箱注册，包含邮箱验证码功能
- **用户登录**: 基于JWT的用户认证系统
- **管理员登录**: 独立的管理员入口，权限控制

### 2. 数据可视化模块

- **景区基础分布分析**:
  - 使用中国地图展示全国景区分布热点
  - 提供省级下钻功能，展示各省份景区密度
  - 支持热力图与散点图切换展示
  - 提供区域分布特征总结与分析

- **景区等级与分类分析**: 
  - 使用环形图展示不同级别景区的数量分布
  - 展示各类景区（如5A、4A级景区，国家级博物馆等）的平均票价
  - 支持在景区、博物馆、地质公园等分类之间切换
  - 提供数据分析结论

- **门票与开放时间分析**:
  - 使用箱线图展示不同级别景区的门票价格分布
  - 通过环形图展示景区开放时间分布
  - 支持交互查看不同时间段开放的景区地理分布
  - 提供价格和开放时间的分析结论

- **评论与情感分析**:
  - 使用散点图展示景区评论数量与情感得分关系
  - 为热门景区提供词云展示高频词
  - 支持按情感得分排序和筛选
  - 提供评论情感趋势分析与游客关注点总结

- **交通与可达性分析**:
  - 使用桑基图展示不同交通方式的流量分布
  - 提供景区可达性评分与分析
  - 展示周边交通设施分布情况
  - 支持按地区和交通方式筛选数据

### 3. 用户功能模块

- **搜索与筛选功能**:
  - 提供多维度搜索功能（关键词、地区、类型、级别、价格区间）
  - 支持筛选结果排序（热度、价格、评分）
  - 结果以卡片式布局展示，包含基本信息与缩略图
  - 集成快速收藏功能

- **个人中心功能**:
  - 用户资料查看与修改
  - 头像上传功能
  - 用户信息保存
  - 用户收藏景区列表展示
  - 取消收藏功能
  - 跳转到景区详情

- **景区详情页**:
  - 展示景区基础信息（名称、级别、地址、票价等）
  - 提供景区图片轮播展示
  - 展示开放时间、交通方式等实用信息
  - 集成评论展示与情感分析结果
  - 支持收藏功能

### 4. 管理后台功能

- **用户管理**:
  - 展示用户列表与基本信息
  - 提供用户搜索与筛选功能
  - 支持用户账号状态管理（启用/禁用）
  - 用户行为分析统计

- **用户记录管理**:
  - 展示用户搜索历史记录
  - 展示用户收藏操作记录
  - 支持按用户、操作类型和时间筛选
  - 提供数据导出功能

## 开发与构建

```bash
# 安装依赖
npm install

# 开发环境运行
npm run dev

# 生产环境构建
npm run build

# 预览构建结果
npm run preview
```

## 技术问题解决

在开发过程中，我们解决了以下技术问题：

1. **TypeScript类型声明**: 为项目中使用的模块添加了适当的类型定义
2. **响应式布局**: 确保在不同设备上有良好的显示效果
3. **ECharts集成**: 实现了多种复杂图表的交互功能
4. **数据处理和转换**: 针对API返回的数据进行适当的转换以满足图表需求
5. **地图组件集成**: 实现中国地图及省级地图的下钻功能
6. **性能优化**: 对大数据量的图表进行了渲染性能优化
7. **组件复用**: 设计了可复用的图表组件库，提高开发效率

## 后端API接口需求

后端需要提供以下API接口：

### 1. 用户认证相关

```
POST /api/login/
请求参数：
{
  "username": "用户名或邮箱",
  "password": "密码"
}
返回数据：
{
  "token": "JWT令牌",
  "user_id": "用户ID",
  "username": "用户名",
  "email": "邮箱",
  "avatar": "头像URL",
  "location": "所在地",
}
```

```
POST /api/register/
请求参数：
{
  "username": "用户名",
  "email": "邮箱",
  "password": "密码",
  "code": "邮箱验证码"
}
返回数据：
{
  "message": "注册成功"
}
```

```
POST /api/email/send-code/
请求参数：
{
  "email": "邮箱"
}
返回数据：
{
  "message": "验证码已发送"
}
```

```
PUT /api/users/profile/
请求头：
Authorization: Bearer {token}
请求参数：
{
  "username": "新用户名", // 可选
  "avatar": "新头像URL", // 可选
  "location": "新所在地", // 可选
  "email": "新邮箱" // 可选
}
返回数据：
{
  "message": "资料更新成功"
}
```

### 2. 景区数据相关

```
GET /api/scenic/list/
请求参数：
{
  "keyword": "搜索关键词",
  "province": "省份",
  "city": "城市",
  "type": "景区类型",
  "level": "景区级别",
  "price_min": "最低票价",
  "price_max": "最高票价",
  "sort": "排序方式(popularity/price_asc/price_desc/rating)",
  "page": "页码",
  "page_size": "每页数量"
}
返回数据：
{
  "total": "总数量",
  "data": [
    {
      "id": "景区ID",
      "name": "景区名称",
      "province": "所在省份",
      "city": "所在城市",
      "type": "景区类型",
      "level": "景区级别",
      "price": "票价",
      "rating": "评分",
      "image": "图片URL"
    }
  ]
}

GET /api/scenic/detail/{id}/
返回数据：
{
  "id": "景区ID",
  "name": "景区名称",
  "images": ["图片URL1", "图片URL2"],
  "province": "所在省份",
  "city": "所在城市",
  "address": "详细地址",
  "price": "票价",
  "opening_hours": "开放时间",
  "type": "景区类型",
  "level": "景区级别",
  "description": "景区描述",
  "suggested_duration": "建议游玩时长",
  "sentiment": {
    "score": "情感得分",
    "intensity": "情感强度",
    "keywords": ["关键词1", "关键词2"]
  },
  "transportation": [
    {
      "type": "交通方式",
      "description": "交通描述"
    }
  ],
  "facilities": [
    {
      "type": "设施类型",
      "name": "设施名称",
      "distance": "距离"
    }
  ]
}

GET /api/scenic/recommend/{id}/
请求参数：
{
  "limit": "返回数量"
}
返回数据：
{
  "data": [
    {
      "id": "景区ID",
      "name": "景区名称",
      "image": "图片URL",
      "price": "票价",
      "rating": "评分"
    }
  ]
}
```

### 3. 评论数据相关

```
GET /api/comment/analysis/
请求参数：
{
  "sort": "排序方式(commentCount/sentimentScore/sentimentIntensity)"
}
返回数据：
{
  "data": [
    {
      "scenic_id": "景区ID",
      "scenic_name": "景区名称",
      "comment_count": "评论数量",
      "sentiment_score": "情感得分",
      "sentiment_intensity": "情感强度"
    }
  ]
}

GET /api/comment/wordcloud/{scenic_id}/
返回数据：
{
  "data": [
    {
      "name": "词语",
      "value": "词频"
    }
  ],
  "aspects": [
    {
      "name": "关注点名称",
      "description": "关注点描述",
      "sentiment": "关注点情感得分"
    }
  ]
}

GET /api/comment/list/{scenic_id}/
请求参数：
{
  "page": "页码",
  "page_size": "每页数量"
}
返回数据：
{
  "total": "总数量",
  "data": [
    {
      "id": "评论ID",
      "user": {
        "id": "用户ID",
        "username": "用户名",
        "avatar": "头像URL"
      },
      "content": "评论内容",
      "rating": "评分",
      "sentiment_score": "情感得分",
      "created_at": "创建时间"
    }
  ]
}
```

### 4. 交通数据相关

```
GET /api/transportation/sankey/
请求参数：
{
  "region": "地区(all/华北/华东等)"
}
返回数据：
{
  "nodes": [
    {
      "name": "节点名称(城市或交通方式)"
    }
  ],
  "links": [
    {
      "source": "源节点名称",
      "target": "目标节点名称",
      "value": "数值"
    }
  ]
}

GET /api/transportation/accessibility/
请求参数：
{
  "transport_type": "交通类型(all/car/train/bus/subway)"
}
返回数据：
{
  "data": [
    {
      "name": "省份名称",
      "value": "可达性评分"
    }
  ],
  "facilities": [
    {
      "type": "设施类型",
      "name": "设施名称",
      "count": "数量" 
    }
  ]
}
```

### 5. 用户管理相关

```
GET /api/admin/users/
请求参数：
{
  "query": "搜索关键词",
  "page": "页码",
  "page_size": "每页数量"
}
返回数据：
{
  "total": "总数量",
  "active_users": "活跃用户数",
  "new_users": "新用户数(近30天)",
  "disabled_users": "禁用用户数",
  "data": [
    {
      "id": "用户ID",
      "username": "用户名",
      "email": "邮箱",
      "phone": "手机号",
      "status": "状态(active/disabled)",
      "role": "角色(user/admin)",
      "avatar": "头像URL",
      "location": "所在地",
      "created_at": "创建时间",
      "last_login": "最后登录时间"
    }
  ]
}

POST /api/admin/users/create/
请求参数：
{
  "username": "用户名",
  "email": "邮箱",
  "phone": "手机号",
  "password": "密码",
  "role": "角色(user/admin)",
  "status": "状态(active/disabled)"
}

PUT /api/admin/users/{id}/
请求参数：
{
  "username": "用户名",
  "email": "邮箱",
  "phone": "手机号",
  "role": "角色(user/admin)",
  "status": "状态(active/disabled)"
}

DELETE /api/admin/users/{id}/

PATCH /api/admin/users/{id}/status/
请求参数：
{
  "status": "状态(active/disabled)"
}
```

### 6. 用户记录管理相关

```
GET /api/admin/user_records/
请求参数：
{
  "user_id": "用户ID",
  "record_type": "记录类型(search/view/favorite)",
  "start_date": "开始日期",
  "end_date": "结束日期",
  "page": "页码",
  "page_size": "每页数量"
}
返回数据：
{
  "total": "总数量",
  "search_count": "搜索记录数",
  "view_count": "浏览记录数",
  "favorite_count": "收藏记录数",
  "type_distribution": [
    {
      "name": "记录类型",
      "value": "数量"
    }
  ],
  "time_trend": [
    {
      "date": "日期",
      "search": "搜索数量",
      "view": "浏览数量",
      "favorite": "收藏数量"
    }
  ],
  "data": [
    {
      "id": "记录ID",
      "user_id": "用户ID",
      "username": "用户名",
      "record_type": "记录类型",
      "content": "记录内容",
      "scenic_id": "景区ID",
      "scenic_name": "景区名称",
      "created_at": "创建时间"
    }
  ]
}

GET /api/admin/user_records/{id}/
返回数据：
{
  "id": "记录ID",
  "user": {
    "id": "用户ID",
    "username": "用户名",
    "email": "邮箱",
    "avatar": "头像URL"
  },
  "record_type": "记录类型",
  "content": "详细内容",
  "ip_address": "IP地址",
  "user_agent": "用户代理",
  "created_at": "创建时间",
  "scenic": {
    "id": "景区ID",
    "name": "景区名称",
    "image": "图片URL"
  }
}

DELETE /api/admin/user_records/{id}/
```

### 7. 用户个人相关

```
POST /api/user/favorite/
请求参数：
{
  "scenic_id": "景区ID"
}
返回数据：
{
  "status": "success/error",
  "message": "操作结果信息"
}

DELETE /api/user/favorite/{scenic_id}/

GET /api/user/favorites/
请求参数：
{
  "page": "页码",
  "page_size": "每页数量"
}
返回数据：
{
  "total": "总数量",
  "data": [
    {
      "id": "收藏ID",
      "scenic": {
        "id": "景区ID",
        "name": "景区名称",
        "image": "图片URL",
        "price": "票价",
        "province": "省份",
        "city": "城市"
      },
      "created_at": "收藏时间"
    }
  ]
}
```

## 注意事项

1. 所有API接口返回的数据格式应为JSON
2. 用户认证采用JWT令牌方式
3. 需要认证的接口在请求头中添加`Authorization: Bearer {token}`
4. 管理员相关接口只有管理员用户可以访问
5. 前端开发过程中遇到类型定义问题请在项目中添加适当的类型声明文件
