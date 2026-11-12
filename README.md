# 校园二手交易平台

一个面向校园场景的二手物品交易系统，基于 Django 5.2 + MySQL 开发，部署在腾讯云轻量服务器上。

**在线演示**：http://43.138.214.101/goods/goods/

---

## 项目简介

校园里每年都有大量教材、数码、生活用品在宿舍间流转，但缺少一个只属于本校的交易渠道。这个项目做了一个尽量完整的闭环：卖家发布商品、买家浏览搜索、下单、支付、卖家商品自动下架、买家确认收货。

技术上刻意选择了「服务端渲染 + 少量 JSON 接口」的混合方案，没有做前后端分离——目标是先把一条完整的业务链路跑通，而不是堆技术栈。

---

## 功能

### 买家

- 首页商品列表，支持分类筛选、关键字搜索
- 商品详情页，查看卖家、价格、描述
- 下单、取消订单、支付、确认收货
- 「我的订单」查看全部订单及状态

### 卖家

- 发布商品：标题、描述、价格、分类、图片
- 「我发布的」按在售 / 已下架分组管理
- 一键下架商品
- 商品被支付后自动下架，避免重复售卖

### 通用

- 注册、登录、登出
- 表单校验：用户名格式、密码强度、两次密码一致
- 订单超时未支付自动取消（10 分钟）
- 图片上传：大小限制 5MB，服务端统一转码为 JPEG

---

## 技术栈

| 层次 | 选型 | 说明 |
|---|---|---|
| 后端框架 | Django 5.2 | 服务端渲染为主，辅以 JsonResponse 接口 |
| 数据库 | MySQL 8 | utf8mb4，`USE_TZ=True`，存 UTC 展示上海时间 |
| 数据库驱动 | PyMySQL | 通过 `install_as_MySQLdb()` 适配 |
| 图片处理 | Pillow | 上传即转码、压缩、透明底铺白 |
| WSGI 服务器 | Gunicorn | 生产环境多 worker |
| 反向代理 | Nginx | 静态文件、媒体文件、TLS |
| 静态文件 | WhiteNoise（可选） | 未部署 Nginx 时的兜底方案 |
| 前端 | 原生 HTML / CSS / JS | 模板继承 + CSS 变量 + 手写 SVG 图标 |

---

## 系统架构

```
浏览器
  │
  ▼
Nginx -- /media/   ──→ MEDIA_ROOT（用户上传的商品图）
  │  
  │
  ▼ 
Gunicorn (WSGI)
  │
  ▼
Django
  ├─ Middleware 链（Security → Session → Common → CSRF → Auth → Messages）
  ├─ URL 分发（campus_second_hand/urls.py → goods / orders）
  ├─ View（函数视图）
  └─ Model（Goods / Category / Orders）
       │
       ▼
     MySQL
```

请求从 Nginx 进来，静态和媒体文件由 Nginx 直接返回，剩下的一律转发给 Gunicorn 交给 Django 处理。

---

## 目录结构

```
campus_second_hand/
│
├── manage.py                        Django 命令行入口（runserver / migrate / collectstatic）
├── requirements.txt                 依赖清单，版本全部锁定
├── README.md                        项目说明（本文件）
├── .env                             真实环境变量：数据库密码、SECRET_KEY、DEBUG（不进 git）
├── .env.example                     .env 的模板，只写键名与填法，可直接复制使用
├── .gitignore                       规定哪些文件不进版本库（.env、.venv、media、logs…）
│
├── campus_second_hand/             【项目配置包】不承载业务逻辑
│   ├── __init__.py                  一行 pymysql.install_as_MySQLdb()，让 PyMySQL 冒充 MySQLdb
│   ├── settings.py                  全局配置：INSTALLED_APPS、MIDDLEWARE、DATABASES、
│   │                                静态/媒体目录、TIME_ZONE、LOGGING、生产安全开关
│   ├── urls.py                      总路由表：/admin/ /register/ /login/ /logout/，
│   │                                再把 /goods/ 交给 goods.urls、/orders/ 交给 orders.urls
│   ├── views.py                     注册、登录、登出三个视图（认证逻辑暂放在项目层）
│   ├── wsgi.py                      WSGI 入口，生产环境由 Gunicorn 加载
│   └── asgi.py                      ASGI 入口，当前项目未使用
│
├── goods/                          【商品应用】
│   ├── __init__.py                  空文件，标记 goods 是一个包
│   ├── models.py                    Goods（标题/描述/图片/价格/在售状态/分类/发布者）
│   │                                Category（分类名/描述/创建时间）
│   ├── views.py                     首页列表 goods()、详情 category()、发布 publish()、
│   │                                我发布的 my_goods()、下架 deactivate()、
│   │                                图片输出 serve_image()、两个 JSON 接口
│   ├── urls.py                      商品路由：goods/ category/list/ goods/list/ publish/
│   │                                my/ category/<id>/ deactivate/<id>/ image/<id>/
│   ├── admin.py                     把模型注册进 Django Admin 后台
│   ├── apps.py                      GoodsConfig，应用配置类（settings 里以它注册）
│   ├── tests.py                     自动化测试文件，当前为空壳
│   └── migrations/                  数据库结构变更历史，按顺序执行，不要手改
│       ├── __init__.py              标记为 Python 包
│       ├── 0001_initial.py          建 Goods 表（第一版结构）
│       ├── 0002_category.py         新建 Category 表
│       ├── 0003_alter_goods_category.py     把 Goods.category 改成指向 Category 的外键
│       └── 0004_alter_category_options_alter_goods_options.py   调整两张表的 Meta（表名、中文名）
│
├── orders/                         【订单应用】
│   ├── __init__.py                  空文件，标记 orders 是一个包
│   ├── models.py                    Orders（订单号/价格快照/四状态/商品/买家/创建时间）
│   ├── views.py                     下单 orders()、我的订单 my_orders()（含支付、取消、
│   │                                确认收货、超时自动取消）、订单 JSON 接口 orders_list()
│   ├── urls.py                      订单路由：orders/<good_id>/ my/ orders/list/
│   ├── admin.py                     把 Orders 注册进后台
│   ├── apps.py                      OrdersConfig，应用配置类
│   ├── tests.py                     自动化测试文件，当前为空壳
│   └── migrations/                  数据库结构变更历史
│       ├── __init__.py              标记为 Python 包
│       ├── 0001_initial.py          建 Orders 表（第一版结构）
│       ├── 0002_orders_goods.py     为 Orders 补充商品外键
│       └── 0003_alter_orders_create_time_alter_orders_goods.py  给创建时间加索引、调整商品外键
│
├── templates/                      【模板】Django 模板，服务端渲染
│   ├── base.html                    母版：导航栏、CSS 变量、SVG 图标、block 定义
│   ├── goods.html                   首页：分类导航 + 搜索框 + 商品卡片列表
│   ├── category.html                商品详情页：图片、价格、卖家、下单入口
│   ├── publish_goods.html           发布页表单（enctype="multipart/form-data" 在此）
│   ├── my_goods.html                「我发布的」：在售 / 已下架两组
│   ├── my_orders.html               「我的订单」：订单列表 + 支付 / 取消 / 确认收货按钮
│   ├── login.html                   登录页，含未登录跳转时的提示语
│   └── register.html                注册页，前端做格式校验
│
├── docs/
│   └── fixes.md                     历史问题修复档案：现象 / 原因 / 改法 / 验证 / 时间
│
├── media/                          【运行期生成，不进 git】
│   └── goods/                       用户上传的商品图，PIL 转码后的 .jpg
│                                    换服务器必须单独备份，否则图片全变死链
├── logs/                           【运行期生成，不进 git】
│   └── app.log                      应用日志，5MB 滚动、保留 3 份，线上排错看这里
│
├── .venv/                          虚拟环境（不进 git；Windows 下的不能直接搬到 Linux）
├── .idea/                          PyCharm 配置（不进 git）
├── __pycache__/                    Python 字节码缓存（不进 git，可随时删除）
└── staticfiles/                    collectstatic 的输出目录（不进 git，部署时才生成）
```
---

## 数据模型

### Category（商品分类）

| 字段 | 类型 | 说明 |
|---|---|---|
| name | CharField(50) | 分类名，唯一 |
| desc | CharField(100) | 分类描述，可空 |
| create_time | DateTimeField | 创建时间 |

### Goods（商品）

| 字段 | 类型 | 说明 |
|---|---|---|
| title | CharField(100) | 标题 |
| description | TextField | 描述 |
| image | ImageField | 存 `media/goods/`，可空 |
| price | Decimal(8,2) | 价格 |
| is_active | BooleanField | 是否在售 |
| category | FK → Category | 可空 |
| user | FK → auth.User | 发布者 |
| create_time | DateTimeField | 上架时间，带索引 |

### Orders（订单）

| 字段 | 类型 | 说明 |
|---|---|---|
| order_sn | CharField(50) | 订单号，唯一 |
| price | Decimal(8,2) | 下单时的价格快照 |
| status | CharField(20) | pending / paid / success / cancelled |
| goods | FK → Goods | 下单商品 |
| user | FK → auth.User | 买家 |
| create_time | DateTimeField | 下单时间，带索引 |

---

## 订单状态流转

```
        下单
         │
         ▼
    ┌─────────┐   支付    ┌──────┐   确认收货   ┌─────────┐
    │ pending │ ────────→ │ paid │ ──────────→ │ success │
    └─────────┘           └──────┘             └─────────┘
         │
         │ 主动取消 / 10 分钟未支付 / 商品已下架
         ▼
    ┌───────────┐
    │ cancelled │
    └───────────┘
```

---

## 路由一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/goods/goods/` | 首页，支持 `?category=` `?q=` |
| GET | `/goods/category/<id>/` | 商品详情 |
| GET | `/goods/image/<id>/` | 商品图片输出（带缓存头） |
| GET/POST | `/goods/publish/` | 发布商品（需登录） |
| GET | `/goods/my/` | 我发布的（需登录） |
| GET | `/goods/deactivate/<id>/` | 下架商品（需登录，仅本人） |
| GET/POST | `/orders/orders/<good_id>/` | 下单（POST，需登录） |
| GET/POST | `/orders/my/` | 我的订单 / 支付、取消、确认收货（需登录） |
| GET | `/goods/goods/list/` | 商品列表 JSON |
| GET | `/goods/category/list/` | 分类列表 JSON |
| GET | `/orders/orders/list/` | 我的订单 JSON（仅本人） |
| GET/POST | `/register/` `/login/` `/logout/` | 认证 |

---

## 本地运行

环境要求：Python 3.10+、MySQL 8。

```bash
# 1. 创建数据库
mysql -u root -p -e "CREATE DATABASE campus_second_hand DEFAULT CHARSET utf8mb4;"

# 2. 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# 3. 配置环境变量
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux
# 编辑 .env，填入数据库密码，本地需写 DEBUG=True

# 4. 建表并启动
python manage.py migrate
python manage.py runserver
```

打开 http://127.0.0.1:8000/goods/goods/ 。

---

## 部署

项目部署在腾讯云轻量应用服务器（Ubuntu 22.04），Nginx 反向代理 + Gunicorn + MySQL。

要点：

1. 服务器安装 Python、MySQL、Nginx，创建虚拟环境
2. `git pull` 拉代码（**不要**用 scp 覆盖整个目录，会冲掉服务器上的 `.env`）
3. 配置服务器 `.env`：`DEBUG=False`、`ALLOWED_HOSTS=<公网 IP 或域名>`、独立 `SECRET_KEY`
4. `pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py collectstatic --noinput`
7. 确保 `logs/`、`media/` 对 Gunicorn 运行用户可写
8. 重启服务（本项目服务器上的服务名是 `campus.service`），`nginx -t && systemctl reload nginx`

Nginx 侧三项配置缺一不可：

- `/static/` → `STATIC_ROOT`（collectstatic 的产物）
- `/media/` → `MEDIA_ROOT`（用户上传的图片，目录权限要让 Nginx 可读）
- `client_max_body_size 8m;` —— 默认只有 1MB，手机拍的照片会直接被 413 拦掉，请求根本到不了 Django 那层 5MB 校验

部署后验证：首页返回 200、样式与图片正常、登录发布下单走通、`logs/app.log` 无 ERROR。

---

## 关键实现说明

**图片处理**：上传后在服务端用 Pillow 打开，超过 5MB 直接拒绝，透明底铺白后统一转 JPEG（quality=80），文件名用「时间戳 + 随机数」。这样既避免了原始大图占空间，也防止伪装成图片的文件被直接落盘。

**订单超时取消**：没有引入 Celery，采用惰性策略——进入「我的订单」时顺手把超过 10 分钟未支付的订单置为已取消。优点是零额外依赖，缺点是用户不打开页面就不会取消。

**登录跳转**：`@login_required` 默认跳 `/accounts/login/`，项目没有这个路由，因此在 settings 里指定 `LOGIN_URL = '/login/'`，并在登录页显示提示语。

**日志**：`DEBUG=False` 后报错页不再显示堆栈，因此配置了 `RotatingFileHandler`，5MB 滚动、保留 3 份，线上排错看 `logs/app.log`。

---
