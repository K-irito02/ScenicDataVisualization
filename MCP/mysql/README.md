# MySQL数据库访问工具

这个工具可以访问本地MySQL数据库，包括`hierarchy_ticketanalysis`和`scenic_area`数据库。

## 功能

1. 查看数据库中的所有表
2. 查看指定表的表结构
3. 查看指定表中的数据（可以限制查询记录数量）

## 安装依赖

### Node.js版本

在使用前，请确保已安装Node.js，然后安装必要的依赖：

```bash
npm install mysql2
```

### Python版本

在使用前，请确保已安装Python，然后安装必要的依赖：

```bash
pip install pymysql tabulate
```

## 使用方法

### Node.js版本

#### 查看数据库中的所有表

```bash
node db_operations.js show-tables hierarchy_ticketanalysis
# 或
node db_operations.js show-tables scenic_area
```

#### 查看指定表的结构

```bash
node db_operations.js describe-table hierarchy_ticketanalysis 表名
# 或
node db_operations.js describe-table scenic_area 表名
```

#### 查看表中的数据

```bash
# 默认显示10条记录
node db_operations.js query-table hierarchy_ticketanalysis 表名
# 或指定显示记录数量
node db_operations.js query-table scenic_area 表名 20
```

### Python版本

#### 查看数据库中的所有表

```bash
python db_operations.py show-tables hierarchy_ticketanalysis
# 或
python db_operations.py show-tables scenic_area
```

#### 查看指定表的结构

```bash
python db_operations.py describe-table hierarchy_ticketanalysis 表名
# 或
python db_operations.py describe-table scenic_area 表名
```

#### 查看表中的数据

```bash
# 默认显示10条记录
python db_operations.py query-table hierarchy_ticketanalysis 表名
# 或指定显示记录数量
python db_operations.py query-table scenic_area 表名 20
```

## 配置文件

连接信息存储在`HieTic_and_SceAr.json`文件中，包含两个数据库的连接信息：

- hierarchy_ticketanalysis
- scenic_area

连接使用root用户，默认端口(3306)，密码已在配置文件中设置。 