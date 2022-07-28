import xadmin

from .models import IpAddre,UserProfile





class IpAdmin(object):
	style = "accordion"
	# model_icon = 'fa fa-film'
	list_display = ['ip']




xadmin.site.register(IpAddre,IpAdmin)


