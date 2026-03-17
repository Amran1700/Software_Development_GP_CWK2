from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent, name='sent'),
    path('drafts/', views.drafts, name='drafts'),
    path('compose/', views.compose, name='compose'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('message/<int:id>/', views.message_detail, name='message_detail'),
]