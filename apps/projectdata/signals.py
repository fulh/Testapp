import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from projectdata.models import projectdata
from django.db.models.signals import pre_save, post_delete,post_save,pre_init
from django.dispatch import receiver
from interface.models import ProjectInfo
from .views import work_done
from .views import TestView


# @receiver(post_delete, sender=projectdata)
# @receiver(post_save, sender=projectdata)
@receiver(work_done, sender=TestView)
def create_pic(sender,**kwargs):
        print("请求的id",kwargs['id'])
        id = kwargs['id']
        qa = projectdata.objects.filter(name_id = id).values('story', 'start_time', 'end_time','plan_start_time','plan_end_time', 'Completion_ratio','color')
        Projectname = ProjectInfo.objects.get(id=id).product_name

        df = pd.DataFrame(list(qa))

        proj_start = df.start_time.min()
        # number of days from project start to task start
        df['start_num'] = (df.start_time - proj_start).dt.days
        # number of days from project start to end of tasks
        df['end_num'] = (df.end_time - proj_start).dt.days
        # days between start and end of each task
        df['days_start_to_end'] = df.end_num - df.start_num
        df['current_num'] = (df.days_start_to_end * df.Completion_ratio/100)

        proj_plan_start = df.plan_start_time.min()
        # number of days from project start to task start
        df['plan_start_num'] = (df.plan_start_time - proj_plan_start).dt.days
        # number of days from project start to end of tasks
        df['plan_end_num'] = (df.plan_end_time - proj_plan_start).dt.days
        # days between start and end of each task
        df['plan_days_start_to_end'] = df.plan_end_num - df.plan_start_num
        # df['plan_current_num'] = (df.days_start_to_end * df.Completion_ratio/100)

        plt.rcParams['font.family'] = 'SimHei'
        # fig, ax = plt.subplots(1, figsize=(16, 6))

        fig, (ax, ax1) = plt.subplots(2, figsize=(16, 6), gridspec_kw={'height_ratios': [9, 1]},facecolor='#E0FFFF')

        ax.patch.set_facecolor('#E0FFFF')
        # fig.set_facecolor('blue')
        fig.set_size_inches(15.3 , 6)

        # bars
        ax.barh(df.index, df.current_num, left=df.start_num,color=df.color)
        ax.barh(df.index, df.days_start_to_end, left=df.start_num,color=df.color,alpha=0.5)
        # ax.barh(df.story, df.current_num+0.1, left=df.start_num, color="#A52A2A")
        # ax.barh(df.story, df.plan_days_start_to_end, left=df.plan_start_num, color=df.color, alpha=0.3)
        # texts
        for idx, row in df.iterrows():
            print("+++++")
            print(idx)
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

        plt.suptitle(Projectname+'进度')

        ##### LEGENDS #####
        c_dict = dict(zip(df['story'], df['color']))
        legend_elements = [Patch(facecolor=c_dict[i], label=i) for i in c_dict]
        ax1.legend(handles=legend_elements, loc='upper center', ncol=15, frameon=False)
        ax1.patch.set_facecolor('#E0FFFF')

        # clean second axis
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax1.set_xticks([])
        ax1.set_yticks([])

        plt.savefig('./static/media/project.png')