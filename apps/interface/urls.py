"""Testapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
import xadmin

from apps.interface import views

urlpatterns = [
    path('project/', views.test_case, name='test_case'),
    path('case/', views.case_test2, name='test_case'),
    path('case_test/', views.index, name='test_case'),
    path('test/', views.test),
    # url('casesuite-(?P<direction_id>(\d+))-(?P<classification_id>(\d+)).html$',views.CaseSuiteRecordviwe),
    url('casesuite-(?P<direction_id>(\d+))-(?P<classification_id>(\d+))-(?P<page>(\d+))',views.CaseSuiteRecordviwe),
    url('fu/(\d+)',views.fu),
]
