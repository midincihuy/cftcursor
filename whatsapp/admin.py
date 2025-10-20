from django.contrib import admin

# Register your models here.
from .models import WhatsAppChat, WhatsAppMessage

@admin.register(WhatsAppChat)
class WhatsAppChatAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat_type', 'chat_id', 'created_at']
    list_filter = ['chat_type', 'created_at']
    search_fields = ['name', 'chat_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'body_preview', 'timestamp', 'from_me', 'has_media']
    list_filter = ['from_me', 'has_media', 'timestamp', 'chat__chat_type']
    search_fields = ['body', 'chat__name']
    date_hierarchy = 'timestamp'
    
    def body_preview(self, obj):
        return obj.get_preview(50)
    body_preview.short_description = 'Message Preview'

