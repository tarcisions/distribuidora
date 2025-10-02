from django.urls import path
from .views import webhook_whatsapp

urlpatterns = [
    path('webhook/', webhook_whatsapp, name='webhook_whatsapp'),
]
