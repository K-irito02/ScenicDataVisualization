# 景区数据可视化平台后端

## 项目简介

这是景区数据可视化平台的后端服务，基于Django和Django REST Framework构建，为前端应用提供API服务。本项目处理用户认证、景区数据管理、数据分析处理等功能，并支持多数据库连接以满足不同的数据存储需求。

## 技术栈

- **Web框架**: Django 5.1
- **API框架**: Django REST Framework
- **数据库**: 
  - MySQL (用于结构化数据存储)
  - MongoDB (用于景区原始数据存储)
- **认证系统**: 
  - Token认证
  - Session认证
- **跨域支持**: django-cors-headers
- **数据处理**: 
  - 自然语言处理(jieba分词)
  - 情感分析
  - 数据清洗与标准化
- **缓存系统**: Redis
- **邮件服务**: SMTP (通过QQ邮箱)

## 目录结构

```
backend/
├── admin_management/          # 管理员功能模块
│   ├── migrations/            # 数据库迁移文件
│   ├── serializers.py         # 数据序列化
│   ├── urls.py                # 路由配置
│   ├── views.py               # 视图函数
│   └── models.py              # 数据模型
├── user_management/           # 用户管理模块
│   ├── migrations/            # 数据库迁移文件
│   ├── models.py              # 用户数据模型
│   ├── serializers.py         # 用户数据序列化
│   ├── urls.py                # 用户路由配置
│   ├── utils.py               # 工具函数
│   └── views.py               # 用户视图函数
├── scenic_data/               # 景区数据模块
│   ├── migrations/            # 数据库迁移文件
│   ├── models.py              # 景区数据模型
│   ├── serializers.py         # 景区数据序列化
│   ├── urls.py                # 景区API路由
│   └── views.py               # 景区数据视图函数
├── data_processing/           # 数据处理模块
│   ├── scripts/               # 数据处理脚本
│   └── 数据处理方法和技术.md    # 数据处理方法文档
├── __pycache__/               # Python缓存文件
├── asgi.py                    # ASGI配置
├── check_db.py                # 数据库检查工具
├── db_routers.py              # 数据库路由配置
├── manage.py                  # Django管理脚本
├── settings.py                # 项目配置文件
├── urls.py                    # 主路由配置
└── wsgi.py                    # WSGI配置
```

## 功能模块

### 1. 用户管理系统
- 用户注册与登录
- 用户信息管理
- 用户权限控制
- 密码重置与修改
- 邮件验证

### 2. 管理员系统
- 管理员登录认证
- 用户管理功能
- 用户行为记录查询
- 系统数据管理

### 3. 景区数据管理
- 景区基础数据查询
- 景区地理分布数据
- 景区等级与分类
- 门票与开放时间
- 评论与情感分析
- 交通可达性分析

### 4. 数据处理系统
- 文本数据预处理
- 自然语言处理
- 情感分析
- 关键词提取
- 数据集成与增强
- 数据汇总与统计

## 数据库设计

项目使用多数据库配置:

1. **主数据库 (scenic_area)**
   - 用户信息
   - 景区基础数据
   - 评论数据
   - 用户行为记录

2. **层次分析数据库 (hierarchy_ticketanalysis)**
   - 景区等级与门票价格关系表

数据库路由器`db_routers.py`实现了对不同模型的读写操作路由到相应的数据库。

## API接口

API接口按功能分为三类：

### 用户接口
- `POST /api/register/` - 用户注册
- `POST /api/login/` - 用户登录
- `GET /api/user-profile/` - 获取用户信息
- `PUT /api/user-profile/` - 更新用户信息
- `POST /api/change-password/` - 修改密码

### 管理员接口
- `POST /api/admin/login/` - 管理员登录
- `GET /api/admin/users/` - 获取用户列表
- `GET /api/admin/user-records/` - 获取用户行为记录

### 景区数据接口
- `GET /api/scenic/list/` - 获取景区列表
- `GET /api/scenic/{id}/` - 获取景区详情
- `GET /api/scenic/distribution/` - 获取景区地理分布
- `GET /api/scenic/classification/` - 获取景区分类数据
- `GET /api/scenic/ticket-analysis/` - 获取门票分析数据
- `GET /api/scenic/comment-analysis/` - 获取评论分析数据
- `GET /api/scenic/transportation/` - 获取交通分析数据

## 部署与运行

### 环境要求
- Python 3.9+
- MySQL 8.0+
- Redis (可选，用于缓存)

### 安装依赖
```bash
pip install -r requirements.txt
```

### 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 运行开发服务器
```bash
python manage.py runserver
```

### 生产环境部署
生产环境推荐使用Gunicorn + Nginx的部署方式，确保关闭DEBUG模式并设置适当的ALLOWED_HOSTS。

## 安全注意事项

- 生产环境中更改默认密钥(SECRET_KEY)
- 关闭DEBUG模式
- 设置环境变量存储敏感信息
- 限制CORS来源
- 配置适当的安全中间件 