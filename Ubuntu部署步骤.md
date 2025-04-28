 # 全国景区数据分析及可视化系统 - Ubuntu部署步骤

## 一、服务器环境准备

### 1. 安装基础工具
```bash
# 更新系统软件包
sudo apt update && sudo apt upgrade -y

# 安装基础开发工具
sudo apt install -y git wget vim build-essential
```

### 2. 安装Python环境
```bash
# 安装Python和开发工具
sudo apt install -y python3 python3-dev python3-pip python3-venv

# 更新pip
sudo -H pip3 install --upgrade pip
```

### 3. 安装MySQL
```bash
# 安装MySQL服务器
sudo apt install -y mysql-server

# 启动MySQL并设置开机自启
sudo systemctl start mysql
sudo systemctl enable mysql

# 配置MySQL安全设置
sudo mysql_secure_installation
```
<!-- 运行MySQL安全脚本时，会执行以下操作:
- 设置root密码（如果尚未设置）
- 移除匿名用户
- 禁止root远程登录
- 删除测试数据库
- 重载权限表 -->

### 4. 安装Redis
```bash
# 安装Redis服务器
sudo apt install -y redis-server

# 启动Redis并设置开机自启
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 5. 安装Node.js环境（用于前端构建）
```bash
# 安装NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# 加载NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  

# 安装Node.js 16
nvm install 16

# 确认版本
node -v
npm -v
```

### 6. 安装Nginx
```bash
# 安装Nginx
sudo apt install -y nginx

# 启动Nginx并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 二、后端部署准备

### 1. 创建项目目录
```bash
sudo mkdir -p /var/www/scenic
cd /var/www/scenic
```

### 2. 创建虚拟环境
```bash
# 创建Python虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 3. 上传后端代码
将本地`backend`目录上传到服务器的`/var/www/scenic/backend`目录
（可以使用SCP、SFTP或Git方式上传）

```bash
# 从GitHub拉取特定分支的backend文件夹
# 1. 确保安装了git
# sudo apt install -y git

# 2. 导航到目标父目录
cd /var/www/scenic

# 3. 克隆特定分支（如果使用私有仓库，使用个人访问令牌）
git clone -b lite_version --single-branch https://github.com/K-irito02/ScenicDataVisualization.git temp_repo
# 使用Token进行Git操作时，克隆仓库使用格式：
# git clone https://<你的token>@github.com/用户名/仓库名.git
例如：git clone -b lite_version --single-branch https://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@github.com/K-irito02/ScenicDataVisualization.git temp_repo
# 4. 移动backend文件夹到正确位置
mv temp_repo/backend .

# 5. 删除临时仓库目录
rm -rf temp_repo

# 6. 设置适当的权限 (Ubuntu中Nginx默认使用www-data用户)
sudo chown -R www-data:www-data /var/www/scenic/backend
sudo chmod -R 755 /var/www/scenic/backend

# 7. 创建并设置上传和日志目录权限
sudo mkdir -p /var/www/scenic/backend/uploads
sudo mkdir -p /var/www/scenic/backend/logs
sudo chown -R www-data:www-data /var/www/scenic/backend/uploads
sudo chown -R www-data:www-data /var/www/scenic/backend/logs
sudo chmod -R 775 /var/www/scenic/backend/uploads
sudo chmod -R 775 /var/www/scenic/backend/logs
```

### 4. 安装后端依赖
```bash
cd /var/www/scenic/backend
pip install -r requirements.txt
```

如果没有requirements.txt文件，根据README信息安装以下包：
```bash
pip install django==5.1.6 djangorestframework django-cors-headers mysqlclient redis
```

### 5. 修改后端配置
```bash
nano settings.py
```

修改以下内容：
```python
# 关闭DEBUG模式
DEBUG = False

# 设置允许的主机
ALLOWED_HOSTS = ['你的服务器IP', '你的域名']  

# 数据库配置（如有必要）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'scenic_area',
        'USER': '你的MySQL用户名',
        'PASSWORD': '你的MySQL密码',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/scenic/static'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/scenic/media'

# 安全密钥（生成新的密钥）
SECRET_KEY = '生成一个新的安全密钥'

# 添加具体的允许的域名列表作为备选方案
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'http://localhost:5173',
    'http://localhost:3000',
    'http://127.0.0.1:8080',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000',
    # 在这里添加您的生产环境域名
]

```

### 6. 配置MySQL数据库
# 数据库导入
# 先登录MySQL
mysql -u root -p
# 登录成功后，在MySQL提示符下执行
use scenic_area;
source /opt/scenic_area.sql;

<!-- ```bash
sudo mysql
```

```sql
CREATE DATABASE scenic_area CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'scenic_user'@'localhost' IDENTIFIED BY '设置一个强密码';
GRANT ALL PRIVILEGES ON scenic_area.* TO 'scenic_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
``` -->

### 7. 数据库迁移
# 更改整个项目目录权限（推荐做法）
# 如果这是您的开发环境，最好是给整个项目目录合适的权限：
# 查看目录的当前所有者和权限
ls -la /var/www/scenic/backend/scenic_data/migrations/

# 更改目录所有权给当前用户
sudo chown -R ubuntu:ubuntu /var/www/scenic/backend/scenic_data/migrations/

# 或者添加写入权限
sudo chmod -R 775 /var/www/scenic/backend/scenic_data/migrations/


```bash
cd /var/www/scenic/backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 8. 收集静态文件
```bash
python manage.py collectstatic
```

### 9. 安装Gunicorn
```bash
pip install gunicorn
```

### 10. 创建Gunicorn服务配置
```bash
sudo nano /etc/systemd/system/scenic-gunicorn.service
```

添加以下内容：
```
[Unit]
Description=Scenic Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/scenic/backend
Environment="PYTHONPATH=/var/www/scenic/backend"
ExecStart=/var/www/scenic/venv/bin/gunicorn --workers 3 --bind unix:/var/www/scenic/scenic.sock wsgi:application

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start scenic-gunicorn
sudo systemctl enable scenic-gunicorn
```

sudo systemctl daemon-reload
sudo systemctl restart scenic-gunicorn
sudo systemctl restart nginx

## 三、前端部署准备

### 1. 上传前端代码
将本地`forward/my-forward`目录上传到服务器的`/var/www/scenic/frontend`目录

```bash
# 如果使用GitHub仓库
cd /var/www/scenic
git clone -b lite_version --single-branch https://github.com/K-irito02/ScenicDataVisualization.git temp_repo
mv temp_repo/forward/my-forward /var/www/scenic/frontend
rm -rf temp_repo

# 设置权限
sudo chown -R www-data:www-data /var/www/scenic/frontend
sudo chmod -R 755 /var/www/scenic/frontend
```

### 2. 修改前端API配置
```bash
nano /var/www/scenic/frontend/.env
```

修改为：
```
VITE_API_BASE_URL=https://你的域名 # 或 http://你的服务器IP
```
www.k-irito.online

### 3. 安装前端依赖
```bash
sudo chown -R ubuntu:ubuntu /var/www/scenic/
cd /var/www/scenic/frontend
npm install
```
步骤1：安装 Highcharts 核心库​​
npm install highcharts --save
​​步骤2：安装 Highcharts 类型声明（TypeScript 必需）​​
npm install @types/highcharts --save-dev

### 4. 构建前端项目
```bash
npm run build
```
构建后的文件将位于`dist`目录

## 四、Nginx配置

### 1. 创建Nginx配置文件
```bash
sudo nano /etc/nginx/sites-available/scenic
```

添加以下内容：
```nginx
server {
    listen 80;
    server_name 你的服务器IP或域名;

    # 前端静态文件
    location / {
        root /var/www/scenic/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django管理界面
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 媒体文件
    location /media/ {
        alias /var/www/scenic/media/;
    }

    # 静态文件
    location /static/ {
        alias /var/www/scenic/static/;
    }
}
```

### 2. 启用站点配置并测试
#### 若目录下已存在
• 根本问题：  

  `/etc/nginx/sites-enabled/` 目录下已存在名为 `scenic` 的文件或链接，导致无法重复创建。

---

**2. 解决方案**

**方法1：删除现有文件后重新链接（推荐）**
```bash
# 1. 删除已存在的文件/链接
sudo rm /etc/nginx/sites-enabled/scenic

# 2. 重新创建符号链接
sudo ln -s /etc/nginx/sites-available/scenic /etc/nginx/sites-enabled/
```

**方法2：强制覆盖（如果确认需要替换）**
```bash
sudo ln -sf /etc/nginx/sites-available/scenic /etc/nginx/sites-enabled/
```
• `-f` 参数会强制覆盖现有文件。


**方法3：检查现有文件内容（谨慎操作）**
如果不确定是否要删除，先查看现有文件内容：
```bash
# 查看文件类型（是真实文件还是符号链接）
ls -l /etc/nginx/sites-enabled/scenic

# 查看文件内容（如果是真实文件）
cat /etc/nginx/sites-enabled/scenic
```
• 如果是无用的旧配置，用 方法1 删除。  

• 如果是其他有效配置，建议重命名而非删除：

  ```bash
  sudo mv /etc/nginx/sites-enabled/scenic /etc/nginx/sites-enabled/scenic.backup
  sudo ln -s /etc/nginx/sites-available/scenic /etc/nginx/sites-enabled/
  ```

---

**3. 验证操作**
```bash
# 检查链接是否创建成功
ls -l /etc/nginx/sites-enabled/ | grep scenic

# 应显示类似输出：
# lrwxrwxrwx 1 root root 35 May 10 10:00 scenic -> /etc/nginx/sites-available/scenic
```
sudo systemctl restart nginx  //重启服务	✅ 短暂中断

#### 若目录下不存在
```bash
sudo ln -s /etc/nginx/sites-available/scenic /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
# 1. sudo systemctl reload nginx 命令作用​​
# ​​功能​​：让 Nginx 服务 ​​重新加载配置文件​​（如 nginx.conf 或 sites-available/ 下的配置）。
# ​​特点​​：
# ​​不停机​​：重新加载过程中，Nginx 保持运行，不会中断现有连接（无缝过渡）。
# ​​安全​​：如果新配置有语法错误，会继续使用旧配置，避免服务崩溃。
# ​​2. 适用场景​​
# 修改了 Nginx 配置后（如添加新站点、调整反向代理规则）。
# 更新 SSL 证书后需要重新加载。
# 更改了负载均衡或缓存策略。
```

## 五、防火墙配置

### 开放必要的端口
```bash
# 安装UFW（如果尚未安装）
sudo apt install -y ufw

# 配置UFW规则
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# 如果防火墙未启用，可以启用
sudo ufw enable
```

<!-- ## 六、HTTPS配置（可选但推荐）
步骤1：修改 Nginx 配置​​
编辑你的 Nginx 站点配置文件（如 /etc/nginx/sites-available/scenic），确保包含以下规则：

server {
    listen 80;
    server_name www.k-irito.online;

    # 允许 Certbot 验证路径
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/html;
        default_type "text/plain";
        try_files $uri =404;  # 确保未找到文件时返回 404
    }

    # 其他配置...
    location / {
        root /var/www/scenic/frontend/dist;  # 前端构建产物路径
        try_files $uri $uri/ /index.html;
    }
}
步骤2：创建验证目录并设置权限​​
sudo mkdir -p /var/www/html/.well-known/acme-challenge
sudo chown -R ubuntu:ubuntu /var/www/html/.well-known
sudo chmod -R 755 /var/www/html/.well-known

​步骤3：测试并重载 Nginx​​
# 测试配置语法
sudo nginx -t

# 重载配置
sudo systemctl reload nginx
步骤4：验证路径是否返回 404​​
curl -I http://www.k-irito.online/.well-known/acme-challenge/test

​​期望输出​​：
HTTP/1.1 404 Not Found
​​步骤5：重新运行 Certbot​​
sudo certbot --nginx -d www.k-irito.online

方法 1：### 1. 安装Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. 获取并配置SSL证书
```bash
sudo certbot --nginx -d 你的域名
``` -->
方法 2：使用腾讯云免费证书
SSL证书配置已成功完成！以下是已完成的步骤：
✅ 解压了上传的证书文件 www.k-irito.online_nginx.zip
✅ 将证书文件放置在正确的位置：
证书文件：/etc/ssl/certs/k-irito.online.pem
私钥文件：/etc/ssl/private/k-irito.online.key
✅ 设置了正确的文件权限
✅ Nginx配置已经包含SSL设置
✅ Nginx配置测试通过
✅ 重启了Nginx服务

## 七、监控与维护

### 1. 查看日志
```bash
# Nginx日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Gunicorn服务日志
sudo journalctl -u scenic-gunicorn
```

### 2. 定期备份数据库
```bash
# 创建备份脚本
nano /var/www/scenic/backup_db.sh
```

添加以下内容：
```bash
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/www/backups"
mkdir -p $BACKUP_DIR
mysqldump -u scenic_user -p'密码' scenic_area > "$BACKUP_DIR/scenic_area_$TIMESTAMP.sql"
```

设置可执行权限并添加到crontab：
```bash
chmod +x /var/www/scenic/backup_db.sh
crontab -e
```

添加定时任务（每天凌晨2点备份）：
```
0 2 * * * /var/www/scenic/backup_db.sh
```

## 八、重要注意事项

1. **更新密码和密钥**：
   - 修改`settings.py`中的`SECRET_KEY`
   - 更新MySQL和Redis的密码
   - 修改邮箱配置中的密码

2. **文件权限**：
   - 确保`media`和`static`目录有适当的读写权限
   ```bash
   sudo mkdir -p /var/www/scenic/media
   sudo mkdir -p /var/www/scenic/static
   sudo chown -R www-data:www-data /var/www/scenic/media
   sudo chown -R www-data:www-data /var/www/scenic/static
   sudo chmod -R 755 /var/www/scenic/static
   sudo chmod -R 775 /var/www/scenic/media
   ```

3. **定期更新**：
   - 设置服务器安全更新
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **备份策略**：
   - 定期备份源代码和数据库
   - 考虑使用远程存储保存备份

5. **安全措施**：
   - 配置SSH密钥认证
   - 禁用密码登录
   - 考虑使用fail2ban预防暴力攻击

6. **性能优化**：
   - 配置Redis缓存
   - 启用Nginx压缩
   - 配置浏览器缓存控制

按照以上步骤操作，您的全国景区数据分析及可视化系统应该能够成功部署在Ubuntu云服务器上。此部署方案适用于Ubuntu 20.04 LTS和Ubuntu 22.04 LTS版本。