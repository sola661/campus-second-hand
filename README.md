# 校园二手交易平台

基于 Django 的校园二手物品交易系统，支持商品浏览、分类、发布、订单管理等。

**在线演示：** http://43.138.214.101/goods/goods/

## 技术栈

- Python 3 / Django 5.2
- MySQL
- Nginx + Gunicorn
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

## 腾讯云部署

项目部署在腾讯云轻量应用服务器（Ubuntu），使用 Nginx 反向代理 + Gunicorn 运行 Django，MySQL 作为数据库。

主要步骤：

1. 服务器安装 Python、MySQL、Nginx
2. 上传代码，配置 `.env`（数据库、`ALLOWED_HOSTS`、`DEBUG=False` 等）
3. `pip install -r requirements.txt`
4. `python manage.py migrate` 与 `python manage.py collectstatic`
5. 配置 Gunicorn 系统服务与 Nginx（`/static/`、`/media/`）

本地开发与线上均使用 MySQL，通过 `.env` 配置连接信息。
