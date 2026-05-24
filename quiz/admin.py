from django.contrib import admin
from .models import Quiz, Question, Result

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'passing_score', 'created_at']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'text', 'correct_answer', 'order']
    list_filter = ['quiz']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'total_questions', 'time_spent', 'created_at']
    list_filter = ['quiz', 'student']
