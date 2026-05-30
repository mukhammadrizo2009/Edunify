from django.urls import path
from django.views.generic import TemplateView
from .views import (
    course_list_view, course_detail_view, enroll_view,
    lesson_detail_view, course_create_step1, course_create_step2,
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('courses/', course_list_view, name='course_list'),
    # Teacher: kurs yaratish (statik URL'lar avval!)
    path('courses/create/', course_create_step1, name='course_create_step1'),
    path('courses/create/<int:pk>/lessons/', course_create_step2, name='course_create_step2'),
    # Dinamik URL'lar
    path('courses/<int:pk>/', course_detail_view, name='course_detail'),
    path('courses/<int:pk>/enroll/', enroll_view, name='enroll'),
    path('lessons/<int:pk>/', lesson_detail_view, name='lesson_detail'),
]
