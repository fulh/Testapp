# -*- coding: utf-8 -*-
import json
import logging
import time
import uuid

from django.utils.deprecation import MiddlewareMixin
from django_redis import get_redis_connection
from rest_framework import status
from django.shortcuts import render, HttpResponse
from django.core.cache import caches

from django.contrib.auth.models import User
from user.models import UserProfile
from user.models import OnlineUsers
from apps.tools.utils import get_request_browser, get_request_os, get_request_ip,get_ip_address


class OperationLogMiddleware:
    """
    操作日志Log记录
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.operation_logger = logging.getLogger('operation')  # 记录非GET操作日志
        self.query_logger = logging.getLogger('query')  # 记录GET查询操作日志

    def __call__(self, request):
        conn=get_redis_connection('Api_number')
        request.start_time = time.time()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.start_time ))
        try:
            request_body = json.loads(request.body)
        except Exception:
            request_body = dict()
        if request.method == "GET":
            request_body.update(dict(request.GET))
            logger = self.query_logger
        else:
            request_body.update(dict(request.POST))
            logger = self.operation_logger
        # 处理密码, log中密码已******替代真实密码


        for key in request_body:
            if 'password' in key:
                request_body[key] = '******'
        response = self.get_response(request)

        execute_time = round((time.time() - request.start_time),5)
        # response.elapsed.total_seconds()s
        try:
            response_body = response.data
            # 处理token, log中token已******替代真实token值
            if response_body['data'].get('token'):
                response_body['data']['token'] = '******'
        except Exception:
            response_body = dict()

        request_ip = get_request_ip(request)
        log_info = f'[{request.user}@{request_ip} [Request: {request.method} {request.path} {request_body}] ' f'[Response: {response.status_code} {response.reason_phrase} {response_body}]' f'[url_time:{execute_time}]]'
        if response.status_code >= 500:
            logger.error(log_info)
        elif response.status_code >= 400:
            logger.warning(log_info)
        else:
            log_redis = {
                # 'time':f'{timestamp}',
                # 'time':request.start_time,
                'time':str(uuid.uuid4()),
                'user':f'{request.user}',
                'request_ip':request_ip,
                'request':f'[{request.method} {request.path} {request_body}]',
                'Response':f'{response.status_code} {response.reason_phrase} {response_body} ',
                'url_time':execute_time
            }
            # conn.sadd(f'api_url:{request.path}',str(time.time())+':'+log_info)
            # if conn.
            conn.sadd(f'api_url:{request.path}',json.dumps(log_redis))
            # logger.info(log_info)
        return response


# class ResponseMiddleware(MiddlewareMixin):
#     """
#     自定义响应数据格式
#     """
#
#     def process_request(self, request):
#         request.init_time = time.time()
#         return None
#
#     def process_view(self, request, view_func, view_args, view_kwargs):
#         pass
#
#     def process_exception(self, request, exception):
#         pass
#
#     def process_response(self, request, response):
#         execute_time = round((time.time() - request.init_time), 3)
#         if isinstance(response, Response) and response.get('content-type') == 'application/json':
#             if response.status_code >= 400:
#                 msg = '请求失败'
#                 detail = response.data.get('detail')
#                 code = 1
#                 data = {}
#             elif response.status_code == 200 or response.status_code == 201:
#                 msg = '成功'
#                 detail = ''
#                 code = 200
#                 data = response.data
#             else:
#                 return response
#             response.data = {'msg': msg, 'errors': detail, 'code': code, 'data': data,'execute_time':execute_time}
#             response.content = response.rendered_content
#         return response


class OnlineUsersMiddleware(MiddlewareMixin):
    """
    在线用户监测, (采用类心跳机制,10分钟内无任何操作则认为该用户已下线)
    """

    def process_response(self, request, response):
        conn = get_redis_connection('online_user')
        last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        request_ip = get_request_ip(request)
        # redis + django orm 实现在线用户监测
        online_info = {'ip': request_ip, 'browser': get_request_browser(request),
                       'os': get_request_os(request), 'last_time': last_time}
        if request.user.is_authenticated:
            if conn.exists(f'online_user_{request.user.username}_{request_ip}'):
                conn.hset(f'online_user_{request.user.username}_{request_ip}', 'last_time', last_time)
            else:
                conn.hmset(f'online_user_{request.user.username}_{request_ip}', online_info)
                if not OnlineUsers.objects.filter(user=request.user, ip=request_ip).exists():
                    OnlineUsers.objects.create(**{'user': request.user, 'ip': request_ip,'name':request.user.username})
            # key过期后, 使用redis空间通知, 使用户下线
            conn.expire(f'online_user_{request.user.username}_{request_ip}', 2 * 600)
        else:
            if conn.exists(f'online_user_anonyname_{request_ip}'):
                conn.hset(f'online_user_anonyname_{request_ip}', 'last_time', last_time)
            else:
                conn.hmset(f'online_user_anonyname_{request_ip}', online_info)
                if not OnlineUsers.objects.filter(name="anonyname", ip=request_ip).exists():
                    id= UserProfile.objects.get(username="anonyname")
                    OnlineUsers.objects.create(**{'name': "anonyname", 'ip': request_ip,'user':id})
            conn.expire(f'online_user_anonyname__{request_ip}', 2 * 60)
        return response


class IpBlackListMiddleware(MiddlewareMixin):
    """
    IP黑名单校验中间件
    """

    def process_request(self, request):
        request_ip = get_request_ip(request)
        # 在redis中判断IP是否在IP黑名单中/
        conn = get_redis_connection('user_info')
        if conn.sismember('ip_black_list', request_ip):
            from django.http import HttpResponse
            return HttpResponse('IP已被拉入黑名单, 请联系管理员', status=status.HTTP_400_BAD_REQUEST)


class UrlNumeber(MiddlewareMixin):
    """
    统计接口访问次数
    """
    # 日志处理中间件
    def process_request(self, request):
        path = request.path
        if path.endswith('jsi18n/'):
            return None

         # 统计接口访问次数/
        conn = get_redis_connection('url_number')
        # url = ''
        current_url = request.path
        # if "?" in current_url:
        #     url,pandan=str(current_url).split('?')
        # else:
        #     url = current_url
        if conn.exists(f'{current_url}'):
            conn.incr(f'{current_url}', 1)
        else:
            conn.incr(f'{current_url}',1)

        return None


    # def process_response(self, request, response):
    #      # 在redis中判断IP是否在IP黑名单中/
    #     conn = get_redis_connection('url_number')
    #     url = ''
    #     current_url = request.get_full_path()
    #     if "?" in current_url:
    #         url,pandan=str(current_url).split('?')
    #     else:
    #         url = current_url
    #     if conn.exists(f'{url}'):
    #         conn.incr(f'{url}', 1)
    #     else:
    #         conn.incr(f'{url}',1)
    #
    #     return response

class IpLimitMiddleware(MiddlewareMixin):
    def process_request(self,request):
        # ip = request.META.get("REMOTE_ADDR")
        ip = get_request_ip(request)

        # 选择缓存的数据库 redis缓存
        cache = caches['IpLimit']

        # 首先缓存中，根据ip获取数据，假如没有数据，值为空列表 []
        requests = cache.get(ip,[])

        # 如果值存在，且当前时间 - 最后一个时间 > 30 则清洗掉这个值  这里我们插入请求的时间为头插
        while requests and time.time() -  requests[-1] > 30:
            requests.pop()

        # 若没有存在值，则添加，过期时间为30秒，这个过期时间与上面判断的30 保持一致
        requests.insert(0, time.time())
        cache.set(ip, requests, timeout=30)

        # 限制访问次数为 5 次
        print(requests)
        if len(requests) > 5:
            return HttpResponse("请求过于频繁，请稍后重试！")
