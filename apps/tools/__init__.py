import re
import json
# from jsonpath import jsonpath
from loguru import logger
import demjson
from time import sleep

from interface.views import request_case
from interface.models import Pathurl, ProjectInfo, CaseInfo, InterfaceInfo, CaseSuiteRecord

def rep_expr(url,dic):
	"""
	转换变量，把${user}根据变量进行转换
	http://www.ysqorz.top/api/private/v1/${user}
	转换成：
	http://www.ysqorz.top/api/private/v1/fulh
	param url传入的原始字符歘
	param dic 全局变量，从全局变量中获取要替换的值
	"""

	for ctt in re.findall(r'{(\w+)', url):
		try:
			url = url.replace("${" + ctt + "}", dic[ctt])
		except Exception as e:
			logger.error(f'提取不到内容，丢给你一个错误！{e}')
			# url = None
	return url


def create_case_info(*args, **kwargs):
	CaseSuiteRecord.objects.create(**kwargs)

def execute(id,dic,regular_result):
	for item in dic:
		case_id = item["id"]
		case_group_id =item["case_group_id"]
		request_mode = item["request_mode"]
		interface_url = item["interface_url"]
		body_type = item["body_type"]
		request_body = item["request_body"]
		request_head = item["request_head"]
		request_parameter = item["request_parameter"]
		expected_result = item["expected_result"]
		response_assert = item["response_assert"]
		regular_expression = item["regular_expression"]
		regular_variable = item["regular_variable"]
		regular_template = item["regular_template"]
		# actual_result = item["actual_result"]
		wait_time = item["wait_time"]

		if "$" in interface_url:
			interface_url = rep_expr(interface_url, regular_result)

		if "$" in request_parameter:
			request_parameter = rep_expr(request_parameter, regular_result)

		if "$" in request_head:
			request_head = rep_expr(request_head, regular_result)

		if "$" in request_body:
			request_body = rep_expr(request_body, regular_result)

		if "$" in expected_result:
			expected_result = rep_expr(expected_result, regular_result)

		if body_type == "x-www-form-urlencoded":
			pass
		elif body_type == "json":
			request_body = demjson.decode(request_body)
		# 等价于json.loads()反序列化

		# 根据获取到每天测试用例，发送request请求
		response = request_case(request_mode, interface_url, request_body, request_head, request_parameter)

		if regular_expression == "开启" and regular_variable is not None:
			"""					
			如果正则表达式开启，并且变量名不为空
			param regular_template 正则表达式
			param response.text 返回的结果
			根据表达式，提取变量值，赋值给全局变量regular_result
			"""
			regular_result[regular_variable] = re.findall(regular_template, response.text)[0]

		result_code = response.status_code
		# 实际的响应代码
		result_text = response.text
		# 实际的响应文本

		# 根据结果判断，插入对应结果到测试结果列表中
		result = {'case_suite_record_id': int(case_group_id), 'test_case_id': case_id, 'request_data': request_body,
		          'response_code': result_code, 'actual_result': result_text, 'interface_url': interface_url,
		          "request_parameter": request_parameter, "request_body": request_body, "new_case": 1,
		          'execute_total_time': response.elapsed.total_seconds()}

		if result_code == 200:
			if response_assert == "包含":
				if expected_result in result_text:
					result['pass_status'] = 1
					create_case_info(**result)
				# 插入通过状态
				else:
					result['pass_status'] = 0
					create_case_info(**result)
			# 插入不通过状态
			elif response_assert == "相等":
				if expected_result == result_text:
					result['pass_status'] = 1
					create_case_info(**result)
				else:
					result['pass_status'] = 0
					create_case_info(**result)
		else:
			result['pass_status'] = 0
			create_case_info(**result)
		sleep(wait_time)
