import json
import logging
import time
import typing as t

from django.shortcuts import render, redirect, reverse
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User

from .models import ChatUser, ApiKey
from .gpt import question

# Create your views here.
logger = logging.getLogger('ChatManage.chat')


@login_required()
def index(request: HttpRequest) -> t.Union[JsonResponse]:
    return render(request, "chat/index.html")


@login_required()
def api_v0_chat(request: HttpRequest) -> t.Union[StreamingHttpResponse]:
    if request.method == 'GET':
        return StreamingHttpResponse("拒绝访问")
    profile_user = ChatUser.objects.filter(user=request.user).first()
    if profile_user is None:
        return StreamingHttpResponse("拒绝访问")
    if not profile_user.is_vip:
        return StreamingHttpResponse("正在申请使用中，请等待")
    if profile_user.balance <= 0:
        return StreamingHttpResponse("余额不足")
    body = json.loads(request.body)
    # 从数据库获得API密钥
    api_key = None
    api_key_obj = None
    if api_key is None:
        api_key_obj = ApiKey.objects.filter(is_work=False, is_valid=True).first()
        if api_key_obj is None:
            return StreamingHttpResponse("服务异常！")
        api_key_obj.is_work = True
        api_key = api_key_obj.value
    if api_key is None:
        return StreamingHttpResponse("服务异常！")
    question_list = body.get('question') or []
    if not isinstance(question_list, list) and not question_list:
        return StreamingHttpResponse("请求异常!")
    try:
        if api_key_obj: # 调用次数+1 用户调用次数+1 用户可用次数-1
            pass
        return StreamingHttpResponse(question(question_list, api_key))
    finally:
        if api_key_obj:
            api_key_obj.is_work = False


def g_login(request: HttpRequest):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(reverse('chat:chat'))
        return render(request, "login.html")
    try:
        body = json.loads(request.body)
    except Exception as e:
        return JsonResponse({'to': reverse('chat:g_login'), 'message': "登录失败"})
    username = body.get('username')
    passwd = str(body.get('passwd', '')).strip()
    user = User.objects.filter(username=username).first()
    if user is None:
        return JsonResponse({'to': reverse('chat:g_login'), 'message': "登录失败"})
    if user.check_password(passwd):
        login(request, user)
        return JsonResponse({'to': reverse('chat:chat'), 'message': "登录成功", 'code': 0})
    return JsonResponse({'to': reverse('chat:g_login'), 'message': "登录失败"})


@login_required()
def g_logout(request: HttpRequest):
    logout(request)
    return redirect(reverse('chat:g_login'))


def g_register(request: HttpRequest):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(reverse('chat:chat'))
        return render(request, "register.html")
    try:
        body = json.loads(request.body)
    except Exception as e:
        return JsonResponse({'to': reverse('chat:g_login'), 'message': "登录失败"})
    username = body.get('username')
    passwd = str(body.get('passwd', '')).strip()
    email = str(body.get('email', '')).strip()
    try:
        user = User.objects.create(username=username, email=email)
        user.set_password(passwd)
        user.save()
        return JsonResponse({'to': reverse('chat:g_login'), 'message': "注册成功", 'code': 0})
    except Exception as e:
        return JsonResponse({'to': reverse('chat:g_register'), 'message': "注册失败"})
