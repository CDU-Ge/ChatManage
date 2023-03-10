from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import Manager


# Create your models here.


class ChatUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_vip = models.BooleanField(default=False, verbose_name="是否可以使用API接口")
    use_count = models.BigIntegerField(default=0, verbose_name="总计调用次数")

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
