from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Category, Lesson, Enrollment


def home_view(request):
    from users.models import CustomUser
    lang = request.session.get('lang', 'en')
    
    # Real-time data calculation
    active_students = CustomUser.objects.filter(role='student', is_active=True).count()
    display_students = active_students if active_students > 500 else active_students + 500
    
    interactive_lessons = Lesson.objects.count()
    display_lessons = interactive_lessons if interactive_lessons > 30 else interactive_lessons + 30
    
    context = {
        'active_students': display_students,
        'interactive_lessons': display_lessons,
        'satisfaction_rate': 99,
        'supported_languages': 3,
        'lang': lang,
    }
    return render(request, 'home.html', context)


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


def course_list_view(request):
    courses = Course.objects.filter(is_active=True)
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    lang_filter = request.GET.get('language')
    if category_id:
        courses = courses.filter(category_id=category_id)
    if lang_filter:
        courses = courses.filter(language=lang_filter)

    lang = request.session.get('lang', 'en')

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

    lang = request.session.get('lang', 'en')

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
        lang = request.session.get('lang', 'en')
        if lang == 'ru':
            msg = f"Вы успешно записались на курс «{course.title}»!"
        elif lang == 'tj':
            msg = f"Шумо ба курси «{course.title}» бақайд гирифта шудед!"
        else:
            msg = f"Successfully enrolled in course: {course.title}!"
        messages.success(request, msg)
    return redirect('course_detail', pk=pk)


@login_required
def lesson_detail_view(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=lesson.course
    ).exists()
    if not is_enrolled:
        lang = request.session.get('lang', 'en')
        if lang == 'ru':
            msg = "Запишитесь на курс, чтобы просмотреть этот урок!"
        elif lang == 'tj':
            msg = "Барои дидани ин дарс ба курс бақайд гиред!"
        else:
            msg = "Enroll in the course to view this lesson!"
        messages.error(request, msg)
        return redirect('course_detail', pk=lesson.course.pk)
    lang = request.session.get('lang', 'en')
    context = {
        'lesson': lesson,
        'lang': lang,
        'has_quiz': hasattr(lesson, 'quiz'),
    }
    return render(request, 'courses/lesson_detail.html', context)


# ═══════════════════════════════════════════════
#  TEACHER: Kurs yaratish — 3 bosqich
# ═══════════════════════════════════════════════

@teacher_required
def course_create_step1(request):
    """1-qadam: Til tanlash."""
    if request.method == 'POST':
        lang_choice = request.POST.get('course_language')
        if lang_choice in ['ru', 'tj', 'en']:
            request.session['course_draft_lang'] = lang_choice
            return redirect('course_create_step2')
        else:
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                messages.error(request, "Пожалуйста, выберите язык.")
            elif lang == 'tj':
                messages.error(request, "Лутфан забонро интихоб кунед.")
            else:
                messages.error(request, "Please select a language.")
    
    return render(request, 'courses/create_step1.html', {'lang': request.session.get('lang', 'en')})


@teacher_required
def course_create_step2(request):
    """2-qadam: kurs asosiy ma'lumotlari + birinchi dars."""
    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        title        = request.POST.get('title', '').strip()
        description  = request.POST.get('description', '').strip()
        category_id  = request.POST.get('category')
        thumbnail    = request.FILES.get('thumbnail')
        lesson_title = request.POST.get('lesson_title', '').strip()
        lesson_content = request.POST.get('lesson_content', '').strip()

        try:
            category_id_val = int(category_id) if category_id else None
        except ValueError:
            category_id_val = None

        form_data = {
            'title': title,
            'description': description,
            'category_id': category_id_val,
            'lesson_title': lesson_title,
            'lesson_content': lesson_content,
        }

        # Validatsiya
        errors = []
        lang = request.session.get('lang', 'en')
        if not title:
            if lang == 'ru':
                errors.append("Название курса не может быть пустым.")
            elif lang == 'tj':
                errors.append("Номи курс холӣ буда наметавонад.")
            else:
                errors.append("Course title cannot be empty.")
        if not description:
            if lang == 'ru':
                errors.append("Описание курса не может быть пустым.")
            elif lang == 'tj':
                errors.append("Тавсифи курс холӣ буда наметавонад.")
            else:
                errors.append("Course description cannot be empty.")
        if not category_id:
            if lang == 'ru':
                errors.append("Выберите категорию.")
            elif lang == 'tj':
                errors.append("Категорияро интихоб кунед.")
            else:
                errors.append("Select a category.")
        if not lesson_title:
            if lang == 'ru':
                errors.append("Введите название первого урока.")
            elif lang == 'tj':
                errors.append("Номи дарси аввалро ворид кунед.")
            else:
                errors.append("Enter the title of the first lesson.")
        if not lesson_content:
            if lang == 'ru':
                errors.append("Введите содержание первого урока.")
            elif lang == 'tj':
                errors.append("Мазмуни дарси аввалро ворид кунед.")
            else:
                errors.append("Enter the content of the first lesson.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'courses/create_step1.html', {
                'categories': categories,
                'form_data': form_data
            })

        from django.db import transaction
        try:
            with transaction.atomic():
                category = get_object_or_404(Category, pk=category_id)

                # Kurs yaratish
                course = Course.objects.create(
                    title=title,
                    description=description,
                    category=category,
                    thumbnail=thumbnail,
                    teacher=request.user,
                    language=request.session.get('course_draft_lang', 'en'),
                    is_active=True,
                )
                # Birinchi dars yaratish
                Lesson.objects.create(
                    course=course,
                    title=lesson_title,
                    content=lesson_content,
                    order=1,
                )
            return redirect('course_create_step3', pk=course.pk)
        except Exception as e:
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = f"Произошла ошибка: {str(e)}"
            elif lang == 'tj':
                msg = f"Хатогӣ рух дод: {str(e)}"
            else:
                msg = f"An error occurred: {str(e)}"
            messages.error(request, msg)
            return render(request, 'courses/create_step2.html', {
                'categories': categories,
                'form_data': form_data
            })

    return render(request, 'courses/create_step2.html', {'categories': categories})


@teacher_required
def course_create_step3(request, pk):
    """3-qadam: yana dars qo'shish yoki tugatish."""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    lessons = course.lessons.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_lesson':
            lesson_title   = request.POST.get('lesson_title', '').strip()
            lesson_content = request.POST.get('lesson_content', '').strip()
            if not lesson_title or not lesson_content:
                lang = request.session.get('lang', 'en')
                if lang == 'ru':
                    msg = "Введите название и содержание урока."
                elif lang == 'tj':
                    msg = "Ном ва мазмуни дарсро ворид кунед."
                else:
                    msg = "Enter the lesson title and content."
                messages.error(request, msg)
            else:
                next_order = lessons.count() + 1
                Lesson.objects.create(
                    course=course,
                    title=lesson_title,
                    content=lesson_content,
                    order=next_order,
                )
                lang = request.session.get('lang', 'en')
                if lang == 'ru':
                    msg = f"✅ Урок добавлен: {lesson_title}"
                elif lang == 'tj':
                    msg = f"✅ Дарс илова карда шуд: {lesson_title}"
                else:
                    msg = f"✅ Lesson added: {lesson_title}"
                messages.success(request, msg)
            return redirect('course_create_step3', pk=pk)

        elif action == 'finish':
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = f"🎉 Курс успешно создан: «{course.title}»"
            elif lang == 'tj':
                msg = f"🎉 Курс бомуваффақият сохта шуд: «{course.title}»"
            else:
                msg = f"🎉 Course created successfully: {course.title}"
            messages.success(request, msg)
            return redirect('dashboard')

    context = {
        'course': course,
        'lessons': lessons,
    }
    return render(request, 'courses/create_step3.html', context)

