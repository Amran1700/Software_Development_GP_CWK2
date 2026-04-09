from django.urls import path
from . import views

urlpatterns = [
    path('DepartmentID/', views.DepartmentID, name='DepartmentID'),
    path('UpDownDependencies/', views.UpDownDependencies, name='UpDownDependencies'),
    path('TeamPage/', views.TeamPage, name='TeamPage')
]