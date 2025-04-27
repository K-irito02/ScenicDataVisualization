## 一、服务器环境准备

### 1. 安装基础工具
```bash
sudo yum update -y
sudo yum install -y git wget vim epel-release
sudo yum install -y gcc gcc-c++ make
```

### 2. 安装Python环境
```bash
# 安装Python开发工具
sudo yum install -y python3 python3-devel python3-pip

# 更新pip
sudo pip3 install --upgrade pip
```

### 3. 安装MySQL
```bash
# 添加MySQL仓库
sudo rpm -Uvh https://repo.mysql.com/mysql80-community-release-el7-3.noarch.rpm
sudo yum install -y mysql-server

# 启动MySQL并设置开机自启
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 获取临时密码
sudo grep 'temporary password' /var/log/mysqld.log
# ​​使用临时密码登录​​
# mysql -u root -p
# 粘贴临时密码（密码不会显示，输入后按回车）。
# ​​立即修改密码​​
# ALTER USER 'root'@'localhost' IDENTIFIED BY '你的新密码';
# 新密码需满足 MySQL 8.0 的复杂度要求（大小写字母+数字+符号）。


# 配置MySQL安全设置
sudo mysql_secure_installation
```
<!-- ​​验证当前 root 密码​​（首次需输入临时密码）：
Enter password for user root: [输入临时密码]
​​设置新密码​​：
New password: [输入新密码]
Re-enter new password: [确认密码]
​​移除匿名用户​​：
Remove anonymous users? [Y/n] y
​​禁止 root 远程登录​​：
Disallow root login remotely? [Y/n] y
​​删除测试数据库​​：
Remove test database and access to it? [Y/n] y
​​重载权限表​​：
Reload privilege tables now? [Y/n] y -->

<!-- [root@VM-4-15-centos .ssh]# sudo mysql_secure_installation

Securing the MySQL server deployment.

Enter password for user root: 

The existing password for the user account root has expired. Please set a new password.

New password: 

Re-enter new password: 
The 'validate_password' component is installed on the server.
The subsequent steps will run with the existing configuration
of the component.
Using existing password for root.

Estimated strength of the password: 100 
Change the password for root ? ((Press y|Y for Yes, any other key for No) : y

New password: 

Re-enter new password: 

Estimated strength of the password: 100 
Do you wish to continue with the password provided?(Press y|Y for Yes, any other key for No) : y
By default, a MySQL installation has an anonymous user,
allowing anyone to log into MySQL without having to have
a user account created for them. This is intended only for
testing, and to make the installation go a bit smoother.
You should remove them before moving into a production
environment.

Remove anonymous users? (Press y|Y for Yes, any other key for No) : y
Success.


Normally, root should only be allowed to connect from
'localhost'. This ensures that someone cannot guess at
the root password from the network.

Disallow root login remotely? (Press y|Y for Yes, any other key for No) : y
Success.

By default, MySQL comes with a database named 'test' that
anyone can access. This is also intended only for testing,
and should be removed before moving into a production
environment.


Remove test database and access to it? (Press y|Y for Yes, any other key for No) : y
 - Dropping test database...
Success.

 - Removing privileges on test database...
Success.

Reloading the privilege tables will ensure that all changes
made so far will take effect immediately.

Reload privilege tables now? (Press y|Y for Yes, any other key for No) : y
Success.

All done!  -->

### 4. 安装Redis
```bash
sudo yum install -y redis

# 启动Redis并设置开机自启
sudo systemctl start redis
sudo systemctl enable redis
```

### 5. 安装Node.js环境（用于前端构建）
```bash
# 1. 移除所有nodejs仓库
sudo rm -f /etc/yum.repos.d/nodesource*.repo

# 2. 清除缓存
sudo yum clean all
sudo rm -rf /var/cache/yum

# 1. 安装NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# 2. 加载NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 3. 安装Node.js 16 Centos 7的glibc版本为2.17，若安装的Node.js版本太高，不支持
nvm install 16

# 4. 确认版本
node -v

# 验证安装
node -v
npm -v
```

### 6. 安装Nginx
```bash
sudo yum install -y nginx

# 启动Nginx并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 二、后端部署准备

### 1. 创建项目目录
```bash
mkdir -p /var/www/scenic
cd /var/www/scenic
```

### 2. 创建虚拟环境
```bash
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
```

### 3. 上传后端代码
将本地`backend`目录上传到服务器的`/var/www/scenic/backend`目录
（可以使用SCP、FTP或Git方式上传）
# 从GitHub拉取特定分支的backend文件夹
# 1. 确保安装了git
sudo yum install -y git

# 2. 导航到目标父目录
sudo mkdir -p /var/www/scenic
cd /var/www/scenic

# 3. 克隆特定分支
git clone -b lite_version --single-branch https://github.com/K-irito02/ScenicDataVisualization.git temp_repo

# 使用Token进行Git操作 克隆仓库时使用格式：
git clone https://<你的token>@github.com/用户名/仓库名.git

# 4. 移动backend文件夹到正确位置
mv temp_repo/backend .

# 5. 删除临时仓库目录
rm -rf temp_repo

# 6. 设置适当的权限
# 正确的CentOS命令，在CentOS系统上，Nginx默认使用nginx用户和组
sudo chown -R nginx:nginx backend
sudo chmod -R 755 backend

# 安装必要的 SELinux 管理工具
运行以下命令安装：
sudo yum install policycoreutils-python
# 设置正确的SELinux上下文（如果您的系统启用了SELinux）
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/scenic/backend(/.*)?"
sudo restorecon -Rv /var/www/scenic/backend

# 为特定目录设置写入权限
sudo find /var/www/scenic/backend/uploads -type d -exec chmod 775 {} \;
sudo find /var/www/scenic/backend/logs -type d -exec chmod 775 {} \;

# 如果后端需要写入权限（例如上传文件或日志），您可能需要：
sudo mkdir -p /var/www/scenic/backend/uploads
sudo mkdir -p /var/www/scenic/backend/logs
# 为特定目录设置写入权限
sudo find /var/www/scenic/backend/uploads -type d -exec chmod 775 {} \;
sudo find /var/www/scenic/backend/logs -type d -exec chmod 775 {} \;

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
vim settings.py
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
```

### 6. 配置MySQL数据库
```bash
mysql -u root -p
```

```sql
CREATE DATABASE scenic_area CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'scenic_user'@'localhost' IDENTIFIED BY '设置一个强密码';
GRANT ALL PRIVILEGES ON scenic_area.* TO 'scenic_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 7. 数据库迁移
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
sudo vim /etc/systemd/system/scenic-gunicorn.service
```

添加以下内容：
```
[Unit]
Description=Scenic Gunicorn Daemon
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/scenic/backend
ExecStart=/var/www/scenic/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 wsgi:application

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start scenic-gunicorn
sudo systemctl enable scenic-gunicorn
```

## 三、前端部署准备

### 1. 上传前端代码
将本地`forward/my-forward`目录上传到服务器的`/var/www/scenic/frontend`目录

### 2. 修改前端API配置
```bash
vim /var/www/scenic/frontend/.env
```

修改为：
```
VITE_API_BASE_URL=https://你的域名 # 或 http://你的服务器IP
```

### 3. 安装前端依赖
```bash
cd /var/www/scenic/frontend
npm install
```

### 4. 构建前端项目
```bash
npm run build
```
构建后的文件将位于`dist`目录

## 四、Nginx配置

### 1. 创建Nginx配置文件
```bash
sudo vim /etc/nginx/conf.d/scenic.conf
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

### 2. 测试并重新加载Nginx配置
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 五、防火墙配置

### 开放必要的端口
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 六、HTTPS配置（可选但推荐）

### 1. 安装Certbot
```bash
sudo yum install -y certbot python3-certbot-nginx
```

### 2. 获取并配置SSL证书
```bash
sudo certbot --nginx -d 你的域名
```

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
vim /var/www/scenic/backup_db.sh
```

添加以下内容：
```bash
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/www/backups"
mkdir -p $BACKUP_DIR
mysqldump -u scenic_user -p密码 scenic_area > "$BACKUP_DIR/scenic_area_$TIMESTAMP.sql"
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
   sudo chown -R nginx:nginx /var/www/scenic/media
   sudo chown -R nginx:nginx /var/www/scenic/static
   ```

3. **定期更新**：
   - 设置服务器安全更新
   ```bash
   sudo yum-config-manager --enable updates
   sudo yum -y update
   ```

4. **备份策略**：
   - 定期备份源代码和数据库
   - 考虑使用远程存储保存备份

按照以上步骤操作，您的全国景区数据分析及可视化系统应该能够成功部署在CentOS云服务器上。如需进一步优化，可考虑配置Redis缓存、启用内容压缩和实施更严格的安全措施。
