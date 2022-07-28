from django.db import models
from projectdata.color import color_choice
from django.core.validators import MaxValueValidator, MinValueValidator
from interface.models import ProjectInfo


class projectdata(models.Model):
    name = models.ForeignKey(ProjectInfo,verbose_name="项目名称", on_delete=models.CASCADE)
    story = models.CharField(verbose_name='模块名称',max_length=32,help_text="模块名称")
    start_time =  models.DateTimeField(verbose_name='项目开始时间',help_text="项目开始时间")
    end_time = models.DateTimeField(verbose_name='项目结束时间', help_text="项目结束时间")
    plan_start_time =  models.DateTimeField(verbose_name='计划开始时间',help_text="计划开始时间")
    plan_end_time = models.DateTimeField(verbose_name='计划结束时间', help_text="计划结束时间")
    Completion_ratio = models.IntegerField(validators=[MaxValueValidator(100),MinValueValidator(1)],verbose_name='进度',default=0,help_text="进度%")
    # Completion_ratio = models.DecimalField(max_digits=100, decimal_places=2,
    #                                        verbose_name='进度', default=0, help_text="进度%")
    color = models.CharField(choices=color_choice,verbose_name='图例颜色',max_length=32,null=False)

    class Meta:
        db_table = 'project_data'
        verbose_name = '项目进度'
        verbose_name_plural = "项目进度"

    def __str__(self):
        return self.name.__str__()

class projectpic(models.Model):
    class Meta:
        verbose_name = u"项目进度图表"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.Meta.verbose_name


