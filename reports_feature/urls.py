# reports_feature/urls.py
# Author: Sadana Suresh w21162895
# URL patterns for the Reports module.
# app_name='reports' means URLs are referenced as reports:reports_dashboard etc.

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # main dashboard showing the three report cards
    path('', views.reports_dashboard, name='reports_dashboard'),

    # preview page for a given report type e.g. /reports/preview/teams/
    path('preview/<str:report_type>/', views.report_preview, name='preview'),

    # file download e.g. /reports/download/teams/pdf/ or /reports/download/all-teams/excel/
    path('download/<str:report_type>/<str:file_format>/', views.download_report, name='download_report'),
]
