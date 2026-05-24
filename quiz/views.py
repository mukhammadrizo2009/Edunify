from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import Quiz, Question, Result
from ai_assistant.utils import analyze_progress

@login_required
def quiz_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.all()

    # Faqat yozilgan o'quvchilar test ishlay oladi
    is_enrolled = quiz.lesson.course.enrollments.filter(
        student=request.user
    ).exists()
    if not is_enrolled:
        return redirect('course_detail', pk=quiz.lesson.course.pk)

    if request.method == 'POST':
        start_time = int(request.POST.get('start_time', 0))
        time_spent = int(timezone.now().timestamp()) - start_time

        score = 0
        wrong_questions = []

        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}', '')
            if user_answer == question.correct_answer:
                score += 1
            else:
                wrong_questions.append({
                    'question': question.text,
                    'user_answer': user_answer,
                    'correct_answer': question.correct_answer,
                })

        # Natijani saqlash (asinxron feedback uchun boshida ai_feedback bo'sh qoladi)
        result = Result.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            total_questions=questions.count(),
            wrong_questions=wrong_questions,
            ai_feedback='',
            time_spent=time_spent,
        )
        return redirect('quiz_result', pk=result.pk)

    context = {
        'quiz': quiz,
        'questions': questions,
        'start_time': int(timezone.now().timestamp()),
    }
    return render(request, 'quiz/quiz.html', context)

@login_required
def quiz_result_view(request, pk):
    result = get_object_or_404(Result, pk=pk, student=request.user)
    context = {'result': result}
    return render(request, 'quiz/result.html', context)

@login_required
def quiz_ai_feedback_view(request, pk):
    result = get_object_or_404(Result, pk=pk, student=request.user)
    
    # Agar bazada allaqachon feedback bo'lsa, qayta so'rov yubormasdan qaytaramiz
    if result.ai_feedback:
        return JsonResponse({'ai_feedback': result.ai_feedback})
        
    # Sun'iy intellekt tahlilini olish
    try:
        student_data = {
            'subject': result.quiz.lesson.course.category.name,
            'topic': result.quiz.lesson.title,
            'score': result.score,
            'total': result.total_questions,
            'wrong_questions': result.wrong_questions,
            'time_spent': max(result.time_spent // 60, 1),
        }
        ai_feedback = analyze_progress(student_data)
        result.ai_feedback = ai_feedback
        result.save()
        return JsonResponse({'ai_feedback': ai_feedback})
    except Exception as e:
        return JsonResponse({'error': 'Feedbackni yuklashda xatolik yuz berdi'}, status=500)
