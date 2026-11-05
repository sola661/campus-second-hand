from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import re

def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def _login_hint(next_url):
    """未登录访问受限页面跳转登录页时的统一提示语；无来源返回空串（不显示）。"""
    if not next_url:
        return ''
    return '完成登录即可进行更多操作'

def test_base(request):
    return render(request, 'base.html')

@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]{1,20}$', username):
            msg = '用户名必须由1~20位的中文,字母，数字或下划线组成'
            if is_ajax(request):
                return JsonResponse({'code': 400, 'msg': msg})
            messages.error(request, msg)
            return render(request, 'register.html')
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password1):
            msg = '密码必须由8位及以上的数字，字母组成,且字母要同时包含大小写'
            if is_ajax(request):
                return JsonResponse({'code': 400, 'msg': msg})
            messages.error(request, msg)
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            msg = '用户名重复'
            if is_ajax(request):
                return JsonResponse({'code': 400, 'msg': msg})
            messages.error(request, msg)
            return render(request, 'register.html')
        if password1 != password2:
            msg = '两次密码不一致'
            if is_ajax(request):
                return JsonResponse({'code': 400, 'msg': msg})
            messages.error(request, msg)
            return render(request, 'register.html')
        User.objects.create_user(username=username, password=password1)
        if is_ajax(request):
            return JsonResponse({'code': 200, 'msg': '注册成功，请登录'})
        messages.success(request, '注册成功，请登录')
        return redirect('login')

    else:
        return render(request, 'register.html')

@csrf_exempt
def login(request):
    ctx = {'login_hint': _login_hint(request.GET.get('next', ''))}
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = (request.POST.get('password') or '').strip()
        # 用户名/密码格式与注册逻辑保持一致；不匹配按"用户名或密码错误"处理，避免泄露具体原因
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]{1,20}$', username) or \
           not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
            msg = '用户名或密码错误'
            if is_ajax(request):
                return JsonResponse({'code': 400, 'msg': msg})
            messages.error(request, msg)
            return render(request, 'login.html', ctx)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            if is_ajax(request):
                return JsonResponse({'code': 200, 'msg': '登陆成功', 'redirect': '/goods/goods/'})
            messages.success(request, '登陆成功')
            return redirect('/goods/goods/')
        else:
            msg = '用户名或密码错误'
            if is_ajax(request):
                return JsonResponse({'code': 400, 'msg': msg})
            messages.error(request, msg)
            return render(request, 'login.html', ctx)
    else:
        return render(request, 'login.html', ctx)

@require_POST
def logout(request):
    django_logout(request) #收回登录通行证；
    return redirect('/goods/goods/')