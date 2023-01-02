import re
import demjson
from time import sleep
import subprocess
import logging

import xadmin
from xadmin import views
from django.utils.html import format_html
from xadmin.layout import Main, Fieldset, Side
from xadmin.plugins.actions import BaseActionView
from xadmin.views import BaseAdminPlugin, DeleteAdminView
from xadmin.plugins.batch import BatchChangeAction
from django.utils.safestring import mark_safe
from django.utils.datetime_safe import datetime
from django.contrib import messages
import traceback
from django.db.transaction import (
    TransactionManagementError,
    atomic,
    savepoint,
    savepoint_commit,
    savepoint_rollback
)

from charts.models import CaseapiCharts, BarCharts, Progress
from .models import Pathurl, ProjectInfo, CaseInfo, InterfaceInfo, CaseSuiteRecord, PerformanceInfo, \
    PerformanceResultInfo, regular,Direction,Classification,Video
from user.models import UserProfile, IpAddre
from projectdata.models import projectdata
from tools import rep_expr, execute

from django.core.exceptions import ImproperlyConfigured, ValidationError

logger = logging.getLogger(__name__)

regular_result = {}

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
    apps_icons = {"charts": "fa fa-music", }

    # global_search_models = [UserProfile, Sports]
    # global_models_icon = {
    #     UserProfile: "glyphicon glyphicon-user", Sports: "fa fa-cloud"
    def get_site_menu(self):
        return [
            {'title': "测试结果",
             'icon': 'fa fa-bar-chart',
             'menus': [
                 {'title': '接口测试结果', 'icon': 'fa fa-pie-chart', 'url': self.get_model_url(CaseapiCharts, 'changelist')},
                 {'title': '测试进度统计', 'icon': 'fa fa-line-chart', 'url': self.get_model_url(BarCharts, 'changelist')},
                 # {'title': '缺陷统计', 'icon': 'fa fa-bug', 'url': self.get_model_url(Progress, 'changelist')},
                 {'title': '缺陷统计', 'icon': 'fa fa-signal', 'url': self.get_model_url(Progress, 'changelist')},
             ]
             },
            {'title': "接口测试",
             'icon': 'fa fa-bars',
             'menus': [
                 {'title': '接口URL地址', 'icon': 'fa fa-arrows-alt', 'url': self.get_model_url(Pathurl, 'changelist')},
                 {'title': '项目列表', 'icon': 'fa fa-asterisk', 'url': self.get_model_url(ProjectInfo, 'changelist')},
                 {'title': '用例组列表', 'icon': 'fa fa-quora', 'url': self.get_model_url(CaseInfo, 'changelist')},
                 {'title': '用例列表', 'icon': 'fa fa-suitcase', 'url': self.get_model_url(InterfaceInfo, 'changelist')},
                 {'title': '测试结果列表', 'icon': 'fa fa-etsy', 'url': self.get_model_url(CaseSuiteRecord, 'changelist')},
                 {'title': '正则表达提取', 'icon': 'fa fa-cc', 'url': self.get_model_url(regular, 'changelist')}
             ]
             },
            {'title': "性能测试",
             'icon': 'fa fa-flash',
             'menus': [
                 {'title': 'Jmeter脚本', 'icon': 'fa fa-bug', 'url': self.get_model_url(PerformanceInfo, 'changelist')},
                 {'title': '压测结果列表', 'icon': 'fa fa-superpowers',
                  'url': self.get_model_url(PerformanceResultInfo, 'changelist')},
             ]
             }
            ,
            {'title': "用户管理",
             'icon': 'fa-fw fa fa-user',
             'menus': [
                 {'title': '用户信息', 'icon': 'fa-fw fa fa-user', 'url': self.get_model_url(UserProfile, 'changelist')},
                 {'title': 'IP黑名单', 'icon': 'fa fa-certificate',
                  'url': self.get_model_url(IpAddre, 'changelist')},
             ]
             },
            {'title': "项目管理",
             'icon': 'fa fa-line-chart',
             'menus': [
                 {'title': '项目进度列表', 'icon': 'fa fa-thumb-tack', 'url': self.get_model_url(projectdata, 'changelist')},
                 {'title': '项目进度图表', 'icon': 'fa fa-cny', 'url': '/xadmin/test_view'},
             ]
             },
            {'title': "测试组合搜索",
             'icon': 'fa fa-bars',
             'menus': [
                 {'title': '分类', 'icon': 'fa fa-arrows-alt', 'url': self.get_model_url(Direction, 'changelist')},
                 {'title': '方向', 'icon': 'fa fa-asterisk', 'url': self.get_model_url(Classification, 'changelist')},
                 {'title': '视频', 'icon': 'fa fa-quora', 'url': self.get_model_url(Video, 'changelist')},
             ]
             },


        ]


xadmin.site.register(views.CommAdminView, GlobalSettings)


# 在Action中添加复制动作
class CopyAction(BaseActionView):
    action_name = "copy_data"
    description = "复制所选的 %(verbose_name_plural)s"
    model_perm = 'change'
    icon = 'fa fa-facebook'

    def do_action(self, queryset):
        for qs in queryset:
            qs.id = None
            # 先让这条数据的id为空
            qs.save()
        messages.success(self.request, "复制成功")
        return None


# 根据项目来来执行测试用例
class ProjectdoAction(BaseActionView):
    action_name = "cases_do_data"
    description = "所选的 %(verbose_name_plural)s进行测试"
    model_perm = 'change'
    icon = 'fa fa-check'

    def do_action(self, queryset):
        # global regular_result
        # regular_result = {}

        # 循环获取queryset 对象中的列表
        for a in queryset.values():
            id = a['id']
            data_object = InterfaceInfo.objects.filter(case_group__belong_project_id=id).values().order_by("id")
            case_id = []
            for caseid in data_object:
                case_id.append(caseid['id'])

            # 根据获取到到的测试用例组ID，根据用例组ID修改测试结果不是最新数据
            new = {"new_case": 0}
            CaseSuiteRecord.objects.filter(test_case__in=case_id).update(**new)
            # 把数据转换成list
            data_list = list(data_object)
            execute(id, data_list, regular_result)
        messages.success(self.request, "测试用例组执行")
        return None


# 根据用例组来执行测试用例
class CaseSuitedoAction(BaseActionView):
    action_name = "cases_do_data"
    description = "所选的 %(verbose_name_plural)s进行测试"
    model_perm = 'change'
    icon = 'fa fa-check'

    def do_action(self, queryset):
        global regular_result
        # regular_result = {}

        # 循环获取queryset 对象中的列表
        for a in queryset.values():
            id = a['id']
            data_object = CaseInfo.objects.get(id=id).groupsfu.values().order_by("id")

            # 根据获取到到的测试用例组ID，根据用例组ID修改测试结果不是最新数据
            new = {"new_case": 0}
            CaseSuiteRecord.objects.filter(case_suite_record=id).update(**new)
            # 把数据转换成list
            data_list = list(data_object)
            print(data_list)
            execute(id, data_list, regular_result)
        messages.success(self.request, "测试用例组执行")
        return None


# 在用例列表中执行测试用例
class CasedoAction(BaseActionView):
    action_name = "cases_do_data"
    description = "所选的 %(verbose_name_plural)s进行测试"
    model_perm = 'change'
    icon = 'fa fa-check'

    def do_action(self, queryset):
        """"
        定义全局变量，把每次获取的变量存在在全局变量字典中，
        """
        global regular_result
        # regular_result = {}

        # 循环获取queryset 对象中的列表
        idlist = []
        for a in queryset.values():
            idlist.append(a['id'])

        # 根据获取到到的测试用例组ID，根据用例组ID修改测试结果不是最新数据
        new = {"new_case": 0}
        CaseSuiteRecord.objects.filter(test_case_id__in=idlist).update(**new)

        # 把获取的测试列表，按照id进行排序，不排序会找到不定义的变量
        # 把数据转换成list
        data_list = list(queryset.order_by('id').values())
        execute(a["case_group_id"], data_list, regular_result)
        messages.success(self.request, "测试用例组执行")
        return None


# 根据Jmeter脚本列表执行jmeter性能脚本
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

            command = "jmeter" + " -JthreadNum=" + str(sample_number) + " -Jtime=" + str(
                duration) + " -n -t " + jmx + " -l " + jtl + " -e -o " + report
            print(command)
            subprocess.run(command, shell=True)

            PerformanceResultInfo.objects.create(
                script_result_id=id,
                test_report=report + "/index.html",
                jtl=jtl,
                dashboard_report=report, )

        return None


class PathurlAdmin(object):

    def save_models(self):
        obj = self.new_obj
        obj.create_author = self.request.user
        obj.save()

    list_display = [
        'id',
        'url_name',
        'url_path',
        'create_author',
    ]

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
    model_icon = 'fa fa-asterisk'

    def save_models(self):
        obj = self.new_obj
        obj.create_author = self.request.user
        obj.save()

    exclude = ['create_author']
    list_display = [
        'id',
        'product_name',
        'product_describe',
        'product_manager',
        'developer',
        'tester',
        'create_author',
    ]

    ordering = ("id",)
    search_fields = ("product_name", "product_describe", "product_manager", "developer", "tester")
    list_filter = ["product_name", "product_describe", "product_manager", "developer", "tester"]
    list_display_links = ('product_name', 'product_describe', 'product_manager')
    show_detail_fields = ['url_name']
    list_editable = ['product_name']
    # raw_id_fields = ('url_name',)
    list_per_page = 10
    actions = [ProjectdoAction, ]

class CaseInfoAdmin(object):
    model_icon = 'fa fa-quora'
    exclude = ['is_delete', 'create_author']
    list_display = [
        'id',
        'belong_project',
        'case_group_name',
        'case_group_describe',
        'create_time',
        'update_time',
        'clease_sun',
        'create_author',
    ]

    ordering = ("id",)
    search_fields = ("case_group_name", "belong_project")
    # list_filter = ["case_group_name", "belong_project"]
    # list_display_links = ('case_group_name', 'belong_project')
    # show_detail_fields = ['case_group_name']
    list_editable = ['case_group_name']
    list_per_page = 10

    def clease_sun(self, obj):
        # 通过反向查询出用例数
        sum = obj.groupsfu.all().count()
        if sum > 0:
            button_html = '<a  style="color: red" href="/xadmin/interface/interfaceinfo/?_p_case_group__id__exact=%s">%s</a>' % (
            obj.id, obj.groupsfu.all().count())
        else:
            button_html = '<span style="color: black">%s</span>' % (obj.groupsfu.all().count())
        return format_html(button_html)

    # def clease_sun(self, obj):
    # 	# 通过反向查询出用例数
    # 	return obj.groupsfu.all().count()
    #
    clease_sun.short_description = '<span style="color: green">用例数</span>'
    clease_sun.allow_tags = True

    def update_interface_info(self, case_id, field, value):
        """
        根据传入的用例组ID，
        """
        field_value = {field: value}
        InterfaceInfo.objects.filter(id=case_id).update(**field_value)

    def create_case_info(self, *args, **kwargs):
        CaseSuiteRecord.objects.create(**kwargs)

    def make_case(self, request, queryset):
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
    # actions = [CopyAction, make_case, CaseSuitedoAction]
    actions = [CopyAction, CaseSuitedoAction]

    def delete_models(self, request):
        for obj in request:
            print("admin delete")
            self.log('delete', '', obj)
            obj.is_delete = 0
            obj.save()

    #
    def queryset(self):
        qs = super(CaseInfoAdmin, self).queryset()
        print(self.request.user)
        if self.request.user.is_superuser:
            return qs.filter(is_delete=True)
        else:
            return qs.filter(is_delete=True, create_author=self.request.user)

    def save_models(self):
        obj = self.new_obj
        obj.create_author = self.request.user
        obj.save()


from import_export import resources, widgets
from django.apps import apps
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from import_export.results import Error, Result, RowResult
from django.utils.encoding import force_str
from copy import deepcopy


class InterfaceInfoResource(resources.ModelResource):
    id = Field(attribute='id', column_name="ID")
    # case_group = Field(attribute='case_group', column_name="用例组")
    case_group = Field(column_name='用例组', attribute='case_group', widget=ForeignKeyWidget(CaseInfo, 'case_group_name'))
    case_name = Field(attribute='case_name', column_name="用例名称")
    interface_url = Field(attribute='interface_url', column_name="接口地址")

    def import_obj(self, obj, data, dry_run):
        errors = {}
        # a  = CaseInfo.objects.filter(case_group_name=data['用例组']).values()
        # if len(a)==0:
        #     self.errors["project"] = "项目不存在"
        # else:
        #     self.errors["project"] = "kong"

        for field in self.get_import_fields():
            print(field.attribute)
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue
            try:
                self.import_field(field, obj, data)
            except ValueError as e:
                print(e)
                errors[field.attribute] = ValidationError(
                    force_str(e), code="invalid")
        if errors:
            raise ValidationError(errors)

    def import_row(self, row, instance_loader, using_transactions=True, dry_run=False, raise_errors=False, **kwargs):
        skip_diff = self._meta.skip_diff
        row_result = self.get_row_result_class()()
        original = None
        try:
            self.before_import_row(row, **kwargs)
            instance, new = self.get_or_init_instance(instance_loader, row)
            self.after_import_instance(instance, new, **kwargs)
            if new:
                row_result.import_type = RowResult.IMPORT_TYPE_NEW
            else:
                row_result.import_type = RowResult.IMPORT_TYPE_UPDATE
            row_result.new_record = new
            if not skip_diff:
                original = deepcopy(instance)
                diff = self.get_diff_class()(self, original, new)
            if self.for_delete(row, instance):
                if new:
                    row_result.import_type = RowResult.IMPORT_TYPE_SKIP
                    if not skip_diff:
                        diff.compare_with(self, None, dry_run)
                else:
                    row_result.import_type = RowResult.IMPORT_TYPE_DELETE
                    self.delete_instance(instance, using_transactions, dry_run)
                    if not skip_diff:
                        diff.compare_with(self, None, dry_run)
            else:
                import_validation_errors = {}
                try:
                    self.import_obj(instance, row, dry_run)
                except ValidationError as e:
                    # Validation errors from import_obj() are passed on to
                    # validate_instance(), where they can be combined with model
                    # instance validation errors if necessary
                    import_validation_errors = e.update_error_dict(import_validation_errors)
                if self.skip_row(instance, original):
                    row_result.import_type = RowResult.IMPORT_TYPE_SKIP
                else:
                    self.validate_instance(instance, import_validation_errors)
                    self.save_instance(instance, using_transactions, dry_run)
                    self.save_m2m(instance, row, using_transactions, dry_run)
                    # Add object info to RowResult for LogEntry
                    row_result.object_id = instance.pk
                    row_result.object_repr = force_str(instance)
                if not skip_diff:
                    diff.compare_with(self, instance, dry_run)

            if not skip_diff:
                row_result.diff = diff.as_html()
            self.after_import_row(row, row_result, **kwargs)

        except ValidationError as e:
            row_result.import_type = RowResult.IMPORT_TYPE_INVALID
            row_result.validation_error = e
        except Exception as e:
            row_result.import_type = RowResult.IMPORT_TYPE_ERROR
            # There is no point logging a transaction error for each row
            # when only the original error is likely to be relevant
            if not isinstance(e, TransactionManagementError):
                logger.debug(e, exc_info=e)
            tb_info = traceback.format_exc()
            row_result.errors.append(self.get_error_result_class()(e, row))
        return row_result

    # def before_save_instance(self, instance, using_transactions, dry_run):
    #     print(self)
    #     print("instance")
    #     print(using_transactions)
    #     print(instance.case_name,instance.interface_url,instance.case_group)
    #
    #     return instance

    """
    系统在执行InterfaceInfoResource的时候，先初始化其中的数据，apps.get_model('interface', 'InterfaceInfo')._meta.fields获取到modles 中的所有字段
    """

    def __init__(self):
        super(InterfaceInfoResource, self).__init__()
        field_list = apps.get_model('interface', 'InterfaceInfo')._meta.fields
        # 应用名与模型名
        self.verbose_name_dict = {}
        # 获取所有字段的verbose_name并存放在verbose_name_dict字典里
        for i in field_list:
            self.verbose_name_dict[i.name] = i.verbose_name

    """
    导入的时候，在页面显示的都是modles 中的字段名称，没有显示verbose_name 中的名字
    通过重写field_from_django_field 函数，把column_name重写
    """

    @classmethod
    def field_from_django_field(cls, field_name, django_field, readonly):
        FieldWidget = cls.widget_from_django_field(django_field)
        widget_kwargs = cls.widget_kwargs_for_field(field_name)
        field = cls.DEFAULT_RESOURCE_FIELD(
            attribute=field_name,
            # 重写column_name
            column_name=django_field.verbose_name,
            widget=FieldWidget(**widget_kwargs),
            readonly=readonly,
            default=django_field.default,
        )
        return field

    class Meta:
        model = InterfaceInfo
        skip_unchanged = True
        report_skipped = True

        import_id_fields = ('id',)
        fields = (
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

        )
        exclude = (
            'create_author',
            'update_button',
            'delete_button',
            'create_author',
        )


# 列表页面，添加复制动作与批量修改动作
class InterfaceInfoAdmin(object):
    model = InterfaceInfo
    extra = 0
    # 提供1个足够的选项行，也可以提供N个
    style = "accordion"
    model_icon = 'fa fa-suitcase'
    # 在后台admin页面不需要显示关联项
    use_related_menu = False

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

    def save_models(self):
        obj = self.new_obj
        obj.create_author = self.request.user
        obj.save()

    form_layout = (
        Main(
            Fieldset('用例信息部分', 'case_group', 'case_name'),
            Fieldset('接口信息部分', 'interface_url', 'request_mode',
                     'request_parameter', 'request_head', 'body_type',
                     'request_body', 'expected_result', 'response_assert',
                     'wait_time'),
            # Fieldset('正则表达式提取器',
            #          'regular_expression', 'regular_variable', 'regular_template'),
        ),
        # Side(
        # 	Fieldset('响应信息部分','response_code', 'actual_result', 'pass_status'),
        # 	Fieldset('时间部分','create_time', 'update_time'),
        # )
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
        # 'expected_result',
        # 'regular_expression',
        # 'pass_status',
        'update_button',
        'delete_button',
        'create_author',
    ]
    # 排序
    ordering = ("-id",)
    # 可以通过搜索框搜索的字段名称
    search_fields = ("case_name",)
    # 可以进行过滤操作的列
    list_filter = ['case_group', "create_time"]
    list_display_links = ('id', 'case_group', 'case_name')
    show_detail_fields = ['case_name']
    list_editable = ['case_name']
    # readonly_fields = ['actual_result',]
    raw_id_fields = ('case_group',)
    list_per_page = 10

    # 可以批量编辑的字段，要再action中继承BatchChangeAction 才可以使用
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
        # 'regular_expression',
        # 'regular_variable',
        # 'regular_template',
    )

    import_export_args = {
        'import_resource_class': InterfaceInfoResource,
    }
    # 批量编辑要是使用BatchChangeAction
    # actions = [CopyAction, CasedoAction,BatchChangeAction]
    actions = [CopyAction, CasedoAction, BatchChangeAction]


class CaseSuiteRecordAdmin(object):
    model = CaseSuiteRecord
    extra = 1
    # 提供1个足够的选项行，也可以提供N个
    style = "accordion"
    model_icon = 'fa fa-etsy'

    list_display = [
        'id',
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
    # show_all_rel_details = False
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

        text = """<style type="text/css">#%s,%s {padding:10px;border:1px solid green;}</style>
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
            <p id="%s" style="display:none">%s</p>""" % (
            short_id, detail_id, short_id, short_text, detail_id, short_id, detail_id, detail_text)
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
    model_icon = 'fa fa-bug'

    def save_models(self):
        obj = self.new_obj
        obj.create_author = self.request.user
        obj.save()

    list_display = [
        'id',
        'script_introduce',
        'jmeter_script',
        'sample_number',
        'duration',
        'create_time',
        'run_sum',
    ]
    # 排序
    ordering = ("-id",)
    # 可以通过搜索框搜索的字段名称
    search_fields = ("script_introduce", "jmeter_script", "sample_number")
    # 可以进行过滤操作的列
    list_filter = ["script_introduce", "duration", "jmeter_script"]
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
    model_icon = 'fa fa-superpowers'

    def chick_button(self, obj):
        # 修改按钮
        button_html = '<a target="_blank" href="/%s">/%s</a>' % (obj.test_report, obj.test_report)
        return format_html(button_html)

    chick_button.short_description = '<span style="color: green">测试报告</span>'
    chick_button.allow_tags = True

    list_display = [
        'id',
        'script_result',
        'chick_button',
        'run_time',
    ]
    # 排序
    ordering = ("-id",)
    # 可以通过搜索框搜索的字段名称
    search_fields = ("script_result", "test_report", "dashboard_report")
    # 可以进行过滤操作的列
    list_filter = ["script_result", "test_report"]
    show_detail_fields = ['script_result', "test_report"]
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


class regularAdmin(object):
    model_icon = 'fa fa-quora'

    list_display = [
        'test_id',
        'request_choice',
        'regular_name',
        'regular_variable',
        'regular_template',

    ]

class DirectionAdmin(object):
    list_display = [
        'id',
        'name',
    ]

class ClassificationAdmin(object):
    list_display = [
        'id',
        'name',
        'direction',
    ]

class VideoAdmin(object):
    list_display = [
        'id',
        'status',
        'classification',
        'title',
        'summary',
    ]



from projectdata.views import TestView

xadmin.site.register_view(r'test_view/$', TestView, name='for_test')

xadmin.site.register(Direction, DirectionAdmin)
xadmin.site.register(Classification, ClassificationAdmin)
xadmin.site.register(Video, VideoAdmin)



xadmin.site.register(Pathurl, PathurlAdmin)
xadmin.site.register(ProjectInfo, ProjectInfoAdmin)
xadmin.site.register(CaseInfo, CaseInfoAdmin)
xadmin.site.register(InterfaceInfo, InterfaceInfoAdmin)
xadmin.site.register(CaseSuiteRecord, CaseSuiteRecordAdmin)
xadmin.site.register(PerformanceInfo, PerformanceInfoAdmin)
xadmin.site.register(PerformanceResultInfo, PerformanceResultInfoAdmin)
xadmin.site.register(regular, regularAdmin)
