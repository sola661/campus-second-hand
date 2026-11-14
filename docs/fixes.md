# 修复文档记录

## 索引

| 编号 | 问题 | 当前实现位置 |
|---|---|---|
| F-01 | 未登录跳 404，改为跳登录页 | settings.py:53 |
| F-02 | 登出改为 POST | views.py:93 |
| F-03 | 商品下架后不能再支付 | orders/views.py:89 |
| F-04 | 已下架商品不占首页 | goods/views.py:89 |
| F-05 | 图片上传：表单编码 + 大小 + 转码（含 Nginx 放行） | goods/views.py:122 |
| F-06 | 订单接口只返回本人订单 | orders/views.py:24 |
| F-07 | 同商品不能重复下待付款单 | orders/views.py:66 |
| F-08 | 卖家不能买自己的商品 | orders/views.py:57 |
| F-09 | 订单状态四种 | orders/models.py:8 |
| F-10 | DEBUG 默认关闭 | settings.py:48 |
| F-11 | 时区改为上海 | settings.py:158 |
| F-12 | Bootstrap 改自托管，去掉 CDN 依赖 | static/vendor/、templates/base.html:8 |

---

## 已归档

### F-01 未登录访问受限页面跳 404

- **现象**：未登录点「我的订单」，跳到 `/accounts/login/`，页面不存在
- **原因**：`@login_required` 用默认 `LOGIN_URL`，项目没配这个路由
- **改法**：`settings.py` 设 `LOGIN_URL = '/login/'`；登录页新增提示语（`_login_hint`），带 `?next=` 时提示「完成登录即可进行更多操作」
- **验证**：未登录点「我的订单」→ 302 到 `/login/?next=/orders/my/`，页面显示提示语
- **证据**：settings.py:53、campus_second_hand/views.py:13、templates/login.html:58
- **时间**：2026-07 早期

### F-02 登出改成 POST

- **现象**：`/logout/` 是 GET，任何页面塞一个链接就能把你登出
- **原因**：登出是状态变更，不该用 GET
- **改法**：加 `@require_POST`，模板改成带 CSRF 的表单
- **验证**：GET `/logout/` → 405
- **证据**：campus_second_hand/views.py:93
- **时间**：2026-07 早期

### F-03 商品下架后买家仍能支付

- **现象**：买家下单后卖家把商品下架，买家付款依然成功
- **原因**：支付分支只改订单状态，没校验商品是否还在架
- **改法**：`pay` 分支先查 `order.goods.is_active`，不在架就把订单置为 `cancelled` 并提示已下架
- **验证**：下单 → 卖家下架 → 买家支付，订单变 `cancelled`
- **证据**：orders/views.py:89-99
- **时间**：2026-07 早期

### F-04 已下架/售空商品仍占首页

- **现象**：商品卖出后还留在首页列表
- **原因**：列表查询没过滤 `is_active`
- **改法**：`Goods.objects.filter(is_active=True)`；「我发布的」按在售/下架分组
- **验证**：下架后刷新首页，商品消失
- **证据**：goods/views.py:89
- **时间**：2026-07 早期

### F-05 图片上传

- **现象**：发布页上传图片后收不到文件；超大图片直接存盘
- **原因**：表单缺 `enctype`；服务端没有大小与格式校验
- **改法**：表单加 `enctype="multipart/form-data"`；服务端限 5MB；PIL 打开、统一转 JPEG（quality=80）、透明底铺白；解码失败返回友好错误
- **验证**：传 6MB 图 → 提示超限；传改为 `.jpg` 的文本文件 → 提示格式不支持
- **证据**：templates/publish_goods.html:28、goods/views.py:122-151
- **注意**：线上的 5MB 判断要能生效，前提是 Nginx 放行。Nginx 默认 `client_max_body_size` 只有 1MB，手机拍的照片基本都超，会直接返回 413，请求根本到不了 Django。已在站点配置里设为 `client_max_body_size 8m`：5–8MB 交给 Django 出友好提示，超过 8MB 才由 Nginx 拦截
- **时间**：2026-07 早期（Nginx 补充：2026-11）

### F-06 订单接口能查到所有人订单

- **现象**：`orders_list` 原本返回全表订单
- **原因**：查询没有按当前用户过滤
- **改法**：`filter(user=request.user)`
- **验证**：分别登录 A、B，各自只看到自己的订单
- **证据**：orders/views.py:24
- **时间**：2026-07 早期

### F-07 同一商品可重复下待付款单

- **现象**：连点「购买」会生成多条相同订单
- **原因**：创建订单前没查重
- **改法**：`filter(user, goods, status='pending').exists()` 存在则提示去「我的订单」继续支付
- **验证**：连点两次购买，只生成一条 pending
- **证据**：orders/views.py:66
- **时间**：2026-07 早期

### F-08 卖家能买自己的商品

- **现象**：卖家对自己发布的商品也能下单
- **原因**：下单前没有身份校验
- **改法**：`if good.user == request.user` → `messages.error` 并跳回详情页
- **验证**：用发布商品的账号点购买，提示「不能购买自己发布的商品」
- **证据**：orders/views.py:57
- **时间**：2026-07 早期

### F-09 订单状态从 2 种补到 4 种

- **现象**：只有「待付款/已付款」，取消和完成状态没地方落
- **原因**：模型 `choices` 与业务流程不匹配
- **改法**：`pending / paid / success / cancelled` 四态，视图按状态机流转
- **验证**：下单 → 支付 → 确认收货，状态依次变化；取消后不能再支付
- **证据**：orders/models.py:8
- **时间**：2026-07 早期

### F-10 DEBUG 默认关闭

- **现象**：默认 `DEBUG=True`，报错页会暴露源码、settings、SQL
- **原因**：`settings.py` 生成时默认开启
- **改法**：`DEBUG = os.environ.get('DEBUG', 'False')`，本地在 `.env` 显式开
- **验证**：不设环境变量时访问错误路径 → 返回 500 通用页，无堆栈
- **证据**：settings.py:48
- **时间**：2026-07 早期

### F-11 时区改为上海

- **现象**：时间显示与本地差 8 小时
- **原因**：`TIME_ZONE` 为 UTC
- **改法**：`TIME_ZONE = 'Asia/Shanghai'`，`USE_TZ = True`（存库仍 UTC，展示按上海转换）
- **验证**：新发布商品的 `create_time` 显示为北京时间
- **证据**：settings.py:157-162
- **时间**：2026-07 早期

### F-12 Bootstrap 走外部 CDN，弱网下页面排版错乱

- **现象**：网站闲置一段时间后首次打开首页，栅格、按钮、间距样式丢失，退出重进或刷新后恢复正常。手机端与电脑端均可复现
- **原因**：`base.html` 用 `cdn.jsdelivr.net` 引入 Bootstrap 5.3.2。国内访问该 CDN 常年超时或被重置，空闲后连接与 DNS 变冷，首次请求失败 → CSS 未加载就渲染；刷新时命中缓存或重连成功，所以"坏一次好一次"
- **改法**：把 `bootstrap.min.css`（228KB）与 `bootstrap.bundle.min.js`（79KB）下载到 `static/vendor/`，模板改用 `{% static 'vendor/...' %}`，`settings.py` 恢复 `STATICFILES_DIRS`，由 Nginx 从 `collectstatic` 产物直接提供
- **验证**：断网状态下首页仍完整渲染；`/static/vendor/bootstrap.min.css` 返回 200；首屏少两个外部请求
- **证据**：templates/base.html:8、templates/base.html:390、campus_second_hand/settings.py:185-190、static/vendor/
- **时间**：2026-11

## 原始草稿
问题1：模块3，用户在未登录状态下点击之前收藏的地址时会直接报404错误；在settings.py里添加 /login/，未登录的用户直接会定向到登录界面，并在登陆页面新增了提示语；
问题2：模块3，logout视图前添加require_Post，防止登出；
问题3：模块2，修复了orders/views里订单的逻辑，加入订单状态判断；解决了单一商品面对多个订单出现同时购买成功以及买家创建订单此时卖家下架商品后买家依旧支付成功问题；
问题4：模块4，当发布的商品已售空/下架时，不会再占据商品首页的问题；
5：模块5，图片管理及大小限制问题，enctype = "multipart/form-data";
6：模块6，orders视图里 orders_list 加接口锁，防止查到所有人的订单状况；
7：模块6，同一客户能创建多条相同的商品订单,做了过滤filter;
8：模块6，卖家能买自己的商品，good.user = request.user -- error.message
9：模块6，订单状态由两种（待支付，已支付）改成四种状态，对应数据库模型设计的四种；
10：模块8，debug = true问题，源码泄露，改成false状态；
11：模块8. 时区问题，已改成标准上海时间；
