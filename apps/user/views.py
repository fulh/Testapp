from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate, logout,login
from rbac.rbac import initial_permission
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json

from django.views import View

from user.models import UserProfile

class LoginBackend(ModelBackend):
	def authenticate(self, request, username=None, password=None, **kwargs):
		try:
			user = UserProfile.objects.get(Q(mobile=username) | Q(email=username)|Q(username=username))
		except UserProfile.DoesNotExist:  # 可以捕获除与程序退出sys.exit()相关之外的所有异常
			return None

		if user.check_password(password) and self.user_can_authenticate(user):
			return user

	def get_user(self, user_id):
		try:
			return UserProfile.objects.get(id=user_id)
		except UserProfile.DoesNotExist:
			return None


class loginauth(View):
	def get(self,request):
		return render(request, "login.html")
	def post(self,request):
		result = {'status': False, 'message': None, 'data': None}
		name = request.POST.get('name')
		password = request.POST.get('password')
		user_info = authenticate(username=name, password=password)
		# user_info = models.UserProfile.objects.filter(username=name, password=password).values( 'nick_name').first()

		if not user_info:
			result['message'] = '用户名或密码错误'
		else:
			result['status'] = True
			login(request, user_info)
			info_json = {"user_info": user_info.nick_name, "email": user_info.email, "username": user_info.username}
			request.session['name'] = info_json
			initial_permission(request,user_info)
		return HttpResponse(json.dumps(result))

@login_required
def index(request):
	return render(request,"index.html")

def logout(request):
    request.session.clear()
    return redirect('/')
