# 校园二手交易平台

基于 Django 的校园二手物品交易系统，支持商品浏览、分类、发布、订单管理等。

## 技术栈

- Python 3 / Django 5.2
- MySQL
- HTML / CSS / JavaScript

## 本地运行

```bash
pip install -r requirements.txt
```

复制 `.env.example` 为 `.env`，填写 MySQL 密码：

```bash
copy .env.example .env
```

创建数据库后执行迁移并启动：

```bash
python manage.py migrate
python manage.py runserver
```

浏览器访问：http://127.0.0.1:8000

## 说明

本项目为课程/竞赛作品，数据库配置通过环境变量读取，请勿将 `.env` 提交到 Git。
