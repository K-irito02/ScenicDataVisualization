# 全国景区数据分析及可视化系统后端

## 项目介绍
这是一个基于Django和Django REST Framework开发的全国景区数据分析及可视化系统后端。系统提供了景区数据管理、用户管理、收藏功能和数据分析等功能，为前端应用提供了全面的API支持。

## 技术栈
- **Python 3.x**
- **Django 5.1.6**
- **Django REST Framework**
- **MySQL** (单一数据库：scenic_area)
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
│   └── views.py          # 视图函数和API实现
├── scenic_data/          # 景区数据相关功能
│   ├── management/       # Django管理命令
│   ├── migrations/       # 数据库迁移文件
│   ├── models.py         # 景区数据模型
│   ├── serializers.py    # 数据序列化器
│   ├── type_level_data.json # 景区类型和级别数据
│   ├── urls.py           # URL路由
│   └── views.py          # 视图函数和API实现
├── scripts/              # 辅助脚本
│   ├── extract_location_data.py   # 位置数据提取
│   ├── extract_type_level_data.py # 类型级别数据提取
│   ├── fix_migrations.py           # 修复迁移问题
│   ├── migrate_hierarchy_tables.py # 数据库迁移脚本
│   └── update_frontend_data.py     # 前端数据更新脚本
│   └── download_scenic_images.py   # 景区图片下载脚本
├── user_management/      # 用户管理相关功能
│   ├── authentication.py # 自定义认证类
│   ├── middleware.py     # 自定义中间件
│   ├── models.py         # 用户数据模型
│   ├── serializers.py    # 数据序列化器
│   ├── urls.py           # URL路由
│   ├── utils.py          # 工具函数
│   └── views.py          # 视图函数和API实现
├── users/                # 用户资料和头像管理
│   ├── migrations/       # 数据库迁移文件
│   ├── models.py         # 用户资料模型
│   ├── urls.py           # URL路由
│   └── views.py          # 视图函数
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
   - 景区图片下载脚本 (`download_scenic_images.py`): 用于从马蜂窝等外部链接下载景区图片到本地服务器，并更新数据库中的图片URL。

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
- Redis (用于缓存)

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
- 启用CSRF保护

## CORS配置
系统已配置CORS以支持前端跨域请求：
- 开发环境允许所有源
- 支持凭证请求
- 配置了特定的允许头和方法
- 生产环境应明确指定允许的源

## 媒体文件
- 媒体文件存储在`media`目录下，其中景区图片存储在 `media/scenic_images/`
- 开发环境通过`settings.MEDIA_URL`提供访问
- 生产环境应配置服务器直接提供静态文件

- **运行方法**:
  ```bash
  # 进入项目根目录
  cd /var/www/scenic
  # 激活虚拟环境
  source venv/bin/activate
  # 运行脚本
  python backend/scripts/download_scenic_images.py
  ```
- **注意**:
    - 首次运行或大量图片更新时，脚本可能需要较长时间执行。
    - 确保 `/var/www/scenic/media/scenic_images/` 目录有写入权限。
    - 脚本支持断点续传，如果中途中断，再次运行时会从上次未完成的地方继续。

## 邮件服务
- 系统使用QQ邮箱SMTP服务
- 配置邮件发送功能用于找回密码和通知
- 生产环境应更新为企业邮箱

## 部署说明
1. 设置环境变量
2. 配置静态文件收集
3. 使用Gunicorn作为WSGI服务器
4. 配置Nginx作为反向代理
5. 设置SSL证书
6. 启用完整的CSRF保护 