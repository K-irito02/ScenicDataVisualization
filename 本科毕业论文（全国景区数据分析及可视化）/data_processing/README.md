# 景区数据处理与分析模块

这个模块负责景区数据的处理、分析和可视化，是景区数据可视化系统的核心后端组件。

## 目录结构

- `ceshi.py` - 用于快速统计MongoDB中特定字段数据分布的测试脚本
- `scripts/` - 包含数据处理和分析的各类脚本
  - `summary-table.py` - 负责汇总数据和创建主要的数据摘要表
  - `comment_handling.py` - 评论数据处理与情感分析模块
  - `scenic_spots.py` - 景区基础信息处理模块
  - `ticket_prices.py` - 票价数据处理模块
  - `open_hours.py` - 开放时间数据处理模块
  - `transport_mode.py` - 交通方式数据处理模块
  - `provinceTraffic_and_trafficAdd.py` - 省级交通数据处理
  - `hierarchy_TicketAnalysis.py` - 景区层次化票价分析
  - `data_integration_Ai.py` - AI辅助的数据整合工具

## 功能概述

### 数据处理流水线

1. **数据采集与存储**：从MongoDB读取原始景区数据
2. **数据清洗与预处理**：对文本数据进行清洗、格式化和标准化
3. **文本分析**：
   - 使用jieba分词进行中文文本分词
   - 基于词典的情感分析
   - 高频词和关键词提取
4. **数据整合**：将处理结果写入MySQL数据库以供前端查询和可视化

### 主要功能模块

#### 评论处理与情感分析 (`comment_handling.py`)

- 使用词典和规则进行情感分析
- 包含积极/消极词典、程度副词、否定词等资源
- 支持评论预处理、分词、情感得分计算
- 提取评论中的高频词和关键词

#### 数据汇总 (`summary-table.py`)

- 整合MongoDB和MySQL中的数据
- 生成景区综合信息表
- 提取关键业务指标(票价、评价、地理位置等)

#### 票价分析 (`ticket_prices.py`)

- 从非结构化文本中提取票价信息
- 分类不同票价类型
- 计算最低票价、平均票价等指标

#### 交通方式处理 (`transport_mode.py`)

- 识别并提取景区交通方式
- 标准化交通方式描述
- 生成交通便利性指标

#### 数据字段统计分析 (`ceshi.py`)

- 用于快速统计MongoDB中特定字段的值分布
- 支持生成JSON格式的统计结果
- 包含注释掉的示例代码，可用于查询缺失字段或特定值的文档

## 使用方法

### 环境要求

- Python 3.7+
- MongoDB 4.0+
- MySQL 5.7+
- 相关Python包：pymongo, pymysql, jieba, numpy等

### 数据库配置

MongoDB和MySQL的连接参数配置在各脚本文件中，主要包括：

```python
# MongoDB配置
MONGO_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'db': 'scenic_area',
    'collection': 'china_attractions_copy'
}

# MySQL配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '你的密码',
    'database': 'scenic_area',
    'charset': 'utf8mb4'
}
```

### 脚本执行顺序

为获得最佳结果，建议按以下顺序执行脚本：

1. `scenic_spots.py` - 处理基础信息
2. `comment_handling.py` - 处理评论和情感分析
3. `ticket_prices.py` - 分析票价信息
4. `open_hours.py` - 处理开放时间
5. `transport_mode.py` - 处理交通方式
6. `summary-table.py` - 生成综合数据表

### 示例

要处理所有景区的评论数据并进行情感分析：

```bash
cd scripts
python comment_handling.py
```

生成数据摘要表：

```bash
cd scripts
python summary-table.py
```

### 快速测试与统计

使用`ceshi.py`脚本可以快速统计MongoDB中某个字段的数据分布：

```bash
# 修改脚本中的field_name变量为你要统计的字段名
python ceshi.py
```

脚本将生成一个JSON文件，包含字段值及其出现次数的统计。

## 数据字典

### 景区摘要表 (summary_table)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 景区ID | INT | 主键 |
| 景区名称 | VARCHAR(255) | 景区名称 |
| 图片URL | TEXT | 景区图片链接 |
| 景区简介 | TEXT | 景区简要描述 |
| 所在省份 | VARCHAR(50) | 省级行政区 |
| 所在城市 | VARCHAR(50) | 地级市 |
| 所在区县 | VARCHAR(50) | 区/县级行政区 |
| 所在街道镇乡 | VARCHAR(100) | 街道/镇/乡级行政区 |
| 经纬度 | VARCHAR(50) | 经纬度坐标 |
| 景区类型及级别 | VARCHAR(255) | 景区分类和等级 |
| 最低票价 | VARCHAR(50) | 最低门票价格 |
| 交通方式 | VARCHAR(255) | 可用交通方式 |
| 评论数量 | INT | 评论总数 |
| 情感倾向 | VARCHAR(10) | 评论整体情感(优/良/中) |
| 情感得分 | FLOAT | 评论情感分析得分 |

## 注意事项

- 数据处理脚本可能需要较长时间运行，尤其是处理大量评论数据时
- 确保MongoDB和MySQL服务在脚本运行前已启动
- 建议在处理大量数据前，先使用小样本数据测试
- 情感分析结果依赖于词典质量，可能需要针对景区领域进行优化 