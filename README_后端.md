 # 景区数据可视化系统 - 后端项目

本项目是景区数据可视化系统的后端部分，基于Django REST Framework开发，提供了用户管理、景区数据查询和管理员功能等API接口。

## 项目结构

```
backend/
├── __init__.py                   # 包初始化文件
├── asgi.py                       # ASGI配置
├── wsgi.py                       # WSGI配置
├── settings.py                   # 项目配置文件
├── urls.py                       # 主URL配置
├── db_routers.py                 # 数据库路由器
├── README.md                     # 项目说明文档
└── data_processing/              # 数据处理模块
    
user_management/                  # 用户管理应用
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── models.py                     # 用户相关模型（用户资料、收藏、操作记录）
├── serializers.py                # 用户数据序列化器
├── tests.py
├── urls.py                       # 用户相关URL配置
└── views.py                      # 用户相关视图（登录、注册、资料更新、收藏）

scenic_data/                      # 景区数据应用
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── models.py                     # 景区数据模型（景区信息、票价、交通、等级等）
├── serializers.py                # 景区数据序列化器
├── tests.py
├── urls.py                       # 景区数据相关URL配置
└── views.py                      # 景区数据相关视图（景区分布、等级分类、票价、搜索等）

admin_management/                 # 管理员应用
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── models.py
├── serializers.py                # 管理员数据序列化器
├── tests.py
├── urls.py                       # 管理员相关URL配置
└── views.py                      # 管理员相关视图（用户管理、用户记录）
```

## 数据库结构

项目使用了两个MySQL数据库：

1. **scenic_area**：存储主要的景区数据
   - `summary_table`: 景区主要信息表
   - `price_process_Django`: 门票价格表
   - `province_traffic`: 省份交通数据表
   - `time_process`: 开放时间表
   - `traffic_add`: 交通数据表

2. **hierarchy_ticketanalysis**：存储景区等级与票价关系数据
   - `scenic_level_price`: 景区等级票价表
   - `museum_level_price`: 博物馆等级票价表
   - `geological_park_level_price`: 地质公园等级票价表
   - `forest_park_level_price`: 森林公园等级票价表
   - `wetland_level_price`: 湿地公园等级票价表
   - `cultural_relic_level_price`: 文物保护单位等级票价表
   - `nature_reserve_level_price`: 自然景区等级票价表

## API接口

系统提供了以下几类API接口：

### 用户相关接口

- `POST /api/login/`: 用户登录
- `POST /api/register/`: 用户注册
- `PUT /api/users/profile/`: 用户资料更新
- `POST /api/favorites/toggle/`: 景区收藏切换
- `GET /api/favorites/`: 获取用户收藏列表

### 景区数据接口

- `GET /api/data/province-distribution/`: 省份景区分布数据
- `GET /api/data/scenic-levels/`: 景区等级与分类数据
- `GET /api/data/ticket-prices/`: 门票价格数据
- `GET /api/data/open-times/`: 开放时间数据
- `GET /api/data/comment-analysis/`: 评论情感分析数据
- `GET /api/data/word-cloud/<scenic_id>/`: 景区词云数据
- `GET /api/data/transportation/`: 交通方式数据
- `GET /api/scenic/search/`: 景区搜索接口
- `GET /api/data/filter-options/`: 筛选选项数据
- `GET /api/scenic/<id>/`: 景区详情接口

### 管理员接口

- `GET /api/admin/users/`: 用户管理接口
- `GET /api/admin/user-records/`: 用户记录接口

## 技术栈

- Django 5.1.6
- Django REST Framework
- MySQL数据库
- JWT认证

## 安装与运行

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 配置数据库：
   在settings.py中已配置MySQL连接信息。

3. 运行开发服务器：
   ```
   python manage.py runserver
   ```