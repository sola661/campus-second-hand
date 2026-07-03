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

## Render 在线部署

1. 在 [Render](https://render.com) 创建免费 PostgreSQL 数据库
2. 创建 Web Service，连接 GitHub 仓库 `campus-second-hand`
3. 配置：
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn campus_second_hand.wsgi:application`
4. 环境变量：
   - `DATABASE_URL`：从 PostgreSQL 自动关联
   - `SECRET_KEY`：随机字符串
   - `DEBUG`：`False`
   - `PYTHON_VERSION`：`3.12.0`

本地仍用 MySQL（`.env`），线上用 PostgreSQL（`DATABASE_URL`）。
