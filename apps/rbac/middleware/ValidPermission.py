#!/usr/bin/evn python
# -*-coding:utf-8 -*-
__author__ = "FuLiHua"

import re

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import  HttpResponse,redirect

class ValidPermission(MiddlewareMixin):
    def process_request(self,request):
        request_path = request.path_info
        valid_list = settings.VALID_LIST

        for Valid_info in valid_list:
            remat = re.match(Valid_info,request_path)
            if remat:
                return None
        permission_list = request.session.get("permission_list",[])
        for permission in permission_list:
            revalue = re.match(permission,request_path)
            if not revalue:
                return redirect("/login/")
            else:
                return None



        request.session.get("permission_list")


