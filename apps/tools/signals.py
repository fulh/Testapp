from django.db.models.signals import pre_save, post_delete,post_save,pre_init
from django.dispatch import receiver
from django_redis import get_redis_connection

from apps.user.models import IpAddre


@receiver(pre_save, sender=IpAddre)
def create_update_ip_black_list(sender, **kwargs):
    """
    IP黑名单创建及更新信号处理
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """

    conn = get_redis_connection('user_info')
    instance = kwargs.get('instance')
    created = kwargs.get('created')
    update_fields =  kwargs.get('update_fields')
    using = kwargs.get('using')
    raw = kwargs.get('raw')

    ip_id = instance.id
    if ip_id:
        # 更新IP黑名单, 更新redis黑名单IP
        conn.srem('ip_black_list', IpAddre.objects.get(id=instance.id).ip)
        conn.sadd('ip_black_list', instance.ip)

    else:
        # 新增IP黑名单, 添加redis黑名单IP
        conn.sadd('ip_black_list', instance.ip)


@receiver(post_delete, sender=IpAddre)
def delete_ip_black_list(sender, instance, **kwargs):
    """
    IP黑名单删除时信号处理
    :param sender:
    :param instance:

    :param kwargs:
    :return:
    """
    # 删除IP黑名单时, 删除redis黑名单中的IP
    print(kwargs)
    conn = get_redis_connection('user_info')
    conn.srem('ip_black_list', instance.ip)


@receiver(pre_init,sender=IpAddre)
def init_ip(sender, args,**kwargs):
    print(sender.id)
    print(args)
    print("init",sender,kwargs)


