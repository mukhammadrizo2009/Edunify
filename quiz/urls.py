from django.urls import path
from .views import (
    quiz_list_view, quiz_view, quiz_result_view, quiz_ai_feedback_view,
    quiz_create_step1, quiz_create_step2, quiz_create_step3,
    ai_quiz_generate_page, ai_quiz_generate_api, ai_quiz_save,
)

urlpatterns = [
    path('', quiz_list_view, name='quiz_list'),
    path('<int:pk>/', quiz_view, name='quiz'),
    path('result/<int:pk>/', quiz_result_view, name='quiz_result'),
    path('result/<int:pk>/ai-feedback/', quiz_ai_feedback_view, name='quiz_ai_feedback'),
    # Teacher: test yaratish
    path('create/', quiz_create_step1, name='quiz_create_step1'),
    path('create/step2/', quiz_create_step2, name='quiz_create_step2'),
    path('create/<int:pk>/questions/<int:num>/', quiz_create_step3, name='quiz_create_step3'),
    # Teacher: AI bilan test yaratish
    path('ai-generate/', ai_quiz_generate_page, name='ai_quiz_generate'),
    path('ai-generate/api/', ai_quiz_generate_api, name='ai_quiz_generate_api'),
    path('ai-generate/save/', ai_quiz_save, name='ai_quiz_save'),
]
