from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent, name='sent'),
    path('drafts/', views.drafts, name='drafts'),
    path('deleted/', views.deleted, name='deleted'),
    path('compose/', views.compose, name='compose'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('message/<int:message_id>/deleted/', views.deleted_message_detail, name='deleted_message_detail'),
    path('draft/<int:message_id>/edit/', views.edit_draft, name='edit_draft')
]