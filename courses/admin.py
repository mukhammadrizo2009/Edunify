from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Course, Lesson, Enrollment

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'icon']

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ['title', 'category', 'teacher', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title']

@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']

@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_completed']
