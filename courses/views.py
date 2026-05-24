from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Category, Lesson, Enrollment

def course_list_view(request):
    courses = Course.objects.filter(is_active=True)
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        courses = courses.filter(category_id=category_id)
        
    lang = request.GET.get('lang', 'uz')
    
    context = {
        'courses': courses,
        'categories': categories,
        'lang': lang,
    }
    return render(request, 'courses/course_list.html', context)

def course_detail_view(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    lessons = course.lessons.all()
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()
        
    lang = request.GET.get('lang', 'uz')
    
    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'lang': lang,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course
    )
    if created:
        messages.success(request, f"{course.title} kursiga yozildingiz!")
    return redirect('course_detail', pk=pk)

@login_required
def lesson_detail_view(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    # Faqat yozilgan o'quvchilar ko'rishi mumkin
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=lesson.course
    ).exists()
    if not is_enrolled:
        messages.error(request, 'Bu darsni ko\'rish uchun kursga yoziling!')
        return redirect('course_detail', pk=lesson.course.pk)
    # Til tanlash
    lang = request.GET.get('lang', 'uz')
    context = {
        'lesson': lesson,
        'lang': lang,
        'has_quiz': hasattr(lesson, 'quiz'),
    }
    return render(request, 'courses/lesson_detail.html', context)
