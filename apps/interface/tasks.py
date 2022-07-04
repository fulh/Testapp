from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import ProjectInfo,InterfaceInfo


@shared_task
def add(x, y):
    print("aa")
    return x + y


@shared_task
def mul(x, y):
    return x * y

@shared_task
def case():
    probjectset = ProjectInfo.objects.all().values()
    for projcet in list(probjectset):
        id = projcet['id']
    return id
