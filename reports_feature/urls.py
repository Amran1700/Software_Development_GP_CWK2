# reports_feature/urls.py
# Author: Student 5 – Sadana Suresh (w21162895)
# Description: URL patterns for the Reports module.
#              app_name='reports' creates the namespace so URLs are referenced
#              as reports:reports_dashboard, reports:preview, reports:download_report.

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard – shows all available report type cards
    path('', views.reports_dashboard, name='reports_dashboard'),

    # Preview – shows HTML table preview for a given report type
    # e.g. /reports/preview/teams/ or /reports/preview/all-teams/
    path('preview/<str:report_type>/', views.report_preview, name='preview'),

    # Download – triggers file download for a given report type and format
    # e.g. /reports/download/teams/pdf/ or /reports/download/all-teams/excel/
    path('download/<str:report_type>/<str:file_format>/', views.download_report, name='download_report'),
]