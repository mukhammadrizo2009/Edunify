from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Quiz, Question, Result

@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    list_display = ['title', 'lesson', 'passing_score', 'created_at']

@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ['quiz', 'text', 'correct_answer', 'order']
    list_filter = ['quiz']
    fieldsets = (
        ('Question Text', {
            'fields': ('quiz', 'order', 'text', 'text_en', 'text_ru', 'text_tj', 'correct_answer')
        }),
        ('Option A', {'fields': ('option_a', 'option_a_en', 'option_a_ru', 'option_a_tj')}),
        ('Option B', {'fields': ('option_b', 'option_b_en', 'option_b_ru', 'option_b_tj')}),
        ('Option C', {'fields': ('option_c', 'option_c_en', 'option_c_ru', 'option_c_tj')}),
        ('Option D', {'fields': ('option_d', 'option_d_en', 'option_d_ru', 'option_d_tj')}),
    )

@admin.register(Result)
class ResultAdmin(ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'total_questions', 'time_spent', 'created_at']
    list_filter = ['quiz', 'student']
