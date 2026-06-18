from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from .models import Quiz, Question, Result
from ai_assistant.utils import analyze_progress
from courses.models import Lesson

def quiz_list_view(request):
    """Barcha testlarni ko'rsatuvchi sahifa."""
    quizzes = Quiz.objects.select_related('lesson', 'lesson__course').all()
    lang_filter = request.GET.get('language')
    if lang_filter:
        quizzes = quizzes.filter(language=lang_filter)
    # Foydalanuvchi a'zo bo'lgan kurslar ID larini olish
    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = request.user.enrollment_set.values_list('course_id', flat=True)
        
    context = {
        'quizzes': quizzes,
        'enrolled_course_ids': list(enrolled_course_ids),
    }
    return render(request, 'quiz/list.html', context)

def teacher_required(view_func):
    """Faqat teacher yoki admin uchun decorator."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role not in ('teacher', 'admin'):
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = "Доступ к этой странице разрешен только преподавателям."
            elif lang == 'tj':
                msg = "Ин саҳифа танҳо барои омӯзгорон дастрас аст."
            else:
                msg = "Only teachers can access this page."
            messages.error(request, msg)
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

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

    # Foydalanuvchi tilini session dan olish
    lang = request.session.get('lang', 'en')

    # Agar feedback bor bo'lsa va til o'zgarmagan bo'lsa — qaytaramiz
    # Feedback tilini tekshirish uchun: ai_feedback__lang field yo'q,
    # shuning uchun har safar langni cache key ga qo'shamiz
    from django.core.cache import cache
    cache_key = f"ai_feedback_{result.pk}_{lang}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({'ai_feedback': cached})

    try:
        student_data = {
            'subject': result.quiz.lesson.course.category.name,
            'topic': result.quiz.lesson.title,
            'score': result.score,
            'total': result.total_questions,
            'wrong_questions': result.wrong_questions,
            'time_spent': max(result.time_spent // 60, 1),
        }
        ai_feedback = analyze_progress(student_data, lang=lang)
        # Cache da saqlash (1 soat)
        cache.set(cache_key, ai_feedback, timeout=3600)
        # DB ga ham saqlash (default lang uchun)
        if not result.ai_feedback:
            result.ai_feedback = ai_feedback
            result.save()
        return JsonResponse({'ai_feedback': ai_feedback})
    except Exception as e:
        if lang == 'ru':
            err_msg = 'Ошибка при загрузке отзыва ИИ'
        elif lang == 'tj':
            err_msg = 'Хатогӣ ҳангоми боркунии фикру мулоҳизаи AI'
        else:
            err_msg = 'Error loading AI feedback'
        return JsonResponse({'error': err_msg}, status=500)


# ═══════════════════════════════════════════════
#  TEACHER: Test yaratish — 3 bosqich
# ═══════════════════════════════════════════════

@teacher_required
def quiz_create_step1(request):
    """1-qadam: Til tanlash."""
    if request.method == 'POST':
        lang_choice = request.POST.get('quiz_language')
        if lang_choice in ['ru', 'tj', 'en']:
            request.session['quiz_draft_lang'] = lang_choice
            return redirect('quiz_create_step2')
        else:
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                messages.error(request, "Пожалуйста, выберите язык.")
            elif lang == 'tj':
                messages.error(request, "Лутфан забонро интихоб кунед.")
            else:
                messages.error(request, "Please select a language.")
    
    return render(request, 'quiz/create_step1.html', {'lang': request.session.get('lang', 'en')})


@teacher_required
def quiz_create_step2(request):
    """2-qadam: qaysi dars, nechta savol."""
    user = request.user
    # Faqat o'qituvchining o'z darslari (allaqachon quiz yo'q bo'lganlar)
    my_lessons = Lesson.objects.filter(
        course__teacher=user
    ).exclude(quiz__isnull=False).select_related('course')

    if request.method == 'POST':
        lesson_id     = request.POST.get('lesson')
        title         = request.POST.get('title', '').strip()
        passing_score = request.POST.get('passing_score', 60)
        num_questions = request.POST.get('num_questions', '5')
        thumbnail     = request.FILES.get('thumbnail')

        # Validatsiya
        try:
            num_questions = max(1, min(int(num_questions), 50))
            passing_score = max(1, min(int(passing_score), 100))
        except ValueError:
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = "Количество вопросов должно быть корректным числом."
            elif lang == 'tj':
                msg = "Шумораи саволҳо бояд рақами дуруст бошад."
            else:
                msg = "Number of questions must be a valid number."
            messages.error(request, msg)
            return redirect('quiz_create_step1')

        lesson = get_object_or_404(Lesson, pk=lesson_id, course__teacher=user)

        if Quiz.objects.filter(lesson=lesson).exists():
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = "Для этого урока тест уже существует."
            elif lang == 'tj':
                msg = "Барои ин дарс аллакай тест мавҷуд аст."
            else:
                msg = "A quiz already exists for this lesson."
            messages.error(request, msg)
            return redirect('quiz_create_step1')

        quiz = Quiz.objects.create(
            lesson=lesson,
            title=title or f"{lesson.title} — Test",
            passing_score=passing_score,
            thumbnail=thumbnail,
            language=request.session.get('quiz_draft_lang', 'en')
        )
        return redirect('quiz_create_step3', pk=quiz.pk, num=num_questions)

    context = {'my_lessons': my_lessons}
    return render(request, 'quiz/create_step2.html', context)


@teacher_required
def quiz_create_step3(request, pk, num):
    """3-qadam: savollarni to'ldirish."""
    quiz   = get_object_or_404(Quiz, pk=pk, lesson__course__teacher=request.user)
    num    = max(1, min(int(num), 50))
    ranges = range(1, num + 1)

    if request.method == 'POST':
        errors = []
        questions_to_create = []

        for i in ranges:
            text    = request.POST.get(f'q_{i}_text', '').strip()
            opt_a   = request.POST.get(f'q_{i}_a', '').strip()
            opt_b   = request.POST.get(f'q_{i}_b', '').strip()
            opt_c   = request.POST.get(f'q_{i}_c', '').strip()
            opt_d   = request.POST.get(f'q_{i}_d', '').strip()
            correct = request.POST.get(f'q_{i}_correct', '').strip().upper()

            lang = request.session.get('lang', 'en')
            if not text:
                if lang == 'ru':
                    errors.append(f"Текст вопроса №{i} не может быть пустым.")
                elif lang == 'tj':
                    errors.append(f"Матни саволи №{i} холӣ буда наметавонад.")
                else:
                    errors.append(f"Question #{i} text cannot be empty.")
                continue
            if not opt_a or not opt_b or not opt_c or not opt_d:
                if lang == 'ru':
                    errors.append(f"Для вопроса №{i} должны быть заполнены все варианты (A, B, C, D).")
                elif lang == 'tj':
                    errors.append(f"Барои саволи №{i} бояд ҳамаи вариантҳо (A, B, C, D) пур карда шаванд.")
                else:
                    errors.append(f"For question #{i}, all options (A, B, C, D) must be filled.")
                continue
            if correct not in ('A', 'B', 'C', 'D'):
                if lang == 'ru':
                    errors.append(f"Для вопроса №{i} необходимо выбрать правильный ответ.")
                elif lang == 'tj':
                    errors.append(f"Барои саволи №{i} интихоб кардани ҷавоби дуруст ҳатмист.")
                else:
                    errors.append(f"For question #{i}, a correct answer must be selected.")
                continue

            questions_to_create.append(Question(
                quiz=quiz, text=text,
                option_a=opt_a, option_b=opt_b,
                option_c=opt_c, option_d=opt_d,
                correct_answer=correct, order=i,
            ))

        if errors:
            for e in errors:
                messages.error(request, e)

            # Re-build questions data from POST request to populate form inputs
            questions_data = []
            for i in ranges:
                questions_data.append({
                    'num': i,
                    'text': request.POST.get(f'q_{i}_text', '').strip(),
                    'option_a': request.POST.get(f'q_{i}_a', '').strip(),
                    'option_b': request.POST.get(f'q_{i}_b', '').strip(),
                    'option_c': request.POST.get(f'q_{i}_c', '').strip(),
                    'option_d': request.POST.get(f'q_{i}_d', '').strip(),
                    'correct': request.POST.get(f'q_{i}_correct', '').strip().upper(),
                })

            context = {
                'quiz': quiz,
                'ranges': ranges,
                'num': num,
                'questions_data': questions_data
            }
            return render(request, 'quiz/create_step3.html', context)

        # Bulk create all questions inside a transaction
        from django.db import transaction
        try:
            with transaction.atomic():
                Question.objects.bulk_create(questions_to_create)
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = f"✅ Тест успешно создан! Добавлено вопросов: {len(questions_to_create)}."
            elif lang == 'tj':
                msg = f"✅ Тест бомуваффақият сохта шуд! {len(questions_to_create)} савол илова карда шуд."
            else:
                msg = f"✅ Quiz created successfully! Added {len(questions_to_create)} questions."
            messages.success(request, msg)
            return redirect('dashboard')
        except Exception as e:
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = f"Ошибка при сохранении теста: {str(e)}"
            elif lang == 'tj':
                msg = f"Хатогӣ ҳангоми нигоҳдории тест: {str(e)}"
            else:
                msg = f"Error saving quiz: {str(e)}"
            messages.error(request, msg)
            
            questions_data = []
            for i in ranges:
                questions_data.append({
                    'num': i,
                    'text': request.POST.get(f'q_{i}_text', '').strip(),
                    'option_a': request.POST.get(f'q_{i}_a', '').strip(),
                    'option_b': request.POST.get(f'q_{i}_b', '').strip(),
                    'option_c': request.POST.get(f'q_{i}_c', '').strip(),
                    'option_d': request.POST.get(f'q_{i}_d', '').strip(),
                    'correct': request.POST.get(f'q_{i}_correct', '').strip().upper(),
                })
            context = {
                'quiz': quiz,
                'ranges': ranges,
                'num': num,
                'questions_data': questions_data
            }
            return render(request, 'quiz/create_step3.html', context)

    # GET request: build empty list of questions
    questions_data = []
    for i in ranges:
        questions_data.append({
            'num': i,
            'text': '',
            'option_a': '',
            'option_b': '',
            'option_c': '',
            'option_d': '',
            'correct': '',
        })

    context = {
        'quiz': quiz,
        'ranges': ranges,
        'num': num,
        'questions_data': questions_data
    }
    return render(request, 'quiz/create_step3.html', context)

