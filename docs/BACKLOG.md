# BACKLOG

> 只记未解决的问题。修完并验证后从这里删除，搬进 `fixes.md`。
> 每周只允许 3 条处于「进行中」。

字段：`编号 | 一句话 | 位置 | 影响 | 来源 | 状态`
来源：`self`（自己发现）/ `review`（他人或 AI 指出）/ `fixes`（修复时暴露）
状态：`待复现` / `本周` / `排队` / `v3` / `待确认`

## A. 会出事的（正确性 / 安全）

- [ ] **A-01** 支付并发下会超卖 | orders/views.py:89-99 | 两个请求同时支付同一商品都会成功 | 来源:fixes+review | 状态:本周
- [ ] **A-02** 登录/注册/发布接口豁免 CSRF | views.py:22,62、goods/views.py:105 | login CSRF；第三方页面可代用户发布 | 来源:review | 状态:本周
- [ ] **A-03** 下架走 GET | goods/views.py:161 | 任意页面嵌 `<img src>` 即可让已登录用户误下架 | 来源:review | 状态:本周
- [ ] **A-04** `ALLOWED_HOSTS` 默认 `'*'` | settings.py:50 | 任意 Host 头被接受，上线漏配也「能跑」 | 来源:fixes+review | 状态:本周
- [ ] **A-05** `requirements.txt` 非 UTF-8 | 根目录 | 别人 `pip install -r` 可能直接报错 | 来源:review | 状态:本周

## B. 影响观感的（能用，但显得不专业）

- [ ] **B-01** 订单号可能撞唯一约束 | orders/views.py:16 | 同秒同随机数 → IntegrityError 500 | 来源:review | 状态:排队
- [ ] **B-02** `?category=abc` 触发 500 | goods/views.py:99 | `int()` 抛 ValueError | 来源:review | 状态:排队
- [ ] **B-03** 异常原文回传前端 | goods/views.py:79 等 | 泄露 SQL 片段，且掩盖 bug | 来源:review | 状态:排队
- [ ] **B-04** 商品列表无分页 | goods/views.py:54 | 数据量一大就拖垮首页 | 来源:review | 状态:v3
- [ ] **B-05** ngrok / Render 域名硬编码 | settings.py:186-193 | 开发调试残留混在生产配置 | 来源:review | 状态:排队
- [ ] **B-06** 图片存了两份 | goods/*.png + static/images/*.png | 仓库多出约 5MB | 来源:review | 状态:排队
- [ ] **B-07** 两个 `tests.py` 是空壳 | goods/tests.py、orders/tests.py | 没有任何自动化验证 | 来源:review | 状态:排队
- [ ] **B-08** 缺 LICENSE / description / topics | 仓库设置 | 观感与可用性 | 来源:review | 状态:排队
- [ ] **B-09** 重复下单查重有竞态 | orders/views.py:66 | 并发连点仍可能生成两条 pending | 来源:fixes | 状态:排队
- [ ] **B-10** 超时取消逐条 `save()` | orders/views.py:116-128 | 每次进页面 N 次写库；可改 `update()` | 来源:review | 状态:排队

## C. 可以永远不修的（记下来备查）

- [ ] **C-01** 认证逻辑在 project 层，无独立 users app | campus_second_hand/views.py | 结构问题，重做才值得 | 来源:self | 状态:备忘
- [ ] **C-02** 视图里 `try/except` 包住整个查询 | goods/views.py | 吞掉真实异常，应交给日志和 500 页 | 来源:self | 状态:备忘
- [ ] **C-03** 手写 `_load_dotenv` 而非 python-dotenv | settings.py:21-33 | 能用，边界情况少处理（引号、转义） | 来源:self | 状态:备忘

## D. 待确认（我不知道这算不算问题）

- [ ] **D-01** 前后端不分离，CORS 是否多余 | settings.py:174-184 | 需要想清楚留着的理由 | 来源:fixes | 状态:待确认
- [ ] **D-02** `conn_max_age=600` 与 worker 数的关系 | settings.py:111-118 | 持久连接会不会打满 MySQL `max_connections` | 来源:review | 状态:待确认
- [ ] **D-03** WhiteNoise 与 Nginx 静态文件职责重叠 | settings.py:81-85 | 两套都在供静态文件，是否必要 | 来源:review | 状态:待确认

## 已排除（查过，不是问题）

- [x] **X-01** 改订单 id 查看他人订单 | orders/views.py:24,87 | 已有 `filter(user=request.user)` 挡住，实测 404 | 见 fixes.md F-06
