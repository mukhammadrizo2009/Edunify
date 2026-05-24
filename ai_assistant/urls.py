from django.urls import path
from .views import ai_chat_view, ai_page_view

urlpatterns = [
    path('',     ai_page_view, name='ai_page'),
    path('chat/', ai_chat_view, name='ai_chat'),
]
