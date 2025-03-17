常用Git命令
# Git 常用命令指南

## 初始化和配置

### 初始化Git仓库
```bash
git init
```
在当前目录初始化一个新的Git仓库。

### 配置用户信息
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```
设置全局用户名称和邮箱。

## 基本操作

### 查看当前分支
```bash
git branch
```
列出所有本地分支，并标记当前所在分支。

### 添加文件到暂存区
```bash
git add .
```
将所有更改的文件添加到暂存区。

### 提交更改
```bash
git commit -m "Commit message"
```
提交暂存区的更改，并添加提交信息。

## 远程仓库操作

### 添加远程仓库
```bash
git remote add origin https://github.com/username/repository.git
```
添加一个新的远程仓库。

### 查看当前配置的远程仓库URL
```bash
git remote -v
```
查看所有配置的远程仓库。

### 更新远程仓库URL
```bash
git remote set-url origin https://github.com/username/repository.git
```
更新现有远程仓库的URL。

### 删除远程仓库
```bash
git remote remove origin
```
删除本地仓库中对远程仓库的引用。

## 推送和拉取

### 推送到远程仓库
```bash
git push -u origin master
```
将本地分支推送到远程仓库的 `master` 分支。

### 推送到远程仓库（如果默认分支是 `main`）
```bash
git push -u origin main
```
将本地分支推送到远程仓库的 `main` 分支。

### 拉取远程仓库的更改
```bash
git pull origin master
```
从远程仓库的 `master` 分支拉取更改并合并到本地。

## 分支管理

### 创建新分支
```bash
git branch new-branch
```
创建一个名为 `new-branch` 的新分支。

### 切换到新分支
```bash
git checkout new-branch
```
切换到 `new-branch` 分支。

### 合并分支
```bash
git merge branch-name
```
将 `branch-name` 分支合并到当前分支。

## 状态查看

### 查看当前状态
```bash
git status
```
查看工作目录和暂存区的状态。

### 查看提交历史
```bash
git log
```
查看提交历史记录。