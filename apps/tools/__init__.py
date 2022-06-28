import re
import json
from jsonpath import jsonpath
from loguru import logger


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

		url = url.replace("${" + ctt + "}", dic[ctt])

	return url