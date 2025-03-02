# 马蜂窝全国景点爬虫

这是一个基于Scrapy和Selenium的马蜂窝全国景点爬虫，用于爬取马蜂窝网站上的全国各地景点信息。爬虫使用Redis数据库存储URL和数据，支持分布式部署。

## 功能特点

- 爬取马蜂窝网站上的全国各地景点信息
- 支持分布式部署，可以同时运行多个爬虫实例
- 使用Redis数据库存储URL和数据，避免重复爬取
- 支持断点续爬，可以随时停止和恢复爬取
- 支持导出数据为JSON或CSV格式

## 环境要求

- Python 3.6+
- Redis 5.0+
- Scrapy 2.5+
- Selenium 4.0+
- Microsoft Edge浏览器及对应版本的EdgeDriver

## 安装依赖

```bash
pip install scrapy selenium redis
```

## 配置说明

### 爬虫配置

爬虫的主要配置在`settings_distributed.py`文件中，包括：

- `USER_AGENT`：浏览器标识
- `CONCURRENT_REQUESTS`：并发请求数
- `DOWNLOAD_DELAY`：下载延迟
- `COOKIES_ENABLED`：是否启用Cookie
- `DOWNLOADER_MIDDLEWARES`：下载中间件配置
- `ITEM_PIPELINES`：数据管道配置

### Redis配置

爬虫使用Redis数据库存储URL和数据，需要在启动爬虫时指定Redis服务器地址和密码。

## 使用方法

### 启动爬虫

使用`run_db_crawler.py`脚本启动爬虫：

```bash
python run_db_crawler.py --spider china_attractions_db --master --task-type all --redis-host localhost --monitor
```

参数说明：

- `--spider`：爬虫名称，可选值为`beijing_attractions_db`或`china_attractions_db`
- `--master`：是否为主节点，主节点负责初始化URL队列
- `--task-type`：任务类型，可选值为`all`、`cities`、`list`或`detail`
  - `all`：执行所有任务
  - `cities`：只爬取城市列表
  - `list`：只爬取景点列表
  - `detail`：只爬取景点详情
- `--redis-host`：Redis服务器地址
- `--monitor`：是否监控Redis数据库状态

### 分布式部署

可以在多台机器上同时运行爬虫，实现分布式爬取：

1. 在主节点上启动爬虫：

```bash
python run_db_crawler.py --spider china_attractions_db --master --task-type all --redis-host localhost --monitor
```

2. 在从节点上启动爬虫：

```bash
python run_db_crawler.py --spider china_attractions_db --task-type all --redis-host 主节点IP --node-id node2 --monitor
```

### 导出数据

使用`export_data.py`脚本导出数据：

```bash
python export_data.py --data-type china --format json --export-cities
```

参数说明：

- `--data-type`：要导出的数据类型，可选值为`beijing`、`china`或`city`
  - `beijing`：导出北京景点数据
  - `china`：导出全国景点数据
  - `city`：导出指定城市的景点数据
- `--format`：输出文件格式，可选值为`json`或`csv`
- `--export-cities`：是否导出城市数据（仅当`--data-type=china`时有效）
- `--city-id`：要导出的城市ID（仅当`--data-type=city`时有效）
- `--output`：输出文件路径

## 数据结构

### 城市数据

```json
{
  "name": "城市名称",
  "link": "城市链接",
  "city_id": "城市ID",
  "attractions_list_url": "景点列表页URL"
}
```

### 景点数据

```json
{
  "name": "景点名称",
  "poi_id": "景点ID",
  "link": "景点链接",
  "city": "所在城市",
  "city_id": "城市ID",
  "score": "评分",
  "image": "图片URL",
  "summary": "简介",
  "transport": "交通信息",
  "ticket": "门票信息",
  "opening_hours": "开放时间",
  "location": "位置信息",
  "comments": ["评论1", "评论2", ...]
}
```

## 注意事项

1. 爬虫使用Selenium模拟浏览器访问，需要安装Microsoft Edge浏览器及对应版本的EdgeDriver
2. 爬虫默认使用Redis数据库存储URL和数据，需要先启动Redis服务器
3. 爬虫默认限制每个城市最多爬取10页景点列表，可以在代码中修改
4. 爬虫默认使用分布式部署，可以同时运行多个爬虫实例
5. 爬虫默认使用Redis密码为`3143285505`，可以在代码中修改

## 常见问题

1. **爬虫无法启动**：检查Redis服务器是否正常运行，检查EdgeDriver是否安装正确
2. **爬虫运行缓慢**：可能是网络问题或者反爬机制，可以尝试增加下载延迟
3. **爬虫无法获取数据**：可能是网页结构发生变化，需要更新爬虫代码
4. **Redis连接失败**：检查Redis服务器地址和密码是否正确

## 更新日志

- 2023-03-02：初始版本发布，支持爬取马蜂窝网站上的全国各地景点信息 