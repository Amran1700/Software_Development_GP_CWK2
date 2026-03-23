# reports/urls.py
# Author: Student 5 – Reports Module

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # /reports/                          → dashboard with 3 report cards
    path('', views.reports_dashboard, name='dashboard'),
    # /reports/preview/<report_type>/    → HTML preview + download buttons
    path('preview/<str:report_type>/', views.report_preview, name='preview'),
    # /reports/generate/                 → POST handler, returns file download
    path('generate/', views.generate_report, name='generate'),
]
