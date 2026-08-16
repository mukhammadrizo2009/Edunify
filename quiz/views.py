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
def quiz_view(request, slug):
    quiz = get_object_or_404(Quiz, slug=slug)
    questions = quiz.questions.all()

    # Faqat yozilgan o'quvchilar test ishlay oladi
    is_enrolled = quiz.lesson.course.enrollments.filter(
        student=request.user
    ).exists()
    if not is_enrolled:
        return redirect('course_detail', slug=quiz.lesson.course.slug)

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
    # Faqat o'qituvchining o'z darslari
    my_lessons = Lesson.objects.filter(
        course__teacher=user
    ).select_related('course')

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


# ═══════════════════════════════════════════════
#  TEACHER: AI Test Generator
# ═══════════════════════════════════════════════

@teacher_required
def ai_quiz_generate_page(request):
    """AI yordamida test yaratish sahifasi."""
    user = request.user
    # Faqat quiz yo'q bo'lgan darslar (Endi barcha darslar)
    my_lessons = Lesson.objects.filter(
        course__teacher=user
    ).select_related('course')

    context = {
        'my_lessons': my_lessons,
        'lang': request.session.get('lang', 'en'),
    }
    return render(request, 'quiz/ai_generate.html', context)


@teacher_required
def ai_quiz_generate_api(request):
    """AJAX endpoint — AI yordamida test yaratish."""
    import json as json_module

    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json_module.loads(request.body)
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return JsonResponse({'error': 'Prompt is empty'}, status=400)

        if len(prompt) > 1000:
            return JsonResponse({'error': 'Prompt too long (max 1000 chars)'}, status=400)

        lang = request.session.get('lang', 'en')

        from ai_assistant.utils import generate_quiz_with_ai
        result = generate_quiz_with_ai(prompt, lang=lang)

        return JsonResponse({'success': True, 'data': result})

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        lang = request.session.get('lang', 'en')
        err_msgs = {
            'ru': 'Произошла ошибка при генерации теста. Попробуйте ещё раз.',
            'tj': 'Ҳангоми сохтани тест хатогӣ рух дод. Дубора кӯшиш кунед.',
            'en': 'An error occurred while generating the quiz. Please try again.',
        }
        return JsonResponse({'error': err_msgs.get(lang, err_msgs['en'])}, status=500)


@teacher_required
def ai_quiz_save(request):
    """AI yaratgan testni bazaga saqlash."""
    import json as json_module

    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json_module.loads(request.body)
        lesson_id = data.get('lesson_id')
        title = data.get('title', '').strip()
        passing_score = int(data.get('passing_score', 60))
        questions_data = data.get('questions', [])

        if not lesson_id:
            return JsonResponse({'error': 'Lesson ID required'}, status=400)

        if not questions_data:
            return JsonResponse({'error': 'No questions to save'}, status=400)

        user = request.user
        lesson = get_object_or_404(Lesson, pk=lesson_id, course__teacher=user)

        # Quiz yaratish
        quiz = Quiz.objects.create(
            lesson=lesson,
            title=title or f"{lesson.title} — AI Test",
            passing_score=max(1, min(passing_score, 100)),
            language=request.session.get('quiz_draft_lang', 'en'),
        )

        # Savollarni yaratish
        from django.db import transaction
        questions_to_create = []
        for i, q in enumerate(questions_data, 1):
            correct = q.get('correct', 'A').upper()
            if correct not in ('A', 'B', 'C', 'D'):
                correct = 'A'

            questions_to_create.append(Question(
                quiz=quiz,
                text=q.get('text', ''),
                option_a=q.get('option_a', ''),
                option_b=q.get('option_b', ''),
                option_c=q.get('option_c', ''),
                option_d=q.get('option_d', ''),
                correct_answer=correct,
                order=i,
            ))

        with transaction.atomic():
            Question.objects.bulk_create(questions_to_create)

        lang = request.session.get('lang', 'en')
        success_msgs = {
            'ru': f'✅ Тест успешно создан! {len(questions_to_create)} вопросов добавлено.',
            'tj': f'✅ Тест бомуваффақият сохта шуд! {len(questions_to_create)} савол илова карда шуд.',
            'en': f'✅ Quiz created successfully! {len(questions_to_create)} questions added.',
        }
        messages.success(request, success_msgs.get(lang, success_msgs['en']))

        return JsonResponse({
            'success': True,
            'message': success_msgs.get(lang, success_msgs['en']),
            'redirect': '/users/dashboard/',
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


# ═══════════════════════════════════════════════
#  STUDENT AI QUIZ — Student uchun AI test
# ═══════════════════════════════════════════════

@login_required
def student_ai_quiz_page(request):
    """Student AI Quiz — mavzu tanlash sahifasi."""
    from .models import StudentAIQuiz

    # Studentning oldingi AI testlari (oxirgi 10 ta)
    past_quizzes = StudentAIQuiz.objects.filter(
        student=request.user, is_completed=True
    ).order_by('-created_at')[:10]

    context = {
        'past_quizzes': past_quizzes,
        'lang': request.session.get('lang', 'en'),
    }
    return render(request, 'quiz/student_ai_quiz.html', context)


@login_required
def student_ai_quiz_generate(request):
    """AJAX endpoint — Student uchun AI test yaratish."""
    import json as json_module

    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json_module.loads(request.body)
        subject = data.get('subject', '').strip()
        topic = data.get('topic', '').strip()
        difficulty = data.get('difficulty', 'medium').strip()
        num_questions = int(data.get('num_questions', 10))

        if not subject or not topic:
            return JsonResponse({'error': 'Subject and topic are required'}, status=400)

        if difficulty not in ('easy', 'medium', 'hard'):
            difficulty = 'medium'

        num_questions = max(5, min(num_questions, 20))
        
        # UI language is from session, but quiz language can be selected
        session_lang = request.session.get('lang', 'en')
        quiz_lang = data.get('quiz_lang', session_lang)

        from ai_assistant.utils import generate_student_quiz_with_ai
        result = generate_student_quiz_with_ai(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            lang=quiz_lang,
        )

        # StudentAIQuiz yaratish
        from .models import StudentAIQuiz
        ai_quiz = StudentAIQuiz.objects.create(
            student=request.user,
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            language=quiz_lang,
            questions_data=result.get('questions', []),
            total_questions=len(result.get('questions', [])),
        )

        return JsonResponse({
            'success': True,
            'quiz_id': ai_quiz.pk,
            'data': result,
        })

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        lang = request.session.get('lang', 'en')
        err_msgs = {
            'ru': 'Произошла ошибка при генерации теста. Попробуйте ещё раз.',
            'tj': 'Ҳангоми сохтани тест хатогӣ рух дод. Дубора кӯшиш кунед.',
            'en': 'An error occurred while generating the quiz. Please try again.',
        }
        return JsonResponse({'error': err_msgs.get(lang, err_msgs['en'])}, status=500)


@login_required
def student_ai_quiz_submit(request):
    """AJAX endpoint — Student AI test javoblarini tekshirish."""
    import json as json_module

    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json_module.loads(request.body)
        quiz_id = data.get('quiz_id')
        answers = data.get('answers', {})  # {'0': 'A', '1': 'C', ...}
        time_spent = int(data.get('time_spent', 0))

        if not quiz_id:
            return JsonResponse({'error': 'Quiz ID required'}, status=400)

        from .models import StudentAIQuiz
        ai_quiz = get_object_or_404(StudentAIQuiz, pk=quiz_id, student=request.user)

        if ai_quiz.is_completed:
            return JsonResponse({'error': 'Quiz already completed'}, status=400)

        questions = ai_quiz.questions_data
        score = 0
        wrong_answers = []

        for i, q in enumerate(questions):
            user_answer = answers.get(str(i), '').upper()
            correct = q.get('correct', 'A').upper()

            if user_answer == correct:
                score += 1
            else:
                wrong_answers.append({
                    'question': q.get('text', ''),
                    'user_answer': user_answer,
                    'correct_answer': correct,
                    'explanation': q.get('explanation', ''),
                    'options': {
                        'A': q.get('option_a', ''),
                        'B': q.get('option_b', ''),
                        'C': q.get('option_c', ''),
                        'D': q.get('option_d', ''),
                    }
                })

        # Natijani saqlash
        ai_quiz.score = score
        ai_quiz.wrong_answers = wrong_answers
        ai_quiz.time_spent = time_spent
        ai_quiz.is_completed = True
        ai_quiz.save()

        percentage = ai_quiz.get_percentage()

        return JsonResponse({
            'success': True,
            'quiz_id': ai_quiz.pk,
            'score': score,
            'total': ai_quiz.total_questions,
            'percentage': percentage,
            'wrong_count': len(wrong_answers),
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def student_ai_quiz_result(request, pk):
    """Student AI Quiz natijasi sahifasi."""
    from .models import StudentAIQuiz
    ai_quiz = get_object_or_404(StudentAIQuiz, pk=pk, student=request.user, is_completed=True)

    context = {
        'ai_quiz': ai_quiz,
        'lang': request.session.get('lang', 'en'),
    }
    return render(request, 'quiz/student_ai_result.html', context)


@login_required
def student_ai_quiz_analysis(request, pk):
    """AJAX endpoint — AI batafsil tahlil."""
    from .models import StudentAIQuiz
    ai_quiz = get_object_or_404(StudentAIQuiz, pk=pk, student=request.user, is_completed=True)

    lang = request.session.get('lang', 'en')

    # Agar tahlil allaqachon mavjud bo'lsa
    if ai_quiz.ai_detailed_analysis and isinstance(ai_quiz.ai_detailed_analysis, dict) and ai_quiz.ai_detailed_analysis.get('summary'):
        return JsonResponse({'analysis': ai_quiz.ai_detailed_analysis})

    try:
        from ai_assistant.utils import analyze_student_quiz_detailed

        quiz_data = {
            'subject': ai_quiz.subject,
            'topic': ai_quiz.topic,
            'difficulty': ai_quiz.difficulty,
            'score': ai_quiz.score,
            'total': ai_quiz.total_questions,
            'wrong_answers': ai_quiz.wrong_answers,
            'time_spent': ai_quiz.time_spent,
        }

        analysis = analyze_student_quiz_detailed(quiz_data, lang=lang)

        # DB ga saqlash
        ai_quiz.ai_detailed_analysis = analysis
        if not ai_quiz.ai_feedback and analysis.get('summary'):
            ai_quiz.ai_feedback = analysis['summary']
        ai_quiz.save()

        return JsonResponse({'analysis': analysis})

    except Exception as e:
        import traceback
        traceback.print_exc()
        lang = request.session.get('lang', 'en')
        err_msgs = {
            'ru': 'Ошибка при загрузке анализа AI.',
            'tj': 'Хатогӣ ҳангоми боркунии тахлили AI.',
            'en': 'Error loading AI analysis.',
        }
        return JsonResponse({'error': err_msgs.get(lang, err_msgs['en'])}, status=500)


@teacher_required
def quiz_edit_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, lesson__course__teacher=request.user)
    lang = request.session.get('lang', 'en')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        thumbnail = request.FILES.get('thumbnail')
        passing_score = request.POST.get('passing_score')
        quiz_language = request.POST.get('quiz_language')

        if title:
            quiz.title = title
        if thumbnail:
            quiz.thumbnail = thumbnail
        if passing_score:
            try:
                quiz.passing_score = int(passing_score)
            except ValueError:
                pass
        if quiz_language in ['ru', 'tj', 'en']:
            quiz.language = quiz_language
            
        quiz.save()
        
        if lang == 'ru':
            msg = "Тест успешно обновлен."
        elif lang == 'tj':
            msg = "Тест бомуваффақият нав карда шуд."
        else:
            msg = "Quiz updated successfully."
        messages.success(request, msg)
        return redirect('dashboard')
        
    context = {
        'quiz': quiz,
        'lang': lang,
    }
    return render(request, 'quiz/quiz_edit.html', context)
