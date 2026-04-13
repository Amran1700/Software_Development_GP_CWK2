# Author: Amran Mohammed id:w2066724

from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'sender',
        'recipients',
        'subject',
        'timestamp',
        'status',
        'read_status'
    )
    # Columns shown in admin list view aka what is used in my fixtures
    list_filter = ('status', 'read_status', 'timestamp')
    search_fields = (
        'subject',
        'body',
        'sender__username',
        'receiver__username'
    )
    ordering = ('-timestamp',)
    # Orders newest email first
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    # insures that its impossible to edit timestamp manually
    def recipients(self, obj):
        return ", ".join([user.username for user in obj.receiver.all()])
        # Converts user list into readable string
    recipients.short_description = "Recipients"
