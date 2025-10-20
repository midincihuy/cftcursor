from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/chat/<int:chat_id>/', views.chat_detail_api, name='chat_detail_api'),
    path('import/', views.import_whatsapp_data, name='import_data'),
]
