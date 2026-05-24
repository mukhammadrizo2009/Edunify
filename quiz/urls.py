from django.urls import path
from .views import quiz_view, quiz_result_view, quiz_ai_feedback_view

urlpatterns = [
    path('<int:pk>/', quiz_view, name='quiz'),
    path('result/<int:pk>/', quiz_result_view, name='quiz_result'),
    path('result/<int:pk>/ai-feedback/', quiz_ai_feedback_view, name='quiz_ai_feedback'),
]
