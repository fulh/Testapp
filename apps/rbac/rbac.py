#!/usr/bin/evn python
# -*-coding:utf-8 -*-
__author__ = "FuLiHua"
from rbac.models import Roles,Permission,Menu

def initial_permission(request,user):
    # roles_list = Roles.objects.filter(user__username=user)
    roles_list = user.roles_set.all()
    print(roles_list)

    permission_list = Permission.objects.filter(roles_action__in=roles_list).values('title', 'url', 'action')

    permission_info = Menu.objects.filter(permission_menu__permission__roles_action__in=roles_list).values("title",
                                                                                                           "permission_menu__id",
                                                                                                           "permission_menu__permission__url",
                                                                                                           "permission_menu__permission__action").distinct()

    permission_dict = {}

    for permission in permission_info:
        id = permission["permission_menu__id"]
        if not id in permission_dict:
            permission_dict[id] = {
                "url": [permission["permission_menu__permission__url"]],
                "action": [permission["permission_menu__permission__action"]]
            }
        else:
            permission_dict[id]["url"].append(permission["permission_menu__permission__url"])
            permission_dict[id]["action"].append(permission["permission_menu__permission__action"])
    print(permission_dict)
    request.session["permission_dict"] = permission_dict

    # 生成菜单
    menu_info = Menu.objects.filter(permission_menu__permission__roles_action__in=roles_list).values("id", "title",
                                                                                                     "permission_menu__permission__action",
                                                                                                     "permission_menu__permission__url",
                                                                                                     "permission_menu__title").distinct()
    menu_list = []
    menu_dict = {}
    # 获取生成菜单的权限信息
    for menu in menu_info:
        if menu["permission_menu__permission__action"] == "list":
            menu_list.append(menu)
            # temp = {"permission_title":menu["permission_menu__group__title"],"url":menu["permission_menu__url"]}
            # menu_list.append(temp)
            # menu_dict = {"id":menu["id"],"title":menu["title"],"menu_list":menu_list}

            # menu_list.append((menu["title"],menu["permission_menu__url"]))
            # menu_list.append(menu_dict)
    for permission_m in menu_list:
        if permission_m["id"] in menu_dict:
            menu_dict[permission_m["id"]]["children"].append({
                "title": permission_m["permission_menu__title"],
                "url": permission_m["permission_menu__permission__url"]
            })
        else:
            menu_dict[permission_m["id"]] = {
                "menu_name": permission_m["title"],
                'children': [
                    {
                        "title": permission_m["permission_menu__title"],
                        "url": permission_m["permission_menu__permission__url"]
                    }
                ]
            }
    request.session["menu_dict"] = menu_dict
