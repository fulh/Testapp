from django.db import models


class Pathurl(models.Model):
	url_name = models.CharField(max_length=32,help_text="接口说明",verbose_name="接口说明")
	url_path = models.CharField(max_length=32,blank=True,verbose_name="接口地址")
	create_time = models.DateTimeField(auto_now_add=True,null=True,blank=True,verbose_name="创建时间")
	update_time = models.DateTimeField(auto_now_add=True,null=True,blank=True,verbose_name="修改时间")

	class Meta:
		db_table ='path_url'
		verbose_name ='地址信息'
		verbose_name_plural = '地址信息'

	def __str__(self):
		return self.url_name


class ProjectInfo(models.Model):
	product_name = models.CharField(max_length=32, verbose_name="项目名称",help_text="请输入项目名称", db_index=True)
	# 产品线名称，并创建索引
	product_describe = models.TextField(verbose_name="项目描述", help_text="请输入项目描述",blank=True, null=True, default="")
	# 产品描述
	product_manager = models.CharField(max_length=11, verbose_name="项目经理", help_text="请输入项目经理")
	# 产品经理
	developer = models.CharField(max_length=11, verbose_name="开发人员",blank=True, null=True, default="", help_text="请输入开发人员")
	# 开发人员
	tester = models.CharField(max_length=11, verbose_name="测试人员",blank=True, null=True, default="", help_text="请输入测试人员")
	# 测试人员
	create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="创建时间")
	# 创建时间
	update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="修改时间")

	# 修改时间

	class Meta:
		db_table = 'product_info'

		verbose_name = '项目列表'
		verbose_name_plural = "项目列表"

	def __str__(self):
		return self.product_name

	def module_sum(self):
		# 用例总数
		return self.products.all().count()

	# 利用外键反向统计语句
	# short_description在django admin中显示列名称
	module_sum.short_description = '<span style="color: red">项目总数</span>'
	module_sum.allow_tags = True


class CaseInfo(models.Model):
	# 用例组信息表

	case_group_name = models.CharField(	max_length=32, verbose_name="用例组名称",help_text="请输入用例组名称", db_index=True)
	# 用例组名称，并创建索引
	case_group_describe = models.CharField(max_length=255, verbose_name="用例组描述",blank=True, null=True, default="", help_text="请输入用例组描述")
	# 用例组描述
	create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="创建时间")
	# 创建时间
	update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="修改时间")

	# 修改时间

	class Meta:
		db_table = 'case_info'

		verbose_name = '用例组列表'
		verbose_name_plural = "用例组列表"

	def __str__(self):
		return self.case_group_name

	def case_sum(self):
		# 用例总数
		return self.groups.all().count()

	# 利用外键反向统计语句

	case_sum.short_description = '<span style="color: red">用例总数</span>'
	case_sum.allow_tags = True


class InterfaceInfo(models.Model):
    # 用例信息表

    mode_choice = (
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
        ("PATCH", "PATCH"),
    )
    # 请求方式枚举
    # 第一个元素是存储在数据库里面的值
    # 第二个元素是页面显示的值
    body_choice = (
        ("x-www-form-urlencoded", "application/x-www-form-urlencoded"),
        ("json", "application/json"),
        ("form-data", "multipart/form-data"),
        ("xml", "text/xml"),
    )
    # 请求体类型枚举
    assert_choice = (
        ("包含", "包含"),
        ("相等", "相等"),
    )
    # 断言方式枚举
    regular_choice = (
        ("开启", "开启"),
        ("不开启", "不开启"),
    )
    # 是否开启正则表达式枚举

    case_group = models.ForeignKey(CaseInfo, on_delete=models.CASCADE,verbose_name="用例组", related_name="groups",help_text="请选择用例组")
    # 外键，关联用例组id
    case_name = models.CharField(max_length=32, verbose_name="用例名称",help_text="请输入用例名称", db_index=True)
    # 用例名称，并创建索引
    interface_url = models.CharField(max_length=255, verbose_name="接口地址", help_text="请输入接口地址")
    # 接口地址
    request_mode = models.CharField(choices=mode_choice, max_length=11,verbose_name="请求方式", default="GET",help_text="请选择请求方式")
    # 请求方式
    request_parameter = models.TextField(verbose_name="请求参数", blank=True, null=True,help_text="请输入字典格式的请求参数", default="")
    # 请求参数
    request_head = models.TextField(verbose_name="请求头", blank=True, null=True,help_text="请输入字典格式的请求头", default="")
    # 请求头
    body_type = models.CharField(choices=body_choice, max_length=21,blank=True, null=True,verbose_name="请求体类型", default="x-www-form-urlencoded",help_text="请选择请求体类型")
    # 请求体类型
    request_body = models.TextField(
        verbose_name="请求体", blank=True, null=True,
        help_text="请输入浏览器原生表单、json、文件或xml格式的请求体", default="")
    # 请求体
    expected_result = models.TextField(
        verbose_name="预期结果", blank=True, null=True,
        help_text="请输入预期结果", default="")
    # 预期结果
    response_assert = models.CharField(
        choices=assert_choice, max_length=2,
        blank=True, null=True,
        verbose_name="响应断言方式", default="包含",
        help_text="请选择断言方式")
    # 响应断言方式
    wait_time = models.FloatField(
        max_length=5, verbose_name="等待时间", default=0.1,
        blank=True, null=True, help_text="请输入等待时间，单位：秒")
    # 等待时间
    regular_expression = models.CharField(
        choices=regular_choice, max_length=3,
        blank=True, null=True,
        verbose_name="开启正则表达式", default="不开启",
        help_text="请选择是否开启正则表达式")
    # 开启正则表达式
    regular_variable = models.CharField(
        max_length=11, blank=True, null=True,
        verbose_name="正则表达式变量名", default="",
        help_text="请输入正则表达式变量名")
    # 正则表达式变量名
    regular_template = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="正则表达式模板", default="",
        help_text="请输入正则表达式模板")
    # 正则表达式模板
    response_code = models.IntegerField(
        verbose_name="响应代码", blank=True, null=True)
    # 响应代码
    actual_result = models.TextField(
        verbose_name="实际结果", blank=True, null=True)
    # 实际结果
    pass_status = models.BooleanField(verbose_name="是否通过", blank=True, null=True)
    # 是否通过，1为通过，0为不通过
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name="创建时间")
    # 创建时间
    update_time = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name="修改时间")

    # 修改时间

    class Meta:
        db_table = 'interface_info'

        verbose_name = '用例列表'
        verbose_name_plural = "用例列表"

    def __str__(self):
        return self.case_name


class CaseSuiteRecord(models.Model):
    id = models.AutoField(primary_key=True)
    case_suite_record = models.ForeignKey(CaseInfo, on_delete=models.CASCADE, verbose_name='测试用例组')
    test_case = models.ForeignKey(InterfaceInfo, on_delete=models.CASCADE, verbose_name='测试用例')
    request_data = models.CharField('请求体', max_length=1024, null=True)
    response_code = models.IntegerField(verbose_name="响应代码", blank=True, null=True)
    # 响应代码
    actual_result = models.TextField(verbose_name="实际结果", blank=True, null=True)
    # 实际结果
    pass_status = models.BooleanField(verbose_name="是否通过", blank=True, null=True)
    execute_total_time = models.CharField('执行耗时', max_length=1024, null=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="创建时间")

    class Meta:
        db_table = 'Case_Suite'

        verbose_name = '测试结果'
        verbose_name_plural = "测试结果"

    def __str__(self):
        return self.case_name
