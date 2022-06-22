import demjson
import requests
from django.shortcuts import render
from .models import InterfaceInfo

def test_case(request):
	nid = [1]
	# nid=request.GET.get('nid')
	Interfaceobj=InterfaceInfo.objects.get(id__in=nid)
	# for a in Interfaceobj:
	# 	print(a.case_name)
	print(Interfaceobj.case_group)
	response = requests.request(
		Interfaceobj.request_mode,
		Interfaceobj.interface_url,
		data=Interfaceobj.request_body,
		headers=demjson.decode(Interfaceobj.request_head),
		params=demjson.decode(Interfaceobj.request_parameter)
	)
	print(response.status_code)
	# 实际的响应代码
	print(response.text)
	# 实际的响应文本
	return render(request,"index.html")
