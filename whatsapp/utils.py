import json
import logging
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from .models import WhatsAppChat, WhatsAppMessage

logger = logging.getLogger(__name__)

class WhatsAppDataImporter:
    """Utility class for importing WhatsApp data from JSON"""
    
    def __init__(self):
        self.imported_chats = 0
        self.imported_messages = 0
        self.errors = []
    
    def import_from_json_file(self, json_file):
        """Import data from a JSON file object"""
        try:
            data = json.load(json_file)
            return self.import_from_data(data)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON format: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False
    
    def import_from_data(self, data):
        """Import data from parsed JSON data"""
        if not isinstance(data, list):
            self.errors.append("JSON data should be a list of chat objects")
            return False
        
        try:
            with transaction.atomic():
                for chat_data in data:
                    self._import_chat(chat_data)
            
            logger.info(f"Successfully imported {self.imported_chats} chats and {self.imported_messages} messages")
            return True
            
        except Exception as e:
            self.errors.append(f"Error during import: {str(e)}")
            logger.error(f"Import failed: {str(e)}")
            return False
    
    def _import_chat(self, chat_data):
        """Import a single chat and its messages"""
        try:
            # Validate required fields
            if 'id' not in chat_data or 'name' not in chat_data:
                self.errors.append(f"Missing required fields in chat data")
                return
            
            # Create or update chat
            chat, created = WhatsAppChat.objects.get_or_create(
                chat_id=chat_data['id'],
                defaults={
                    'name': chat_data['name'],
                    'picture_url': chat_data.get('picture', ''),
                    'chat_type': 'group' if '@g.us' in chat_data['id'] else 'individual'
                }
            )
            
            if created:
                self.imported_chats += 1
            
            # Import last message if available
            if 'lastMessage' in chat_data:
                self._import_message(chat, chat_data['lastMessage'])
                
        except Exception as e:
            self.errors.append(f"Error importing chat {chat_data.get('name', 'Unknown')}: {str(e)}")
    
    def _import_message(self, chat, msg_data):
        """Import a single message"""
        try:
            # Convert timestamp
            timestamp = timezone.datetime.fromtimestamp(
                msg_data.get('timestamp', 0), tz=timezone.utc
            )
            
            # Get forwarding score from nested data
            forwarding_score = 0
            if '_data' in msg_data and 'forwardingScore' in msg_data['_data']:
                forwarding_score = msg_data['_data']['forwardingScore']
            
            message, created = WhatsAppMessage.objects.get_or_create(
                chat=chat,
                message_id=msg_data.get('id', ''),
                defaults={
                    'body': msg_data.get('body', ''),
                    'timestamp': timestamp,
                    'from_me': msg_data.get('fromMe', False),
                    'has_media': msg_data.get('hasMedia', False),
                    'forwarding_score': forwarding_score,
                    'participant': msg_data.get('participant', ''),
                    'ack_status': msg_data.get('ack', 0),
                }
            )
            
            if created:
                self.imported_messages += 1
                
        except Exception as e:
            self.errors.append(f"Error importing message: {str(e)}")
    
    def get_import_summary(self):
        """Get summary of import results"""
        return {
            'imported_chats': self.imported_chats,
            'imported_messages': self.imported_messages,
            'errors': self.errors,
            'success': len(self.errors) == 0
        }

