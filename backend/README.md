# 全国景区数据分析及可视化系统后端

## 项目介绍
这是一个基于Django和Django REST Framework开发的全国景区数据分析及可视化系统后端。系统提供了景区数据管理、用户管理、收藏功能和数据分析等功能，为前端应用提供了全面的API支持。

## 技术栈
- **Python 3.x**
- **Django 5.1.6**
- **Django REST Framework**
- **MySQL** (单一数据库：scenic_area)
- **Redis** (缓存)
- **SMTP** (邮件服务)

## 项目结构
```
backend/
├── admin_management/     # 管理员功能模块
├── data_processing/      # 数据处理脚本和方法
├── scenic_data/          # 景区数据相关功能
├── scripts/              # 辅助脚本
│   └── migrate_hierarchy_tables.py  # 数据库迁移脚本
├── user_management/      # 用户管理相关功能
├── users/                # 用户资料和头像管理
├── __init__.py
├── asgi.py               # ASGI配置
├── manage.py             # Django命令行工具
├── settings.py           # 项目配置
├── urls.py               # URL路由配置
└── wsgi.py               # WSGI配置
```

## 主要功能模块
1. **景区数据管理** (`scenic_data`)
   - 景区数据的增删改查
   - 景区数据分析和可视化支持
   - 景区分类和级别管理

2. **用户管理** (`user_management`)
   - 用户认证（登录、注册、找回密码）
   - 用户收藏功能
   - 权限管理

3. **用户资料** (`users`)
   - 用户个人信息管理
   - 头像上传和管理

4. **管理员功能** (`admin_management`)
   - 系统管理员特有功能
   - 数据审核与管理

5. **数据处理** (`data_processing`)
   - 数据分析和处理方法
   - 数据导入导出功能

## 数据库配置
项目使用MySQL数据库：
- **scenic_area**: 存储景区、用户相关数据以及景区层次分析数据

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

### 创建超级用户
```bash
python manage.py createsuperuser
```

### 运行开发服务器
```bash
python manage.py runserver
```

## 安全提示
- 生产环境中请修改`settings.py`中的`SECRET_KEY`
- 关闭`DEBUG`模式
- 更新数据库密码和邮箱配置
- 配置适当的`ALLOWED_HOSTS`

## 部署说明
1. 设置环境变量
2. 配置静态文件收集
3. 使用Gunicorn/uWSGI作为WSGI服务器
4. 配置Nginx作为反向代理
5. 设置SSL证书

## 注意事项
- 项目使用Redis进行缓存，确保Redis服务已启动
- 邮件功能使用的是QQ邮箱SMTP服务，请根据需要替换为其他服务商
- 媒体文件存储在`media`目录下，确保该目录有适当的权限 