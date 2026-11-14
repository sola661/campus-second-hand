from urllib.parse import urlencode
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import time
import random

from goods.models import Goods
from .models import Orders


def generate_order_sn():
    return f'ORD{int(time.time())}{random.randint(1000, 9999)}'

@login_required #装饰器：确保用户已登录
def orders_list(request):
    try:
        # 订单是私有数据：只返回当前登录用户自己的订单，防止全平台订单被任意拉取,filter()方法用于筛选数据，只能是该用户的订单数据；
        orders = Orders.objects.filter(user=request.user).values('order_sn','price','status','create_time','goods__title','user__username')
        orders_data = []
        for order in orders:
            orders_item = {
                'order_sn': order['order_sn'],
                'price': str(order['price']),
                'status': str(order['status']),
                'create_time': order['create_time'].strftime('%Y-%m-%d %H:%M:%S'),
                'goods': order['goods__title'],
                'user': order['user__username']
            }
            orders_data.append(orders_item)
        return JsonResponse({
            'code': 200,
            'msg': '订单查询成功',
            'data': orders_data,
            'count': len(orders_data)
        },json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg':f'订单查询失败：{str(e)}',
            'data': [],
            'count': 0
        },json_dumps_params={'ensure_ascii': False})


@login_required
def orders(request, good_id):
    good = get_object_or_404(Goods, id=good_id)

    if request.method == 'POST':
        # 卖家不能购买自己发布的商品
        if good.user == request.user:
            messages.error(request, '不能购买自己发布的商品')
            return redirect('goods:category', good_id=good_id)

        if not good.is_active:
            messages.error(request, '该商品已售空')
            return redirect('goods:goods')

        # 同一买家对同一商品已有待付款订单时拒绝重复下单
        if Orders.objects.filter(user=request.user, goods=good, status='pending').exists():
            messages.error(request, '您已有该商品的待付款订单，请到我的订单中继续支付')
            return redirect('orders:my_orders')

        Orders.objects.create(
            order_sn=generate_order_sn(),
            price=good.price,
            status='pending',
            goods=good,
            user=request.user
        )
        return redirect('orders:my_orders')

    return redirect('goods:category', good_id=good_id)


@login_required
def my_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action', 'pay')
        order = get_object_or_404(Orders, id=order_id, user=request.user)

        if action == 'pay' and order.status == 'pending':
            # 付款前检查商品是否还在架（已被他人买走或卖家下架则订单自动取消，防止超卖）
            if not order.goods.is_active:
                order.status = 'cancelled'
                order.save()
                messages.error(request, '该商品已被他人购买或已下架，订单已自动取消')
                return redirect('orders:my_orders')
            order.status = 'paid'
            order.goods.is_active = False
            order.goods.save()
            order.save()
            return redirect(reverse('orders:my_orders') + '?paid=1')

        if action == 'cancel' and order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            messages.success(request, '订单已取消')

        if action == 'receive' and order.status == 'paid':
            order.status = 'success'
            order.save()
            messages.success(request, '交易完成，感谢使用校园二手交易平台')

        return redirect('orders:my_orders')

    # 惰性取消：进入"我的订单"页时，把超过10分钟未支付的订单自动置为已取消
    cutoff = timezone.now() - timedelta(minutes=10)
    expired_orders = Orders.objects.filter(
        user=request.user,
        status='pending',
        create_time__lt=cutoff
    )
    cancelled_titles = []
    for exp in expired_orders:
        exp.status = 'cancelled'
        exp.save()
        cancelled_titles.append(exp.goods.title)
    # 为每笔超时取消的订单追加一次性提示（messages 读一次即消失，不会重复提示）
    for title in cancelled_titles:
        messages.error(request, f'您下单的「{title}」超时未支付，已自动取消')

    user_orders = Orders.objects.filter(user=request.user).order_by('-create_time')
    context = {
        'orders': user_orders,
        'page_title': '我的订单',
    }
    return render(request, 'my_orders.html', context)
