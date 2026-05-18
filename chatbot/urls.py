from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('procesar/', views.procesar_chat, name='procesar'),
]