from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q, Max
from django.utils import timezone
from datetime import timezone as dt_timezone
from datetime import datetime
import json
from .models import WhatsAppChat, WhatsAppMessage

def dashboard_view(request):
    """Main dashboard view"""
    chats = WhatsAppChat.objects.prefetch_related('messages').annotate(last_message_time=Max("messages__timestamp")).order_by("-last_message_time")
    
    # Get chats with their latest messages
    chat_data = []
    for chat in chats:
        latest_message = chat.get_latest_message()
        if latest_message:
            chat_data.append({
                'chat': chat,
                'latest_message': latest_message ,
            })
    
    context = {
        'chat_data': chat_data,
    }
    return render(request, 'whatsapp/dashboard.html', context)

def chat_detail_api(request, chat_id):
    """API endpoint for chat details"""
    chat = get_object_or_404(WhatsAppChat, id=chat_id)
    latest_message = chat.get_latest_message()
    
    data = {
        'id': chat.id,
        'chat_id': chat.chat_id,
        'name': chat.name,
        'chat_type': chat.get_chat_type_display(),
        'is_group': chat.is_group,
        'latest_message': {
            'body': latest_message.body if latest_message else '',
            'timestamp': latest_message.timestamp.isoformat() if latest_message else None,
            'from_me': latest_message.from_me if latest_message else False,
            'has_media': latest_message.has_media if latest_message else False,
            'forwarding_score': latest_message.forwarding_score if latest_message else 0,
        } if latest_message else None
    }
    return JsonResponse(data)

def import_whatsapp_data(request):
    """Import WhatsApp data from JSON"""
    if request.method == 'POST' and request.FILES.get('json_file'):
        json_file = request.FILES['json_file']
        try:
            data = json.load(json_file)
            imported_count = 0
            
            for chat_data in data:
                # Create or update chat
                chat, created = WhatsAppChat.objects.get_or_create(
                    chat_id=chat_data['id'],
                    defaults={
                        'name': chat_data['name'],
                        'picture_url': chat_data.get('picture', ''),
                        'chat_type': 'group' if '@g.us' in chat_data['id'] else 'individual'
                    }
                )
                
                # Create message if it doesn't exist
                if 'lastMessage' in chat_data:
                    msg_data = chat_data['lastMessage']
                    message, msg_created = WhatsAppMessage.objects.get_or_create(
                        chat=chat,
                        message_id=msg_data.get('id', ''),
                        defaults={
                            'body': msg_data.get('body', ''),
                            'timestamp': timezone.datetime.fromtimestamp(
                                msg_data.get('timestamp', 0), tz=dt_timezone.utc
                            ),
                            'from_me': msg_data.get('fromMe', False),
                            'has_media': msg_data.get('hasMedia', False),
                            'forwarding_score': msg_data.get('_data', {}).get('forwardingScore', 0),
                            'participant': msg_data.get('participant', ''),
                            'ack_status': msg_data.get('ack', 0),
                        }
                    )
                    if msg_created:
                        imported_count += 1
                
                if created:
                    imported_count += 1
            
            return JsonResponse({
                'success': True, 
                'message': f'Successfully imported {imported_count} records'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error importing data: {str(e)}'
            })
    
    return render(request, 'whatsapp/import.html')
