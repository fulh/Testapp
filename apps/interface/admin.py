from django.contrib import admin
import re
import demjson
from time import sleep
import subprocess

import xadmin
from xadmin import views
from django.utils.html import format_html
from xadmin.layout import Main, Fieldset, Side
from xadmin.plugins.actions import BaseActionView
from xadmin.plugins.batch import BatchChangeAction
from django.utils.safestring import mark_safe
from django.utils.datetime_safe import datetime

from .models import Pathurl, ProjectInfo, CaseInfo, InterfaceInfo, CaseSuiteRecord,PerformanceInfo,PerformanceResultInfo
from .views import request_case
from tools import rep_expr,execute


class BaseSetting(object):
	"""xadmin的基本配置"""
	enable_themes = True  # 开启主题切换功能
	use_bootswatch = True  # 支持切换主题


xadmin.site.register(views.BaseAdminView, BaseSetting)


class GlobalSettings(object):
	"""xadmin的全局配置"""
	site_title = "测试后台管理系统"  # 设置站点标题
	site_footer = "测试用例管理"  # 设置站点的页脚
	menu_style = "accordion"  # 设置菜单折叠，在左侧，默认的
	# 设置models的全局图标, UserProfile, Sports 为表名
	# global_search_models = [UserProfile, Sports]
	# global_models_icon = {
	#     UserProfile: "glyphicon glyphicon-user", Sports: "fa fa-cloud"


xadmin.site.register(views.CommAdminView, GlobalSettings)


class CopyAction(BaseActionView):
	# 添加复制动作

	action_name = "copy_data"
	description = "复制所选的 %(verbose_name_plural)s"
	model_perm = 'change'
	icon = 'fa fa-facebook'

	def do_action(self, queryset):
		for qs in queryset:
			qs.id = None
			# 先让这条数据的id为空
			qs.save()
		return None



class CaseSuitedoAction(BaseActionView):
	# 用例组执行测试用例

	action_name = "cases_do_data"
	description = "所选的 %(verbose_name_plural)s进行测试"
	model_perm = 'change'
	icon = 'fa fa-check'

	def do_action(self, queryset):

		global regular_result
		regular_result = {}

		# 循环获取queryset 对象中的列表
		for a in queryset.values():

			id = a['id']
			data_object = CaseInfo.objects.get(id=id).groups.values().order_by("id")

			# 根据获取到到的测试用例组ID，根据用例组ID修改测试结果不是最新数据
			new = {"new_case": 0}
			CaseSuiteRecord.objects.filter(case_suite_record=id).update(**new)
			# 把数据转换成list
			data_list = list(data_object)
			execute(id,data_list,regular_result)

		return None



class CasedoAction(BaseActionView):
	# 用例执行测试用例

	action_name = "cases_do_data"
	description = "所选的 %(verbose_name_plural)s进行测试"
	model_perm = 'change'
	icon = 'fa fa-check'

	def do_action(self, queryset):
		""""
		定义全局变量，把每次获取的变量存在在全局变量字典中，
		"""
		global regular_result
		regular_result = {}

		# 循环获取queryset 对象中的列表
		idlist = []
		for a in queryset.values():
			idlist.append(a['id'])

		#根据获取到到的测试用例组ID，根据用例组ID修改测试结果不是最新数据
		new = {"new_case": 0}
		CaseSuiteRecord.objects.filter(test_case_id__in=idlist).update(**new)

		#把数据转换成list
		data_list = list(queryset.values())
		execute(a["case_group_id"],data_list,regular_result)

		return None

class jmeteraction(BaseActionView):

	action_name = "cases_do_data"
	description = "所选的 %(verbose_name_plural)s进行压力测试"
	model_perm = 'change'
	icon = 'fa fa-check'


	def do_action(self, queryset):
		jmeter = queryset.values()
		print(list(jmeter))
		for jt in list(jmeter):
			id = jt["id"]
			jmeter_script = jt["jmeter_script"]
			sample_number = jt["sample_number"]
			duration = jt["duration"]

			prefix = re.findall("(.*).jmx", jmeter_script)[0]
			time = datetime.now().strftime("%Y%m%d%H%M%S")
			jmx = "media/" + jmeter_script
			jtl = "media/" + prefix + time + ".jtl"
			report = "media/" + prefix + time + "report"


			command = "jmeter" + " -JthreadNum=" + str(sample_number) + " -Jtime=" + str(duration) + " -n -t " + jmx + " -l " + jtl + " -e -o " + report
			print(command)
			subprocess.run(command, shell=True)

			PerformanceResultInfo.objects.create(
				script_result_id=id,
				test_report=report + "/index.html",
				jtl=jtl,
				dashboard_report=report,)

		return None



class PathurlAdmin(object):

	list_display = [
		'id',
		'url_name',
		'url_path',
	]

	# ordering = ("id",)
	ordering = ("id",)
	search_fields = ("url_name",)
	list_filter = ["create_time"]
	list_display_links = ('id', 'url_name', 'url_path')
	show_detail_fields = ['url_name']
	list_editable = ['url_path']
	raw_id_fields = ('url_name',)
	model_icon = 'fa fa-book'
	list_per_page = 10

	batch_fields = (
		'url_name',
		'url_path'
	)


class ProjectInfoAdmin(object):
	# model = ProjectInfo
	model_icon = 'fa fa-asterisk'
	list_display = [
		'id',
		'product_name',
		'product_describe',
		'product_manager',
		'developer',
		'tester',
	]

	ordering = ("id",)
	search_fields = ("product_name", "product_describe", "product_manager", "developer", "tester")
	list_filter = ["product_name", "product_describe", "product_manager", "developer", "tester"]
	list_display_links = ('product_name', 'product_describe', 'product_manager')
	show_detail_fields = ['url_name']
	list_editable = ['product_name']
	# raw_id_fields = ('url_name',)
	list_per_page = 10

# batch_fields = (
# 	'url_name',
# 	'url_path'
# )


class CaseInfoAdmin(object):
	# model = CaseInfo
	# inlines =[ProjectInfoAdmin]
	model_icon = 'fa fa-quora'

	list_display = [
		'id',
		# 'make_case',
		'case_group_name',
		'case_group_describe',
		'create_time',
		'update_time',
	]

	ordering = ("id",)
	search_fields = ("case_group_name", "case_group_name")
	list_filter = ["case_group_name", "case_group_name"]
	list_display_links = ('case_group_name', 'case_group_name')
	show_detail_fields = ['url_name']
	list_editable = ['case_group_name']
	# raw_id_fields = ('url_name',)
	list_per_page = 10

	# batch_fields = (
	# 	'url_name',
	# 	'url_path'
	# )

	def update_interface_info(self, case_id, field, value):
		"""
		根据传入的用例组ID，
		"""
		field_value = {field: value}
		InterfaceInfo.objects.filter(id=case_id).update(**field_value)

	def create_case_info(self, *args, **kwargs):
		CaseSuiteRecord.objects.create(**kwargs)

	def make_case(self,request, queryset):
		"""
		param request request 请求数据
		param queryset 是CaseInfo对象的QuerySet 对象
		"""
		global regular_result
		regular_result = {}

		# 循环获取queryset 对象中的列表
		for a in queryset.values():

			data_object = CaseInfo.objects.get(id=a['id']).groups.values().order_by("id")

			# 根据获取到到的测试用例组ID，根据用例组ID修改测试结果不是最新数据
			new = {"new_case": 0}
			CaseSuiteRecord.objects.filter(case_suite_record=a['id']).update(**new)
			# 把数据转换成list
			data_list = list(data_object)
			# id =a['id']
			execute(a['id'], data_list, regular_result)



	make_case.short_description = "选择执行测试用例"
	actions = [CopyAction, make_case,CaseSuitedoAction]

# 列表页面，添加复制动作与批量修改动作


class InterfaceInfoAdmin(object):
	model = InterfaceInfo
	extra = 1
	# 提供1个足够的选项行，也可以提供N个
	style = "accordion"
	model_icon = 'fa fa-suitcase'

	# 折叠
	def update_interface_info(self, case_id, field, value):
		field_value = {field: value}
		InterfaceInfo.objects.filter(id=case_id).update(**field_value)

	def update_button(self, obj):
		# 修改按钮
		button_html = '<a class="icon fa fa-edit" style="color: green" href="/xadmin/interface/interfaceinfo/%s/update/">修改</a>' % obj.id
		return format_html(button_html)

	update_button.short_description = '<span style="color: green">修改</span>'
	update_button.allow_tags = True

	def delete_button(self, obj):
		# 删除按钮
		button_html = '<a class="icon fa fa-times" style="color: blue" href="/xadmin/interface/interfaceinfo/%s/delete/">删除</a>' % obj.id
		return format_html(button_html)

	delete_button.short_description = '<span style="color: blue">删除</span>'
	delete_button.allow_tags = True

	form_layout = (
		Main(
			Fieldset('用例信息部分',
			         'case_group', 'case_name'),
			Fieldset('接口信息部分',
			         'interface_url', 'request_mode',
			         'request_parameter', 'request_head', 'body_type',
			         'request_body', 'expected_result', 'response_assert',
			         'wait_time'),
			Fieldset('正则表达式提取器',
			         'regular_expression', 'regular_variable', 'regular_template'),
		),
		Side(
			# Fieldset('响应信息部分',
			#          'response_code', 'actual_result', 'pass_status'),
			# Fieldset('时间部分',
			#          'create_time', 'update_time'),
		)
	)
	# 详情页面字段分区，请注意不是fieldsets

	# 列表展示的字段
	list_display = [
		'id',
		'case_group',
		'case_name',
		'interface_url',
		'request_mode',
		'request_parameter',
		'request_head',
		'body_type',
		'request_body',
		'expected_result',
		# 'response_assert',
		# 'wait_time',
		'regular_expression',
		# 'regular_variable',
		# 'regular_template',
		# 'response_code',
		# 'actual_result',
		'pass_status',
		# 'create_time',
		# 'update_time',
		'update_button',
		'delete_button',
	]
	# 排序
	ordering = ("-id",)
	# 可以通过搜索框搜索的字段名称
	search_fields = ("case_name",)
	# 可以进行过滤操作的列
	list_filter = ["pass_status", "create_time"]
	list_display_links = ('id', 'case_group', 'case_name')
	show_detail_fields = ['case_name']
	list_editable = ['case_name']
	readonly_fields = ['response_code', 'actual_result', 'pass_status']
	raw_id_fields = ('case_group',)
	list_per_page = 10

	batch_fields = (
		'case_name',
		'interface_url',
		'request_mode',
		'request_parameter',
		'request_head',
		'body_type',
		'request_body',
		'expected_result',
		'response_assert',
		'wait_time',
		'regular_expression',
		'regular_variable',
		'regular_template',
	)

	def make_published(self, request, queryset):
		print(queryset)
		global regular_result
		regular_result = {}
		data_list = list(queryset.values().order_by("id"))
		print(data_list)
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
				temp = "".join(re.findall(r'\w+', re.findall(r'{\w+', interface_url)[0]))
				newtemp = regular_result[temp]
				interface_url = interface_url.replace("${" + temp + "}", newtemp)
			print(interface_url)
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
			elif body_type == "json":
				request_body = demjson.decode(request_body)
			# 等价于json.loads()反序列化
			response = request_case(request_mode, interface_url, request_body, request_head, request_parameter)

			if regular_expression == "开启" and regular_variable is not None:
				# 如果正则表达式开启，并且变量名不为空
				regular_result[regular_variable] = re.findall(regular_template, response.text)[0]
			# re.findall(正则表达式模板, 某个接口的实际结果)
			# 返回一个符合规则的list，取第1个
			# 即为正则表达式提取的结果

			result_code = response.status_code
			# 实际的响应代码
			result_text = response.text
			# 实际的响应文本
			expect_error = "接口请求失败，请检查拼写是否正确！"

			if result_code == 200:
				if response_assert == "包含":
					self.update_interface_info(case_id, "response_code", result_code)
					# 插入响应代码
					self.update_interface_info(case_id, "actual_result", result_text)
					# 插入实际结果
					if expected_result in result_text:
						self.update_interface_info(case_id, "pass_status", 1)
					# 插入通过状态
					else:
						self.update_interface_info(case_id, "pass_status", 0)
				# 插入不通过状态
				elif response_assert == "相等":
					self.update_interface_info(case_id, "response_code", result_code)
					self.update_interface_info(case_id, "actual_result", result_text)
					if expected_result == result_text:
						self.update_interface_info(case_id, "pass_status", 1)
					else:
						self.update_interface_info(case_id, "pass_status", 0)
			else:
				self.update_interface_info(case_id, "response_code", result_code)
				self.update_interface_info(case_id, "actual_result", expect_error)
				self.update_interface_info(case_id, "pass_status", 0)

			sleep(wait_time)

	make_published.short_description = "执行测试用例"
	actions = [CopyAction,CasedoAction, make_published]
	# 列表页面，添加复制动作与批量修改动作


class CaseSuiteRecordAdmin(object):
	model = CaseSuiteRecord
	extra = 1
	# 提供1个足够的选项行，也可以提供N个
	style = "accordion"
	model_icon = 'fa fa-etsy'

	list_display = [
		# 'id',
		'case_suite_record',
		'test_case',
		'request_data',
		'response_code',
		# 'actual_result',
		'pass_status',
		'new_case',
		'execute_total_time',
		'create_time',
		'show_intro',
	]
	# 排序
	ordering = ("-id",)
	# 可以通过搜索框搜索的字段名称
	search_fields = ("case_suite_record", "test_case", "pass_status")
	# 可以进行过滤操作的列
	list_filter = ["case_suite_record"]
	show_detail_fields = ['response_code']
	readonly_fields = ["case_suite_record", "test_case"]
	# raw_id_fields = ('case_group',)
	list_per_page = 10

	def show_intro(self, obj):
		# 显示简介
		if not obj.actual_result:
			return mark_safe('')
		if len(obj.actual_result) < 20:
			return mark_safe(obj.actual_result)

		short_id = f'{obj._meta.db_table}_short_text_{obj.id}'
		short_text_len = len(obj.actual_result) // 4
		short_text = obj.actual_result[:short_text_len] + '......'
		detail_id = f'{obj._meta.db_table}_detail_text_{obj.id}'
		detail_text = obj.actual_result

		text = """<style type="text/css">
	                    #%s,%s {padding:10px;border:1px solid green;} 
	              </style>
	                <script type="text/javascript">

	                function openShutManager(oSourceObj,oTargetObj,shutAble,oOpenTip,oShutTip,oShortObj){
	                    var sourceObj = typeof oSourceObj == "string" ? document.getElementById(oSourceObj) : oSourceObj;
	                    var targetObj = typeof oTargetObj == "string" ? document.getElementById(oTargetObj) : oTargetObj;
	                    var shortObj = typeof oShortObj == "string" ? document.getElementById(oShortObj) : oShortObj;
	                    var openTip = oOpenTip || "";
	                    var shutTip = oShutTip || "";
	                    if(targetObj.style.display!="none"){
	                       if(shutAble) return;
	                       targetObj.style.display="none";
	                       shortObj.style.display="block";
	                       if(openTip  &&  shutTip){
	                        sourceObj.innerHTML = shutTip; 
	                       }
	                    } else {
	                       targetObj.style.display="block";
	                       shortObj.style.display="none";
	                       if(openTip  &&  shutTip){
	                        sourceObj.innerHTML = openTip; 
	                       }
	                    }
	                    }
	                </script>
	                <p id="%s">%s</p>
	                <p><a href='#a' onclick="openShutManager(this,'%s',false,'点击关闭','点击展开','%s')">点击展开</a></p>

	                <p id="%s" style="display:none">
	                   %s
	                </p>
	                """ % (short_id, detail_id, short_id, short_text, detail_id, short_id, detail_id, detail_text)
		return mark_safe(text)

	show_intro.short_description = '实际响应结果'

	def has_add_permission(self):
		""" 取消后台添加附件功能 """

		return False

	def has_delete_permission(self, obj=None):
		""" 取消后台删除附件功能 """

		return False

	def save_model(self, obj, form, change):
		""" 取消后台编辑附件功能 """

		return False

	def has_change_permission(self, obj=None):
		"""取消链接后的编辑权限"""
		return False


class PerformanceInfoAdmin(object):
	model = PerformanceInfo
	extra = 1
	# 提供1个足够的选项行，也可以提供N个
	style = "accordion"
	model_icon = 'fa fa-etsy'

	list_display = [
		'id',
		'script_introduce',
		'jmeter_script',
		'sample_number',
		'duration',
		'create_time',
	]
	# 排序
	ordering = ("-id",)
	# 可以通过搜索框搜索的字段名称
	search_fields = ("script_introduce", "jmeter_script", "sample_number")
	# 可以进行过滤操作的列
	list_filter = ["script_introduce","duration","jmeter_script"]
	show_detail_fields = ['script_introduce']
	# readonly_fields = ["case_suite_record", "test_case"]
	# raw_id_fields = ('case_group',)
	list_per_page = 10
	actions = [jmeteraction]

class PerformanceResultInfoAdmin(object):
	model = PerformanceResultInfo
	extra = 1
	# 提供1个足够的选项行，也可以提供N个
	style = "accordion"
	model_icon = 'fa fa-etsy'

	def chick_button(self, obj):
		# 修改按钮
		button_html = '<a target="_blank" href="/%s">/%s</a>' %(obj.test_report,obj.test_report)
		# '<a class="icon fa fa-edit" style="color: green" href="/xadmin/interface/interfaceinfo/%s/update/">修改</a>' % obj.dashboard_report
		return format_html(button_html)

	chick_button.short_description = '<span style="color: green">测试报告</span>'
	chick_button.allow_tags = True

	list_display = [
		'id',
		'script_result',
		'chick_button',
		# 'test_report',
		# 'jtl',
		# 'dashboard_report',
		'run_time',
	]
	# 排序
	ordering = ("-id",)
	# 可以通过搜索框搜索的字段名称
	search_fields = ("script_result", "test_report", "dashboard_report")
	# 可以进行过滤操作的列
	list_filter = ["script_result","test_report"]
	show_detail_fields = ['script_result',"test_report"]
	# readonly_fields = ["case_suite_record", "test_case"]
	# raw_id_fields = ('case_group',)
	list_per_page = 10



	def has_add_permission(self):
		""" 取消后台添加附件功能 """

		return False

	def has_delete_permission(self, obj=None):
		""" 取消后台删除附件功能 """

		return False

	def save_model(self, obj, form, change):
		""" 取消后台编辑附件功能 """

		return False

	def has_change_permission(self, obj=None):
		"""取消链接后的编辑权限"""
		return False

xadmin.site.register(Pathurl, PathurlAdmin)
xadmin.site.register(ProjectInfo, ProjectInfoAdmin)
xadmin.site.register(CaseInfo, CaseInfoAdmin)
xadmin.site.register(InterfaceInfo, InterfaceInfoAdmin)
xadmin.site.register(CaseSuiteRecord, CaseSuiteRecordAdmin)
xadmin.site.register(PerformanceInfo, PerformanceInfoAdmin)
xadmin.site.register(PerformanceResultInfo, PerformanceResultInfoAdmin)
