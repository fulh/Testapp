import uuid
import os
import time
from datetime import datetime
from django.conf import settings

from django.db import models
from django.db.models import ImageField,FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.contrib.auth.models import AbstractUser


def upload_user_image_path(instance, filename):
    first,two = filename.split('.')
    return os.path.join(
        'user',
        'head_portrait',
        instance.first_name+instance.last_name+'-'+time.strftime("%Y-%m-%d", time.localtime( time.time()))+'.'+two,
    )

def thumbnail_image_path(instance, filename):
    first,two = filename.split('.')
    return os.path.join(
        'user',
        'thumbnail',
        instance.first_name+instance.last_name+'-'+time.strftime("%Y-%m-%d", time.localtime( time.time()))+'.'+two,
    )

class RImageFiled(ImageField):
    def __init__(self, *args, **kwargs):
        self.max_upload_size = kwargs.pop("max_upload_size", [])
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        file = data.file

        try:
            if file.size > self.max_upload_size:
                raise forms.ValidationError('上传图片不能超过 {}， 当前图片大小 {}。'
                                            .format(filesizeformat(self.max_upload_size),
                                                    filesizeformat(file.size)))
        except AttributeError:
            pass
        return data

class UserProfile(AbstractUser):
    gender_choices = (
        ('male','男'),
        ('female','女')
    )

    nick_name = models.CharField(verbose_name='昵称',max_length=50,default='')
    birthday = models.DateField(verbose_name='生日',null=True,blank=True)
    gender = models.CharField(verbose_name='性别',max_length=10,choices=gender_choices,default='female')
    adress = models.CharField(verbose_name='地址',max_length=100,default='')
    mobile = models.CharField(verbose_name='手机号',max_length=11,null=True,blank=True)
    card_id = models.CharField(verbose_name='身份证',max_length=32,null=True,blank=True)
    image = RImageFiled(upload_to=upload_user_image_path,max_upload_size=56000000,default='image/default.png',max_length=100)
    thumbnail =RImageFiled(upload_to=thumbnail_image_path,max_upload_size=56000,default='image/default.png',max_length=100)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.first_name+self.last_name

    def get_user_info(self):
        # 获取用户信息
        user_info = {
            'id': self.pk,
            'username': self.username,
            'name': self.name,
            'avatar': '/media/' + str(self.image),
            'email': self.email,
            # 'permissions': self._get_user_permissions(),
            # 'department': self.department.name if self.department else '',
            'mobile': '' if self.mobile is None else self.mobile
        }
        return user_info


class IpAddre(models.Model):
    ip = models.GenericIPAddressField(verbose_name='IP',unique=True)

    class Meta:
        db_table = 'monitor_ipblacklist'
        verbose_name = 'IP黑名单'
        verbose_name_plural = verbose_name
        ordering = ['-id']
    def __str__(self):
        return self.ip

class OnlineUsers(models.Model):
    """
    在线用户
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    name = models.CharField(verbose_name='用户名',max_length=32)
    ip = models.GenericIPAddressField(verbose_name='IP')

    objects = models.Manager()

    class Meta:
        db_table = 'monitor_onlineusers'
        verbose_name = '在线用户'
        verbose_name_plural = verbose_name
        ordering = ['-id']
