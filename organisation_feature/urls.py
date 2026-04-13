""" Name: Ehsaan Zakriya
ID: W2115831"""

from django.urls import path
from . import views

urlpatterns = [
    path('org-chart/', views.org_chart, name='org_chart'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),
]
