from django.shortcuts import render
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import UserProfile

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
