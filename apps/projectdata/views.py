from django.shortcuts import render
from xadmin.views import CommAdminView,BaseAdminView
from .models import projectdata,projectpic
import django.dispatch
work_done = django.dispatch.Signal(providing_args=['id'])

class TestView(CommAdminView):
    def get(self, request):
        id = request.GET.get('id')
        print(BaseAdminView.get_admin_url(self,'for_test'))
        context = super().get_context()  # 这一步是关键，必须super一下继承CommAdminView里面的context，不然侧栏没有对应数据，我在这里卡了好久
        title = "项目进度"  # 定义面包屑变量
        context["breadcrumbs"].append({'url': '/xadmin/', 'title': title})  # 把面包屑变量添加到context里面
        context["title"] = title  # 把面包屑变量添加到context里面
        story = projectdata.objects.values('name_id','name__product_name').distinct()

        # 定义一个信号
        if id:
            work_done.send(TestView, id=id)
            context.update(
                {"story_bar": story, "pic": 0}
            )
        else:
            context.update(
                {"story_bar": story, "pic": 1}
            )
        return render(request, 'test.html', context)  # 最后指定自定义的template模板，并返回context
