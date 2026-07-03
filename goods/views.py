import os, io, time, random
from pathlib import Path
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.http import http_date
from PIL import Image
from .models import Category,Goods

def serve_image(request, good_id):
    good = get_object_or_404(Goods, id=good_id)
    if not good.image:
        raise Http404
    path = Path(good.image.path)
    if not path.exists():
        raise Http404
    with open(path, 'rb') as f:
        head = f.read(16)
    sigs = {b'\xff\xd8\xff': 'image/jpeg', b'\x89PNG': 'image/png', b'GIF8': 'image/gif', b'RIFF': 'image/webp'}
    ctype = 'application/octet-stream'
    for sig, ct in sigs.items():
        if head.startswith(sig):
            ctype = ct
            break
    resp = FileResponse(path.open('rb'), content_type=ctype)
    resp['Cache-Control'] = 'public, max-age=86400'
    if 'Content-Disposition' in resp:
        del resp['Content-Disposition']
    return resp

def category_list(request):
    try:
        categories = Category.objects.all().values('name','desc','create_time') #获取到的是一个queryset对象，django特有的；
        category_data = list(categories) #把queryset对象转成list的形式；
        return JsonResponse({
            'code': 200,
            'msg': '分类表查询成功',
            'data': category_data,
            'count': len(category_data),
        },json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'分类查询失败：{str(e)}',
            'data': [],
            'count': 0
        },json_dumps_params={'ensure_ascii': False})

def goods_list(request):
    try:
        goods_query = Goods.objects.all().values('id','title','description','image','price','create_time','is_active','category__name','user__username')
        goods_data = []
        #每次for循环都把大字典里面的每一个键值对都打包成一个大字典装进空列表里面；
        for good in goods_query:
            goods_info = {
                'id': good['id'],
                'title': good['title'],
                'description': good['description'] or '',
                'image': good['image'] or '',
                'price': str(good['price']),
                'create_time': good['create_time'].strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': bool(good['is_active']),
                'category': good['category__name'] or '未分类',
            }
            goods_data.append(goods_info)

        return JsonResponse({
            'code': 200,
            'msg': '商品表查询成功',
            'data': goods_data,
            'count': len(goods_data)
        },json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg':f'商品列表查询失败：{str(e)}',
            'data': [],
            'count': 0
        },json_dumps_params={'ensure_ascii': False})

def goods(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    keyword = request.GET.get('q', '').strip()

    goods_qs = Goods.objects.all().order_by('-create_time')
    if category_id:
        goods_qs = goods_qs.filter(category_id=category_id)
    if keyword:
        goods_qs = goods_qs.filter(title__icontains=keyword)

    context = {
        'goods_list': goods_qs,
        'categories': categories,
        'current_category': int(category_id) if category_id else None,
        'keyword': keyword,
        'page_title': '校园二手交易平台 - 首页'
    }
    return render(request,'goods.html',context)

@csrf_exempt
@login_required
def publish(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        if not title or not price:
            return render(request, 'publish_goods.html', {
                'categories': Category.objects.all(),
                'error': '标题和价格为必填项',
            })

        good = Goods(
            title=title,
            description=description,
            price=price,
            user=request.user,
        )
        if category_id:
            good.category_id = int(category_id)
        if image:
            from django.core.files.base import ContentFile
            img = Image.open(image)
            if img.mode in ('RGBA', 'LA', 'P'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = bg
            buf = io.BytesIO()
            img.save(buf, 'JPEG', quality=80)
            name = f'{int(time.time())}{random.randint(1000,9999)}.jpg'
            good.image.save(name, ContentFile(buf.getvalue()), save=False)
        good.save()

        return redirect(reverse('goods:goods') + '?published=1')

    categories = Category.objects.all()
    return render(request, 'publish_goods.html', {'categories': categories})

@login_required
def deactivate(request, good_id):
    good = get_object_or_404(Goods, id=good_id, user=request.user)
    if good.is_active:
        good.is_active = False
        good.save()
    return redirect('goods:category', good_id=good_id)

def category(request,good_id):
    # 1. 根据商品ID找商品（找不到就返回404，不报错）
    good = get_object_or_404(Goods, id=good_id)
    # 2. 拿到分类名（无分类则显示“未分类”）
    category_name = good.category.name if good.category else "未分类"
    # 3. 传数据给模板（模板后续写，先返回简单响应）
    context = {
        'category_name': category_name,
        'good': good,
        'page_title': f'{category_name}分类页'
    }
    # 先返回一个简单的HTML响应（不用等模板，解决报错）
    return render(request, 'category.html', context)