import xadmin
from xadmin.sites import site
import pandas as pd
from .models import projectdata,projectpic
from xadmin.views.base import CommAdminView,ModelAdminView,BaseAdminView
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from django.contrib import admin

class ProjectPicAdmin(object):
	"""
	这是用于缺陷趋势图和项目测试进度
	"""
	# list_display = []
	# 设置需要跳转的页面 index1.html，这个页面需要在template
	object_list_template = "color.html"
	model_icon ='fa fa-bug'

	def get_context(self):
		print(self)
		context = CommAdminView.get_context(self)
		story = projectdata.objects.values('id','story')
		print(self.request.path)
		print(self.request.get_full_path())
		print(self.request.GET.get('id'))
		context.update(
			{"story_bar":story}
		)

		return context


class ProjectDataAdmin(object):
	model_icon = 'fa fa-quora'

	list_display = [
		'name',
		'story',
		'start_time',
		'end_time',
		'plan_start_time',
		'plan_end_time',
		'Completion_ratio',
		'color',
	]

	ordering = ("id",)
	search_fields = ("name", "story", "start_time", "Completion_ratio")
	# list_filter = ["case_group_name", "belong_project"]
	# list_display_links = ('case_group_name', 'belong_project')
	# show_detail_fields = ['case_group_name']
	# list_editable = ['case_group_name']
	list_per_page = 10

xadmin.site.register(projectdata,ProjectDataAdmin)
# xadmin.site.register(projectpic,ProjectPicAdmin)

