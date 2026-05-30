from django.urls import path
from .views import quiz_list_view, quiz_view, quiz_result_view, quiz_ai_feedback_view, quiz_create_step1, quiz_create_step2

urlpatterns = [
    path('', quiz_list_view, name='quiz_list'),
    path('<int:pk>/', quiz_view, name='quiz'),
    path('result/<int:pk>/', quiz_result_view, name='quiz_result'),
    path('result/<int:pk>/ai-feedback/', quiz_ai_feedback_view, name='quiz_ai_feedback'),
    # Teacher: test yaratish
    path('create/', quiz_create_step1, name='quiz_create_step1'),
    path('create/<int:pk>/questions/<int:num>/', quiz_create_step2, name='quiz_create_step2'),
]
