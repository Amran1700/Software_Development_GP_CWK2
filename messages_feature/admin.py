from django.contrib import admin
from .models import Message

# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender','recipients', 'subject', 'timestamp', 'status', 'read_status')
    list_filter = ('status', 'read_status', 'timestamp')
    search_fields = ('subject', 'body', 'sender__username','receiver__username')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    
    def recipients(self, obj):
        return ", ".join([user.username for user in obj.receiver.all()])

    recipients.short_description = "Recipients"
