import logging

import requests
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

def get_balance(key):
    proxies = {}
    base_url = "https://api.openai.com/dashboard/billing/credit_grants"
    try:
        resp = requests.get(base_url, headers={
            'Content-Type': "application/json",
            'Authorization': f"Bearer {key}"
        }, proxies=proxies, timeout=3).json()
    except Exception as e:
        logging.error(e)
        resp = {}
    return resp.get('total_available', -1)


class ChatUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_vip = models.BooleanField(default=False, verbose_name="是否可以使用API接口")
    use_count = models.BigIntegerField(default=0, verbose_name="总计调用次数")
    balance = models.BigIntegerField(default=0, verbose_name="剩余调用次数")

    def __repr__(self):
        return f"<{self.user} api: {self.is_vip}>"


class ApiKey(models.Model):
    """
    值
    有效性
    调用次数
    是否使用
    创建时间
    删除时间
    """
    value = models.CharField(max_length=128, unique=True, verbose_name="api密钥")
    call_count = models.BigIntegerField(default=0, verbose_name="调用次数")
    is_work = models.BooleanField(default=False, verbose_name="是否正在使用使用")
    is_valid = models.BooleanField(default=True, verbose_name="key是否能用")
    created_time = models.DateTimeField(auto_now_add=True)
    edited_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.value}"

    @admin.display(ordering='balance', description="余额")
    def balance(self):
        if self.is_valid:
            return get_balance(self.value)
        else:
            return -1
