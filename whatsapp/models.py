from django.db import models

# Create your models here.
from django.utils import timezone
import json

class WhatsAppChat(models.Model):
    CHAT_TYPES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
    ]
    
    chat_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    picture_url = models.URLField(blank=True, null=True)
    chat_type = models.CharField(max_length=20, choices=CHAT_TYPES, default='individual')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_group(self):
        return '@g.us' in self.chat_id or self.chat_type == 'group'
    
    def get_latest_message(self):
        return self.messages.first()

class WhatsAppMessage(models.Model):
    chat = models.ForeignKey(WhatsAppChat, on_delete=models.CASCADE, related_name='messages')
    message_id = models.CharField(max_length=200)
    body = models.TextField()
    timestamp = models.DateTimeField()
    from_me = models.BooleanField(default=False)
    has_media = models.BooleanField(default=False)
    forwarding_score = models.IntegerField(default=0)
    participant = models.CharField(max_length=100, blank=True, null=True)  # For group messages
    ack_status = models.IntegerField(default=0)  # WhatsApp acknowledgment status
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.chat.name}: {self.body[:50]}..."
    
    @property
    def is_forwarded(self):
        return self.forwarding_score > 0
    
    def get_preview(self, length=30):
        return self.body[:length] + '...' if len(self.body) > length else self.body
