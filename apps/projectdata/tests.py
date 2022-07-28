# from django.test import TestCase
from interface.models import CaseSuiteRecord,InterfaceInfo
# Create your tests here.

case_list=CaseSuiteRecord.objects.filter(new_case=1,pass_status=False ,case_suite_record_id =3).values()
interdic = InterfaceInfo.objects.all().values("case_name","id")
app_list =[]
for inter in interdic:
    # print(inter)
    for case in case_list:
        if inter['id'] == case['test_case_id']:
            case['test_case_id'] = inter["case_name"]
            app_list.append(case)
            # print(inter['id'])
            # print(case['test_case_id'])
            # case_list[]
print(app_list)


""""
报错信息，没有找到问题，
"""