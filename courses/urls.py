from django.urls import path
from django.views.generic import TemplateView
from .views import (
    course_list_view, course_detail_view, enroll_view,
    lesson_detail_view, course_create_step1, course_create_step2, course_create_step3,
    course_edit_view, home_view, lesson_create_view, lesson_edit_view, lesson_delete_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('courses/', course_list_view, name='course_list'),
    # Teacher: kurs yaratish (statik URL'lar avval!)
    path('courses/create/', course_create_step1, name='course_create_step1'),
    path('courses/create/step2/', course_create_step2, name='course_create_step2'),
    path('courses/create/<int:pk>/lessons/', course_create_step3, name='course_create_step3'),
    path('courses/<int:pk>/edit/', course_edit_view, name='course_edit'),
    # Dinamik URL'lar
    path('courses/<str:slug>/', course_detail_view, name='course_detail'),
    path('courses/<int:pk>/enroll/', enroll_view, name='enroll'),
    path('courses/<int:course_pk>/lesson/add/', lesson_create_view, name='lesson_create'),
    path('lessons/<int:pk>/', lesson_detail_view, name='lesson_detail'),
    path('lessons/<int:pk>/edit/', lesson_edit_view, name='lesson_edit'),
    path('lessons/<int:pk>/delete/', lesson_delete_view, name='lesson_delete'),
]
