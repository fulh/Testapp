from django.contrib import admin
import xadmin
from django.utils.html import format_html
from xadmin.layout import Main, Fieldset, Side

from .models import Pathurl,ProjectInfo,CaseInfo,InterfaceInfo

class PathurlAdmin(object):
	# model = Pathurl

	list_display = [
		'id',
		'url_name',
		'url_path',
	]

	ordering = ("id",)
	search_fields = ("url_name",)
	list_filter = ["create_time"]
	list_display_links = ('id', 'url_name', 'url_path')
	show_detail_fields = ['url_name']
	list_editable = ['url_path']
	raw_id_fields = ('url_name',)
	list_per_page = 10

	batch_fields = (
		'url_name',
		'url_path'
	)


class ProjectInfoAdmin(object):
	# model = ProjectInfo

	list_display = [
		'id',
		'product_name',
		'product_describe',
		'product_manager',
		'developer',
		'tester',
	]

	ordering = ("id",)
	search_fields = ("product_name","product_describe","product_manager","developer","tester")
	list_filter = ["product_name","product_describe","product_manager","developer","tester"]
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

	list_display = [
		'id',
		'case_group_name',
		'case_group_describe',
		'create_time',
		'update_time',
	]

	ordering = ("id",)
	search_fields = ("case_group_name","case_group_name")
	list_filter = ["case_group_name","case_group_name"]
	list_display_links = ('case_group_name', 'case_group_name')
	show_detail_fields = ['url_name']
	list_editable = ['case_group_name']
	# raw_id_fields = ('url_name',)
	list_per_page = 10

	# batch_fields = (
	# 	'url_name',
	# 	'url_path'
	# )
class InterfaceInfoAdmin(object):
    model = InterfaceInfo
    extra = 1
    # 提供1个足够的选项行，也可以提供N个
    style = "accordion"

    # 折叠

    def update_button(self, obj):
        # 修改按钮
        button_html = '<a class="icon fa fa-edit" style="color: green" href="/admin/interface/interfaceinfo/%s/update/">修改</a>' % obj.id
        return format_html(button_html)

    update_button.short_description = '<span style="color: green">修改</span>'
    update_button.allow_tags = True

    def delete_button(self, obj):
        # 删除按钮
        button_html = '<a class="icon fa fa-times" style="color: blue" href="/admin/interface/interfaceinfo/%s/delete/">删除</a>' % obj.id
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

	#列表展示的字段
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
        'response_assert',
        'wait_time',
        'regular_expression',
        'regular_variable',
        'regular_template',
        'response_code',
        'actual_result',
        'pass_status',
        'create_time',
        'update_time',
        'update_button',
        'delete_button',
    ]
    #排序
    ordering = ("id",)
    #可以通过搜索框搜索的字段名称
    search_fields = ("case_name",)
    #可以进行过滤操作的列
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




xadmin.site.register(Pathurl, PathurlAdmin)
xadmin.site.register(ProjectInfo, ProjectInfoAdmin)
xadmin.site.register(CaseInfo, CaseInfoAdmin)
xadmin.site.register(InterfaceInfo, InterfaceInfoAdmin)
