import xadmin

from .models import IpAddre,UserProfile





class IpAdmin(object):
    # 显示的列
    list_display = ['ip']


xadmin.site.register(IpAddre,IpAdmin)


