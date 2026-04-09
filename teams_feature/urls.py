from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
]