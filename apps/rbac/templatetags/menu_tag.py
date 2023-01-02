#!/usr/bin/evn python
# -*-coding:utf-8 -*-
__author__ = "FuLiHua"
from django import template

register=template.Library()

@register.inclusion_tag("rbac/menu.html")
def get_menu(request):
    # 获取当前用户可以放到菜单栏中的权限
    menu_dict = request.session["menu_dict"]
    print("==================================")
    return {"menu_dict":menu_dict}
