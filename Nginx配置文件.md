
```
# 域名服务器块，处理HTTP请求，将所有HTTP请求重定向到HTTPS
server {
    listen 80;                                    # 监听80端口（HTTP）
    server_name www.k-irito.online k-irito.online; # 设置服务器名称，包括www和无www的域名版本
    
    # 将HTTP请求重定向到HTTPS
    location / {                                  # 匹配所有路径的请求
        return 301 https://$host$request_uri;     # 返回301永久重定向到HTTPS版本，保留主机名和请求URI
    }
    
    # 允许 Certbot 验证路径，用于SSL证书自动更新
    location ^~ /.well-known/acme-challenge/ {    # 精确匹配Let's Encrypt验证路径
        root /var/www/html;                       # 设置此位置的根目录
        default_type "text/plain";                # 设置默认MIME类型为纯文本
        try_files $uri =404;                      # 尝试查找文件，如果不存在则返回404错误
    }
    
    # 添加favicon.ico处理
    location = /favicon.ico {                     # 精确匹配favicon.ico请求
        alias /var/www/scenic/static/assets/icon.png; # 指向实际图标文件
        access_log off;                           # 关闭访问日志记录
        log_not_found off;                        # 不记录404错误
        expires max;                              # 设置最大过期时间，提高缓存效率
    }
}

# IP地址服务器块，处理HTTP请求，强制所有请求使用HTTPS
server {
    listen 80;                                    # 监听80端口（HTTP）
    server_name 1.15.103.26;                      # 设置服务器IP地址
    
    # 将所有HTTP请求重定向到HTTPS，包括API请求
    location / {                                  # 匹配所有路径的请求
        return 301 https://$host$request_uri;     # 返回301永久重定向到HTTPS版本，保留主机名和请求URI
    }
    
    # 允许 Certbot 验证路径，用于SSL证书自动更新
    location ^~ /.well-known/acme-challenge/ {    # 精确匹配Let's Encrypt验证路径
        root /var/www/html;                       # 设置此位置的根目录
        default_type "text/plain";                # 设置默认MIME类型为纯文本
        try_files $uri =404;                      # 尝试查找文件，如果不存在则返回404错误
    }
    
    # 添加favicon.ico处理
    location = /favicon.ico {                     # 精确匹配favicon.ico请求
        alias /var/www/scenic/static/assets/icon.png; # 指向实际图标文件
        access_log off;                           # 关闭访问日志记录
        log_not_found off;                        # 不记录404错误
        expires max;                              # 设置最大过期时间，提高缓存效率
    }
}

# HTTPS配置 - 域名服务器块
server {
    listen 443 ssl;                               # 监听443端口（HTTPS），启用SSL
    server_name www.k-irito.online k-irito.online; # 设置服务器名称，支持www和无www的域名

    # SSL证书配置
    ssl_certificate /etc/ssl/certs/k-irito.online.pem;      # SSL证书文件路径
    ssl_certificate_key /etc/ssl/private/k-irito.online.key; # SSL密钥文件路径
    
    # 优化SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;                # 仅允许TLS 1.2和1.3协议，提高安全性
    ssl_prefer_server_ciphers on;                 # 优先使用服务器端加密套件
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256; # 设置安全的加密算法
    ssl_session_cache shared:SSL:10m;             # 设置SSL会话缓存大小为10MB
    ssl_session_timeout 10m;                      # 设置SSL会话超时时间为10分钟
    ssl_session_tickets on;                       # 启用SSL会话票证
    ssl_stapling on;                              # 启用OCSP装订，加速SSL握手
    ssl_stapling_verify on;                       # 验证OCSP响应
    
    # 添加HSTS头，提高安全性和减少重定向
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always; # 强制使用HTTPS一年(31536000秒)
    
    # 添加favicon.ico处理
    location = /favicon.ico {                     # 精确匹配favicon.ico请求
        alias /var/www/scenic/static/assets/icon.png; # 指向实际图标文件
        access_log off;                           # 关闭访问日志记录
        log_not_found off;                        # 不记录404错误
        expires max;                              # 设置最大过期时间，提高缓存效率
    }
    
    # 开启gzip压缩，减小传输数据大小
    gzip on;                                      # 启用gzip压缩
    gzip_vary on;                                 # 添加Vary: Accept-Encoding头
    gzip_proxied any;                             # 对所有代理请求启用压缩
    gzip_comp_level 6;                            # 设置压缩级别为6（平衡CPU使用和压缩比率）
    gzip_types text/plain text/css application/json application/javascript application/x-javascript text/xml application/xml application/xml+rss text/javascript; # 要压缩的MIME类型

    root /var/www/scenic/frontend/dist;           # 设置网站根目录
    index index.html;                             # 设置默认索引文件
    
    # 所有前端资源设置缓存，提高加载速度
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { # 匹配静态资源文件
        expires 7d;                               # 设置过期时间为7天
        access_log off;                           # 关闭访问日志
        add_header Cache-Control "public, max-age=604800"; # 设置缓存控制头，604800秒=7天
    }
    
    location / {                                  # 处理根路径请求
        try_files $uri $uri/ /index.html;         # 尝试查找文件，支持单页应用路由
    }

    # 后端API - 使用HTTP，增加超时参数
    location /api/ {                              # 匹配API请求路径
        # 增加超时设置 - 提高CSRF请求的超时时间
        proxy_connect_timeout 30;                 # 连接超时时间30秒
        proxy_read_timeout 300;                   # 读取超时时间300秒
        proxy_send_timeout 300;                   # 发送超时时间300秒
        proxy_buffers 16 64k;                     # 设置缓冲区数量(16)和大小(64k)
        proxy_buffer_size 128k;                   # 设置缓冲区大小为128k
        
        # 增加请求体大小限制
        client_max_body_size 10m;                 # 允许客户端请求体最大10MB，支持上传大文件
        
        # 原有配置 - 代理到后端服务
        proxy_pass http://127.0.0.1:8001;         # 将请求代理到本地8001端口（后端服务）
        proxy_set_header Host $host;              # 设置Host头为原始主机
        proxy_set_header X-Real-IP $remote_addr;  # 设置真实IP头
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # 设置转发IP链
        proxy_set_header X-Forwarded-Proto $scheme; # 设置原始协议（http/https）
        
        # 确保正确传递CSRF cookie - 改进Cookie处理
        proxy_set_header Cookie $http_cookie;     # 设置Cookie头
        proxy_pass_header Set-Cookie;             # 传递Set-Cookie头
        
        # 传递所有请求头
        proxy_pass_request_headers on;            # 确保所有请求头都传递给后端
        
        # 允许跨域请求和Cookie - 修改CORS配置，优化Cookie处理
        add_header Access-Control-Allow-Origin $http_origin always;          # 允许的源
        add_header Access-Control-Allow-Credentials 'true' always;           # 允许凭证（Cookie）
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE' always; # 允许的方法
        add_header Access-Control-Allow-Headers 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,X-CSRFToken' always; # 允许的头
        
        # 处理OPTIONS预检请求 - CORS预检处理
        if ($request_method = 'OPTIONS') {        # 如果是OPTIONS请求
            add_header Access-Control-Allow-Origin $http_origin always;      # 允许的源
            add_header Access-Control-Allow-Credentials 'true' always;       # 允许凭证
            add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE' always; # 允许的方法
            add_header Access-Control-Allow-Headers 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,X-CSRFToken' always; # 允许的头
            add_header Access-Control-Max-Age 1728000;                       # 预检结果缓存20天
            add_header Content-Type 'text/plain charset=UTF-8';              # 内容类型
            add_header Content-Length 0;                                     # 内容长度为0
            return 204;                                                      # 返回204状态码（无内容）
        }
    }
    
    # 特别为CSRF令牌请求单独配置，确保不会超时
    location = /api/csrf-token/ {                 # 精确匹配CSRF令牌请求路径
        proxy_connect_timeout 60;                 # 连接超时时间60秒，更高的超时设置
        proxy_read_timeout 60;                    # 读取超时时间60秒
        proxy_send_timeout 60;                    # 发送超时时间60秒
        
        proxy_pass http://127.0.0.1:8001;         # 代理到后端服务
        proxy_set_header Host $host;              # 设置Host头
        proxy_set_header X-Real-IP $remote_addr;  # 设置真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # 设置转发IP
        proxy_set_header X-Forwarded-Proto $scheme; # 设置原始协议
        
        # 确保正确传递CSRF cookie
        proxy_set_header Cookie $http_cookie;     # 设置Cookie
        proxy_pass_header Set-Cookie;             # 传递Set-Cookie
        
        # 优化的CORS配置
        add_header Access-Control-Allow-Origin $http_origin always;          # 允许的源
        add_header Access-Control-Allow-Credentials 'true' always;           # 允许凭证
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE' always; # 允许的方法
        add_header Access-Control-Allow-Headers 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,X-CSRFToken' always; # 允许的头
    }

    # 管理员接口代理
    location /admin/ {                            # 匹配管理员路径
        # 增加超时设置
        proxy_connect_timeout 30;                 # 连接超时时间30秒
        proxy_read_timeout 300;                   # 读取超时时间300秒
        proxy_send_timeout 300;                   # 发送超时时间300秒
        
        proxy_set_header Host $host;              # 设置Host头
        proxy_set_header X-Real-IP $remote_addr;  # 设置真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # 设置转发IP
        proxy_set_header X-Forwarded-Proto $scheme; # 设置原始协议
        
        # 确保正确传递CSRF cookie
        proxy_set_header Cookie $http_cookie;     # 设置Cookie
        proxy_pass_header Set-Cookie;             # 传递Set-Cookie
        
        proxy_pass http://127.0.0.1:8001;         # 代理到后端服务
    }

    # 媒体文件处理
    location /media/ {                            # 匹配媒体文件路径
        alias /var/www/scenic/media/;             # 指向媒体文件目录
        expires 7d;                               # 设置过期时间为7天
        add_header Cache-Control "public, max-age=604800"; # 设置缓存控制头
    }

    # 静态文件处理
    location /static/ {                           # 匹配静态文件路径
        alias /var/www/scenic/static/;            # 指向静态文件目录
        expires 7d;                               # 设置过期时间为7天
        add_header Cache-Control "public, max-age=604800"; # 设置缓存控制头
    }
}

# HTTPS配置 - IP地址服务器块
server {
    listen 443 ssl;                               # 监听443端口（HTTPS），启用SSL
    server_name 1.15.103.26;                      # 设置服务器IP地址

    # SSL证书配置
    ssl_certificate /etc/ssl/certs/k-irito.online.pem;      # SSL证书文件路径
    ssl_certificate_key /etc/ssl/private/k-irito.online.key; # SSL密钥文件路径
    
    # 优化SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;                # 仅允许TLS 1.2和1.3协议，提高安全性
    ssl_prefer_server_ciphers on;                 # 优先使用服务器端加密套件
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256; # 设置安全的加密算法
    ssl_session_cache shared:SSL:10m;             # 设置SSL会话缓存大小为10MB
    ssl_session_timeout 10m;                      # 设置SSL会话超时时间为10分钟
    ssl_session_tickets on;                       # 启用SSL会话票证
    ssl_stapling on;                              # 启用OCSP装订，加速SSL握手
    ssl_stapling_verify on;                       # 验证OCSP响应
    
    # 添加HSTS头，提高安全性和减少重定向
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always; # 强制使用HTTPS一年
    
    # 添加favicon.ico处理
    location = /favicon.ico {                     # 精确匹配favicon.ico请求
        alias /var/www/scenic/static/assets/icon.png; # 指向实际图标文件
        access_log off;                           # 关闭访问日志
        log_not_found off;                        # 不记录404错误
        expires max;                              # 设置最大过期时间
    }
    
    # 开启gzip压缩，减小传输数据大小
    gzip on;                                      # 启用gzip压缩
    gzip_vary on;                                 # 添加Vary头
    gzip_proxied any;                             # 对所有代理请求启用压缩
    gzip_comp_level 6;                            # 设置压缩级别为6
    gzip_types text/plain text/css application/json application/javascript application/x-javascript text/xml application/xml application/xml+rss text/javascript; # 要压缩的类型

    root /var/www/scenic/frontend/dist;           # 设置网站根目录
    index index.html;                             # 设置默认索引文件
    
    # 所有前端资源设置缓存，提高加载速度
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { # 匹配静态资源文件
        expires 7d;                               # 设置过期时间为7天
        access_log off;                           # 关闭访问日志
        add_header Cache-Control "public, max-age=604800"; # 设置缓存控制头
    }
    
    location / {                                  # 处理根路径请求
        try_files $uri $uri/ /index.html;         # 尝试查找文件，支持单页应用路由
    }

    # 后端API - 使用HTTP，增加超时参数
    location /api/ {                              # 匹配API请求路径
        # 增加超时设置 - 提高CSRF请求的超时时间
        proxy_connect_timeout 30;                 # 连接超时时间30秒
        proxy_read_timeout 300;                   # 读取超时时间300秒
        proxy_send_timeout 300;                   # 发送超时时间300秒
        proxy_buffers 16 64k;                     # 设置缓冲区数量和大小
        proxy_buffer_size 128k;                   # 设置缓冲区大小
        
        # 增加请求体大小限制
        client_max_body_size 10m;                 # 允许客户端请求体最大10MB
        
        # 原有配置 - 代理到后端服务
        proxy_pass http://127.0.0.1:8001;         # 将请求代理到后端
        proxy_set_header Host $host;              # 设置Host头
        proxy_set_header X-Real-IP $remote_addr;  # 设置真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # 设置转发IP
        proxy_set_header X-Forwarded-Proto $scheme; # 设置原始协议
        
        # 确保正确传递CSRF cookie - 改进Cookie处理
        proxy_set_header Cookie $http_cookie;     # 设置Cookie
        proxy_pass_header Set-Cookie;             # 传递Set-Cookie
        
        # 传递所有请求头
        proxy_pass_request_headers on;            # 确保所有请求头都传递
        
        # 允许跨域请求和Cookie - 修改CORS配置，优化Cookie处理
        add_header Access-Control-Allow-Origin $http_origin always;          # 允许的源
        add_header Access-Control-Allow-Credentials 'true' always;           # 允许凭证
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE' always; # 允许的方法
        add_header Access-Control-Allow-Headers 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,X-CSRFToken' always; # 允许的头
        
        # 处理OPTIONS预检请求 - CORS预检处理
        if ($request_method = 'OPTIONS') {        # 如果是OPTIONS请求
            add_header Access-Control-Allow-Origin $http_origin always;      # 允许的源
            add_header Access-Control-Allow-Credentials 'true' always;       # 允许凭证
            add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE' always; # 允许的方法
            add_header Access-Control-Allow-Headers 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,X-CSRFToken' always; # 允许的头
            add_header Access-Control-Max-Age 1728000;                       # 预检结果缓存时间
            add_header Content-Type 'text/plain charset=UTF-8';              # 内容类型
            add_header Content-Length 0;                                     # 内容长度
            return 204;                                                      # 返回204状态码
        }
    }
    
    # 特别为CSRF令牌请求单独配置，确保不会超时
    location = /api/csrf-token/ {                 # 精确匹配CSRF令牌请求路径
        proxy_connect_timeout 60;                 # 连接超时时间60秒
        proxy_read_timeout 60;                    # 读取超时时间60秒
        proxy_send_timeout 60;                    # 发送超时时间60秒
        
        proxy_pass http://127.0.0.1:8001;         # 代理到后端
        proxy_set_header Host $host;              # 设置Host头
        proxy_set_header X-Real-IP $remote_addr;  # 设置真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # 设置转发IP
        proxy_set_header X-Forwarded-Proto $scheme; # 设置原始协议
        
        # 确保正确传递CSRF cookie
        proxy_set_header Cookie $http_cookie;     # 设置Cookie
        proxy_pass_header Set-Cookie;             # 传递Set-Cookie
        
        # 优化的CORS配置
        add_header Access-Control-Allow-Origin $http_origin always;          # 允许的源
        add_header Access-Control-Allow-Credentials 'true' always;           # 允许凭证
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE' always; # 允许的方法
        add_header Access-Control-Allow-Headers 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,X-CSRFToken' always; # 允许的头
    }

    # 管理员接口代理
    location /admin/ {                            # 匹配管理员路径
        # 增加超时设置
        proxy_connect_timeout 30;                 # 连接超时时间30秒
        proxy_read_timeout 300;                   # 读取超时时间300秒
        proxy_send_timeout 300;                   # 发送超时时间300秒
        
        proxy_set_header Host $host;              # 设置Host头
        proxy_set_header X-Real-IP $remote_addr;  # 设置真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # 设置转发IP
        proxy_set_header X-Forwarded-Proto $scheme; # 设置原始协议
        
        # 确保正确传递CSRF cookie
        proxy_set_header Cookie $http_cookie;     # 设置Cookie
        proxy_pass_header Set-Cookie;             # 传递Set-Cookie
        
        proxy_pass http://127.0.0.1:8001;         # 代理到后端
    }

    # 媒体文件处理
    location /media/ {                            # 匹配媒体文件路径
        alias /var/www/scenic/media/;             # 指向媒体文件目录
        expires 7d;                               # 设置过期时间为7天
        add_header Cache-Control "public, max-age=604800"; # 设置缓存控制头
    }

    # 静态文件处理
    location /static/ {                           # 匹配静态文件路径
        alias /var/www/scenic/static/;            # 指向静态文件目录
        expires 7d;                               # 设置过期时间为7天
        add_header Cache-Control "public, max-age=604800"; # 设置缓存控制头
    }
}
```
