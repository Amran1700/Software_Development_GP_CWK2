from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('calendar/', views.calendar_month, name='calendar_month'),
    path('upcoming/', views.upcoming_meetings, name='upcoming_meetings'),
    path('meeting/<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('create/', views.create_meeting, name='create_meeting'),
    path('week/', views.calendar_week, name='calendar_week'),
    path('meeting/<int:pk>/edit/', views.edit_meeting, name='edit_meeting'),
    path('meeting/<int:pk>/delete/', views.delete_meeting, name='delete_meeting'),
]


