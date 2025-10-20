from rest_framework import serializers
from .models import WhatsAppChat, WhatsAppMessage

class WhatsAppMessageSerializer(serializers.ModelSerializer):
    preview = serializers.CharField(source='get_preview', read_only=True)
    is_forwarded = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = WhatsAppMessage
        fields = [
            'id', 'message_id', 'body', 'preview', 'timestamp', 
            'from_me', 'has_media', 'forwarding_score', 'is_forwarded',
            'participant', 'ack_status'
        ]

class WhatsAppChatSerializer(serializers.ModelSerializer):
    latest_message = WhatsAppMessageSerializer(source='get_latest_message', read_only=True)
    is_group = serializers.BooleanField(read_only=True)
    message_count = serializers.IntegerField(source='messages.count', read_only=True)
    
    class Meta:
        model = WhatsAppChat
        fields = [
            'id', 'chat_id', 'name', 'picture_url', 'chat_type', 
            'is_group', 'created_at', 'updated_at', 'latest_message',
            'message_count'
        ]
