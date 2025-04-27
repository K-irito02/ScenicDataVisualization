# 迁移问题修复指南

## 问题描述

在执行 `python manage.py migrate` 时遇到以下错误：

```
django.db.utils.OperationalError: (1091, "Can't DROP 'id'; check that column/key exists")
```

这是因为迁移 `scenic_data.0006_remove_culturalreliclevelprice_id_and_more` 试图删除数据库表中不存在的 `id` 列导致的。

## 解决方案

有两种解决方案可供选择：

### 方案1：使用提供的修复脚本（推荐）

我们提供了一个脚本来解决这个问题，请按照以下步骤操作：

1. 确保您在项目的虚拟环境中
   ```bash
   source /var/www/scenic/venv/bin/activate
   ```

2. 进入backend目录
   ```bash
   cd /var/www/scenic/backend
   ```

3. 运行修复脚本，将问题迁移标记为已完成
   ```bash
   python scenic_data/migrations/fake_migrations.py
   ```

4. 尝试再次运行迁移命令
   ```bash
   python manage.py migrate
   ```

### 方案2：手动跳过迁移

如果脚本不起作用，您可以尝试手动跳过这个迁移：

1. 直接在数据库中标记迁移为已完成：
   ```bash
   python manage.py dbshell
   ```

2. 在数据库shell中执行：
   ```sql
   INSERT INTO django_migrations (app, name, applied) 
   VALUES ('scenic_data', '0006_remove_culturalreliclevelprice_id_and_more', NOW());
   ```

3. 退出数据库shell后再次尝试迁移：
   ```bash
   python manage.py migrate
   ```

## 技术说明

问题的根本原因是模型定义和数据库状态不一致：

1. 最初的模型中，这些表被标记为 `managed=False`，表示Django不管理它们的表结构
2. 后来模型被修改，将 `level` 字段设置为主键，导致Django试图删除自动生成的 `id` 主键
3. 但由于表结构是由外部管理的，Django尝试删除的 `id` 列可能根本不存在

我们的修复方案是：
1. 创建新的迁移文件，将这些表标记为Django管理的表 (`managed=True`)
2. 跳过有问题的迁移
3. 直接设置 `level` 字段为主键而不尝试删除 `id` 列

这样可以确保后续迁移正常进行，并且不会再尝试删除不存在的列。 