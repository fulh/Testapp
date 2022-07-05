#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author:Fulihua
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Testapp.settings')  # 设置django环境

app = Celery('Testapp')

app.config_from_object('django.conf:settings', namespace='CELERY') #  使用CELERY_ 作为前缀，在settings中写配置

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  # 发现任务文件每个app下的task.py

# 时区
app.conf.timezone = 'Asia/Shanghai'
# 是否使用UTC
app.conf.enable_utc = False

