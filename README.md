# 校园二手交易平台

基于 Django 的校园二手物品交易系统，支持商品浏览、分类、发布、订单管理等。

**在线演示：** http://43.138.214.101/goods/goods/

## 技术栈

- Python 3 / Django 5.2
- MySQL
- Nginx + Gunicorn
- HTML / CSS / JavaScript

## 腾讯云部署

项目部署在腾讯云轻量应用服务器（Ubuntu），使用 Nginx 反向代理 + Gunicorn 运行 Django，MySQL 作为数据库。

主要步骤：

1. 服务器安装 Python、MySQL、Nginx
2. 上传代码，配置 `.env`（数据库、`ALLOWED_HOSTS`、`DEBUG=False` 等）
3. `pip install -r requirements.txt`
4. 进行数据库迁移：`python manage.py migrate` 
5. 配置 Gunicorn 系统服务与 Nginx（`/static/`、`/media/`）
