import xadmin
from .models import projectdata,projectpic
from xadmin.views.base import CommAdminView
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from django_pandas.io import read_frame
from matplotlib.patches import Patch

class ProjectPicAdmin(object):
	"""
	这是用于缺陷趋势图和项目测试进度
	"""
	# list_display = []
	# 设置需要跳转的页面 index1.html，这个页面需要在template
	object_list_template = "color.html"

	model_icon ='fa fa-bug'

	def get_context(self):
		context = CommAdminView.get_context(self)
		qa = projectdata.objects.values('story', 'start_time', 'end_time', 'Completion_ratio','color')

		df = pd.DataFrame(list(qa))

		proj_start = df.start_time.min()
		# number of days from project start to task start
		df['start_num'] = (df.start_time - proj_start).dt.days
		# number of days from project start to end of tasks
		df['end_num'] = (df.end_time - proj_start).dt.days
		# days between start and end of each task
		df['days_start_to_end'] = df.end_num - df.start_num
		df['current_num'] = (df.days_start_to_end * df.Completion_ratio/100)

		plt.rcParams['font.family'] = 'SimHei'
		# fig, ax = plt.subplots(1, figsize=(16, 6))

		fig, (ax, ax1) = plt.subplots(2, figsize=(16, 6), gridspec_kw={'height_ratios': [9, 1]},facecolor='#E0FFFF')

		ax.patch.set_facecolor('#E0FFFF')
		# fig.set_facecolor('blue')
		fig.set_size_inches(16, 6)

		# bars
		ax.barh(df.story, df.current_num, left=df.start_num,color=df.color)
		ax.barh(df.story, df.days_start_to_end, left=df.start_num,color=df.color, alpha=0.5)
		# texts
		for idx, row in df.iterrows():
			ax.text(row.end_num + 0.1, idx, f"{int(row.Completion_ratio)}%", va='center', alpha=0.8)
			ax.text(row.start_num - 0.1, idx, row.story, va='center', ha='right', alpha=0.8)

		ax.set_axisbelow(True)
		ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

		xticks = np.arange(0, df.end_num.max() + 1, 3)
		xticks_labels = pd.date_range(proj_start, end=df.end_time.max()).strftime("%m/%d")
		xticks_minor = np.arange(0, df.end_num.max() + 1, 1)
		ax.set_xticks(xticks)
		ax.set_xticks(xticks_minor, minor=True)
		ax.set_xticklabels(xticks_labels[::3])
		ax.set_yticks([])

		ax_top = ax.twiny()

		# align x axis
		ax.set_xlim(0, df.end_num.max())
		ax_top.set_xlim(0, df.end_num.max())

		# top ticks (markings)
		xticks_top_minor = np.arange(0, df.end_num.max() + 1, 7)
		ax_top.set_xticks(xticks_top_minor, minor=True)
		# top ticks (label)
		xticks_top_major = np.arange(3.5, df.end_num.max() + 1, 7)
		ax_top.set_xticks(xticks_top_major, minor=False)
		# week labels
		xticks_top_labels = [f"Week {i}" for i in np.arange(1, len(xticks_top_major) + 1, 1)]
		ax_top.set_xticklabels(xticks_top_labels, ha='center', minor=False)

		# hide major tick (we only want the label)
		ax_top.tick_params(which='major', color='w')
		# increase minor ticks (to marks the weeks start and end)
		ax_top.tick_params(which='minor', length=8, color='k')

		# remove spines
		ax.spines['right'].set_visible(False)
		ax.spines['left'].set_visible(False)
		ax.spines['left'].set_position(('outward', 10))
		ax.spines['top'].set_visible(False)

		ax_top.spines['right'].set_visible(False)
		ax_top.spines['left'].set_visible(False)
		ax_top.spines['top'].set_visible(False)

		plt.suptitle('项目进度图')

		##### LEGENDS #####
		c_dict = dict(zip(df['story'], df['color']))

		legend_elements = [Patch(facecolor=c_dict[i], label=i) for i in c_dict]

		ax1.legend(handles=legend_elements, loc='upper center', ncol=5, frameon=False)

		# clean second axis
		ax1.spines['right'].set_visible(False)
		ax1.spines['left'].set_visible(False)
		ax1.spines['top'].set_visible(False)
		ax1.spines['bottom'].set_visible(False)
		ax1.set_xticks([])
		ax1.set_yticks([])

		# c_dict = dict(zip(df['story'], df['color']))
		#
		# legend_elements = [Patch(facecolor=c_dict[i], label=i) for i in c_dict]
		# plt.legend(handles=legend_elements)

		# plt.show()

		plt.savefig('./static/media/project.png')
		context.update(
			{"progress_bar_charts":"fulihua"}
		)



		# df = pd.read_excel('./static/media/plan.xls')
		# proj_start = df.Start.min()
		# # number of days from project start to task start
		# df['start_num'] = (df.Start - proj_start).dt.days
		# # number of days from project start to end of tasks
		# df['end_num'] = (df.End - proj_start).dt.days
		# # days between start and end of each task
		# df['days_start_to_end'] = df.end_num - df.start_num
		# df['current_num'] = (df.days_start_to_end * df.Completion)
		#
		# def color(row):
		# 	c_dict = {'MKT': '#E64646', 'FIN': '#E69646', 'ENG': '#34D05C', 'PROD': '#34D0C3', 'IT': '#3475D0'}
		# 	return c_dict[row['Department']]
		#
		# df['color'] = df.apply(color, axis=1)
		#
		# fig, ax = plt.subplots(1, figsize=(16, 6))
		# # bars
		# ax.barh(df.Task, df.current_num, left=df.start_num, color=df.color)
		# ax.barh(df.Task, df.days_start_to_end, left=df.start_num, color=df.color, alpha=0.5)
		# # texts
		# for idx, row in df.iterrows():
		# 	ax.text(row.end_num + 0.1, idx,
		# 			f"{int(row.Completion * 100)}%",
		# 			va='center', alpha=0.9)
		# ##### LEGENDS #####
		# # c_dict = {'MKT': '#E64646', 'FIN': '#E69646', 'ENG': '#34D05C', 'PROD': '#34D0C3', 'IT': '#3475D0'}
		# # legend_elements = [Patch(facecolor=c_dict[i], label=i) for i in c_dict]
		# # plt.legend(handles=legend_elements)
		# ##### TICKS #####
		# xticks = np.arange(0, df.end_num.max() + 1, 3)
		# xticks_labels = pd.date_range(proj_start, end=df.End.max()).strftime("%m/%d")
		# xticks_minor = np.arange(0, df.end_num.max() + 1, 1)
		# ax.set_xticks(xticks)
		# ax.set_xticks(xticks_minor, minor=True)
		# ax.set_xticklabels(xticks_labels[::3])
		# # plt.show()
		# plt.savefig('./static/media/project.png')
		# context.update(
		# 	{"progress_bar_charts":"fulihua"}
		# )
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
xadmin.site.register(projectpic,ProjectPicAdmin)
