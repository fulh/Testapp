from django.contrib import admin
import xadmin

from .models import Pathurl,ProjectInfo,CaseInfo,InterfaceInfo

class PathurlAdmin(object):
	model = Pathurl

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
	model = ProjectInfo

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

xadmin.site.register(Pathurl, PathurlAdmin)
xadmin.site.register(ProjectInfo, ProjectInfoAdmin)