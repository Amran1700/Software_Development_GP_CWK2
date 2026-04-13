""" Marc Ferandes w2081572 """
from django.urls import path
from . import views
# app_name sets the namespace for this app's URLs.
# This allows other templates to reference URLs as 'teams:team_list
app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='team_list'), # Team list page — accessible at /teams/
    path('<int:team_id>/', views.team_detail, name='team_detail'),# Team detail page — accessible at /teams/<id>/ e.g. /teams/1/
]