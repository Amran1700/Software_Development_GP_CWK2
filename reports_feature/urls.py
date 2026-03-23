from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('preview/<str:report_type>/', views.report_preview, name='preview'),
    path('generate/', views.generate_report, name='generate'),
]
