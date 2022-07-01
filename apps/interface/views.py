import re
from time import sleep

import demjson
import requests
from django.shortcuts import render
from .models import InterfaceInfo,CaseInfo

def test_case(request):
	nid = 1
	# # nid=request.GET.get('nid')
	# Interfaceobj=InterfaceInfo.objects.get(id__in=nid)
	# # for a in Interfaceobj:
	# # 	print(a.case_name)
	# print(Interfaceobj.case_group)
	# response = requests.request(
	# 	Interfaceobj.request_mode,
	# 	Interfaceobj.interface_url,
	# 	data=Interfaceobj.request_body,
	# 	headers=demjson.decode(Interfaceobj.request_head),
	# 	params=demjson.decode(Interfaceobj.request_parameter)
	# )
	# print(response.status_code)
	# # 实际的响应代码
	# print(response.text)
	# # 实际的响应文本

	data_object = CaseInfo.objects.get(id=nid).groups.values().order_by("id")

	print(list(data_object))
	return render(request,"index.html")


def update_interface_info(case_id, field, value):
	# 等价于UPDATE interface_info SET field=value WHERE id=case_id;
	field_value = {field: value}
	InterfaceInfo.objects.filter(id=case_id).update(**field_value)


def case_test2(request):
	global regular_result
	regular_result = {}
	# 声明一个全局变量regular_result（正则表达式提取的结果）
	# 用于传参
	nid =1
	# case_group_id = request.POST.get('form_case_group_id_b', '')
	data_object = CaseInfo.objects.get(
		id=nid).groups.values().order_by("id")
	# 反向查询用例组包含的用例信息

	data_list = list(data_object)
	# 把QuerySet对象转换成列表
	for item in data_list:
		case_id = item["id"]
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
		# 获取列表里面的字典的值



		# old = "${" + regular_variable + "}"
		# ${变量名} = ${ + 变量名 + }

		if "$" in interface_url:
			temp = "".join(re.findall(r'\w+',re.findall(r'{\w+',interface_url)[0]))
			newtemp = regular_result[temp]
			interface_url = interface_url.replace("${" + temp + "}",newtemp)
		# replace(old, new)把字符串中的旧字符串替换成新字符串
		# 即把正则表达式提取的值替换进去
		# elif "$" in request_parameter:
		# 	request_parameter = request_parameter.replace(old, regular_result[regular_variable])
		# elif "$" in request_head:
		# 	request_head = request_head.replace(old, regular_result[regular_variable])
		# elif "$" in request_body:
		# 	request_body = request_body.replace(old, regular_result[regular_variable])
		# elif "$" in expected_result:
		# 	expected_result = expected_result.replace(old, regular_result[regular_variable])

		if body_type == "x-www-form-urlencoded":
			pass
		# 请求体类型默认使用浏览器原生表单
		# 如果是这种格式，不作任何处理
		elif body_type == "json":
			request_body = demjson.decode(request_body)
		# 等价于json.loads()反序列化

		print(interface_url)

		response = requests.request(
			request_mode,
			interface_url,
			data=request_body,
			headers=demjson.decode(request_head),
			params=demjson.decode(request_parameter)
		)
		if regular_expression == "开启" and regular_variable is not None:
			# 如果正则表达式开启，并且变量名不为空
			regular_result[regular_variable] = re.findall(regular_template, response.text)[0]
		# re.findall(正则表达式模板, 某个接口的实际结果)
		# 返回一个符合规则的list，取第1个
		# 即为正则表达式提取的结果

		if regular_expression == "不开启" and regular_variable == "":
			# 如果正则表达式不开启，并且变量名为空
			data_object = CaseInfo.objects.get(
				id=nid).groups.values("regular_variable").filter(
				regular_expression="开启").order_by("id")
			# 取出过滤条件为"正则表达式开启"的那条用例的变量名
			data_list = list(data_object)
			for item in data_list:
				regular_variable = item["regular_variable"]

		result_code = response.status_code
		# 实际的响应代码
		result_text = response.text
		# 实际的响应文本
		print(response.headers)
		print(requests.utils.dict_from_cookiejar(response.cookies))
		expect_error = "接口请求失败，请检查拼写是否正确！"
		print(result_text)
		if result_code == 200:
			if response_assert == "包含":
				update_interface_info(case_id, "response_code", result_code)
				# 插入响应代码
				update_interface_info(case_id, "actual_result", result_text)
				# 插入实际结果
				if expected_result in result_text:
					update_interface_info(case_id, "pass_status", 1)
				# 插入通过状态
				else:
					update_interface_info(case_id, "pass_status", 0)
				# 插入不通过状态
			elif response_assert == "相等":
				update_interface_info(case_id, "response_code", result_code)
				update_interface_info(case_id, "actual_result", result_text)
				if expected_result == result_text:
					update_interface_info(case_id, "pass_status", 1)
				else:
					update_interface_info(case_id, "pass_status", 0)
		else:
			update_interface_info(case_id, "response_code", result_code)
			update_interface_info(case_id, "actual_result", expect_error)
			update_interface_info(case_id, "pass_status", 0)

		sleep(wait_time)
	return render(request, "index.html")

def request_case(request_mode,interface_url,request_body,request_head,request_parameter):
	print(request_mode)
	print(interface_url)
	print(request_body)
	print(demjson.decode(request_head))
	aa = {"username":"admin","password":"123456"}
	print("请求体",demjson.decode(request_parameter))
	response = requests.request(
		request_mode,
		url=interface_url,
		data=request_body,
		headers=demjson.decode(request_head),
		params=aa
	)
	return response