from urllib.parse import urlencode
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import time
import random

from goods.models import Goods
from .models import Orders


def generate_order_sn():
    return f'ORD{int(time.time())}{random.randint(1000, 9999)}'


def orders_list(request):
    try:
        orders = Orders.objects.all().values('order_sn','price','status','create_time','goods__title','user__username')
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
        if not good.is_active:
            messages.error(request, '该商品已售空')
            return redirect('goods:goods')

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
        order = get_object_or_404(Orders, id=order_id, user=request.user)
        if order.status == 'pending':
            order.status = 'paid'
            order.goods.is_active = False
            order.goods.save()
            order.save()
            return redirect(reverse('orders:my_orders') + '?paid=1')
        return redirect('orders:my_orders')

    user_orders = Orders.objects.filter(user=request.user).order_by('-create_time')
    context = {
        'orders': user_orders,
        'page_title': '我的订单',
    }
    return render(request, 'my_orders.html', context)
