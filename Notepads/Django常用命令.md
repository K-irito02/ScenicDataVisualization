# Django 常用命令

## 1. 创建虚拟环境

```bash
python -m venv myenv
```

**用途**：创建一个名为`myenv`的虚拟环境。

**注意事项**：确保在项目目录下运行此命令，以便虚拟环境与项目相关联。

## 2. 激活虚拟环境

### 在Windows上

```bash
venv\Scripts\activate
```

### 在macOS和Linux上

```bash
source myenv/bin/activate
```

**用途**：激活虚拟环境，使其成为当前终端会话的Python环境。

**注意事项**：激活后，终端提示符会显示虚拟环境的名称，表示已成功激活。

## 3. 创建Django项目

```bash
django-admin startproject myproject
```

**用途**：创建一个新的Django项目，名为`myproject`。

**注意事项**：确保在合适的目录下运行此命令，以便项目文件存放在正确的位置。

## 4. 创建Django应用

```bash
python manage.py startapp myapp
```

**用途**：在现有的Django项目中创建一个新的应用，名为`myapp`。

**注意事项**：在项目的根目录下运行此命令，并在`settings.py`中将新应用添加到`INSTALLED_APPS`。

## 5. 运行开发服务器

```bash
python manage.py runserver
```

**用途**：启动Django的开发服务器，默认在`http://127.0.0.1:8000/`运行。

**注意事项**：确保数据库迁移已完成，并且没有其他程序占用8000端口。

## 6. 创建数据库迁移

```bash
python manage.py makemigrations
```

**用途**：根据模型的更改生成数据库迁移文件。

**注意事项**：在更改模型后运行此命令，以便生成相应的迁移文件。

## 7. 应用数据库迁移

```bash
python manage.py migrate
```

**用途**：将迁移应用到数据库，更新数据库结构。

**注意事项**：在生成迁移文件后运行此命令，以确保数据库结构与模型同步。

## 8. 创建超级用户

```bash
python manage.py createsuperuser
```

**用途**：创建一个可以访问Django管理后台的超级用户。

**注意事项**：需要提供用户名、电子邮件和密码。确保密码足够强。

## 9. 打开Django shell

```bash
python manage.py shell
```

**用途**：打开一个交互式Python shell，预加载Django项目的环境。

**注意事项**：可以在shell中直接操作Django模型和数据库。

## 10. 检查项目错误

```bash
python manage.py check
```

**用途**：检查项目中的错误和潜在问题。

**注意事项**：定期运行此命令以确保项目的健康状态。