from django.urls import path
from .views import (
    quiz_list_view, quiz_view, quiz_result_view, quiz_ai_feedback_view,
    quiz_create_step1, quiz_create_step2, quiz_create_step3, quiz_edit_view,
    ai_quiz_generate_page, ai_quiz_generate_api, ai_quiz_save,
    student_ai_quiz_page, student_ai_quiz_generate,
    student_ai_quiz_submit, student_ai_quiz_result, student_ai_quiz_analysis,
)

urlpatterns = [
    path('', quiz_list_view, name='quiz_list'),
    # <str:slug> moved to bottom to prevent masking other static paths
    path('result/<int:pk>/', quiz_result_view, name='quiz_result'),
    path('result/<int:pk>/ai-feedback/', quiz_ai_feedback_view, name='quiz_ai_feedback'),
    # Teacher: test yaratish
    path('create/', quiz_create_step1, name='quiz_create_step1'),
    path('create/step2/', quiz_create_step2, name='quiz_create_step2'),
    path('create/<int:pk>/questions/<int:num>/', quiz_create_step3, name='quiz_create_step3'),
    path('<int:pk>/edit/', quiz_edit_view, name='quiz_edit'),
    # Teacher: AI bilan test yaratish
    path('ai-generate/', ai_quiz_generate_page, name='ai_quiz_generate'),
    path('ai-generate/api/', ai_quiz_generate_api, name='ai_quiz_generate_api'),
    path('ai-generate/save/', ai_quiz_save, name='ai_quiz_save'),
    # Student: AI Quiz
    path('student-ai/', student_ai_quiz_page, name='student_ai_quiz'),
    path('student-ai/generate/', student_ai_quiz_generate, name='student_ai_quiz_generate'),
    path('student-ai/submit/', student_ai_quiz_submit, name='student_ai_quiz_submit'),
    path('student-ai/result/<int:pk>/', student_ai_quiz_result, name='student_ai_quiz_result'),
    path('student-ai/result/<int:pk>/analysis/', student_ai_quiz_analysis, name='student_ai_quiz_analysis'),
    # Catch-all slug must be at the very bottom
    path('<str:slug>/', quiz_view, name='quiz'),
]
