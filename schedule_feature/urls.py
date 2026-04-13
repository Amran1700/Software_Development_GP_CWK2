# Author : Ibrahim Chowdhury | Student Number: W1905510
from django.urls import path
from . import views

# Namespace for this app — allows URLs to be referenced as 'schedule:url_name'
# e.g. {% url 'schedule:create_meeting' %} in templates
app_name = 'schedule'

# URL patterns for the schedule app: calendar month/week/day views, upcoming meetings list,
# meeting detail, create, edit and delete pages
urlpatterns = [
    path('calendar/', views.calendar_month, name='calendar_month'),
    path('upcoming/', views.upcoming_meetings, name='upcoming_meetings'),
    path('meeting/<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('create/', views.create_meeting, name='create_meeting'),
    path('week/', views.calendar_week, name='calendar_week'),
    path('day/', views.calendar_day, name='calendar_day'),
    path('meeting/<int:pk>/edit/', views.edit_meeting, name='edit_meeting'),
    path('meeting/<int:pk>/delete/', views.delete_meeting, name='delete_meeting'),
]