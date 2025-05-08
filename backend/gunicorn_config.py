import multiprocessing
import os
import sys

# 添加应用目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

bind = "127.0.0.1:8001"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
max_requests = 1000
max_requests_jitter = 50
reload = True
daemon = False
accesslog = "/var/www/scenic/backend/logs/gunicorn_access.log"
errorlog = "/var/www/scenic/backend/logs/gunicorn_error.log"
loglevel = "debug"
capture_output = True 