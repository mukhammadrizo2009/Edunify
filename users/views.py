from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from .forms import RegisterForm, LoginForm, ProfileEditForm
from quiz.models import Result

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = 'Успешная регистрация! Добро пожаловать 🎉'
            elif lang == 'tj':
                msg = 'Бақайдгирӣ бомуваффақият анҷом ёфт! Хуш омадед 🎉'
            else:
                msg = 'Successfully registered! Welcome 🎉'
            messages.success(request, msg)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier'].strip()
            password   = form.cleaned_data['password']

            # Try username first, then email
            user = authenticate(request, username=identifier, password=password)
            if user is None:
                # Try by email
                try:
                    matched = CustomUser.objects.get(email__iexact=identifier)
                    user = authenticate(request, username=matched.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                lang = request.session.get('lang', 'en')
                if lang == 'ru':
                    msg = 'Неверное имя пользователя/email или пароль.'
                elif lang == 'tj':
                    msg = 'Номи корбар/почтаи электронӣ ё пароли нодуруст.'
                else:
                    msg = 'Invalid username/email or password.'
                form.add_error(None, msg)
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    user = request.user

    if user.role == 'teacher' or user.role == 'admin':
        # ── TEACHER DASHBOARD ──────────────────────────────
        from courses.models import Course, Enrollment
        from quiz.models import Quiz, Result

        my_courses = Course.objects.filter(teacher=user).order_by('-created_at')

        # Teacher kurslaridagi barcha quizlar
        my_quizzes = Quiz.objects.filter(
            lesson__course__teacher=user
        ).order_by('-created_at')

        # Jami o'quvchilar soni (teacher kurslariga yozilganlar)
        total_students = Enrollment.objects.filter(
            course__teacher=user
        ).values('student').distinct().count()

        # Jami testlar topshirilgan soni
        total_attempts = Result.objects.filter(
            quiz__lesson__course__teacher=user
        ).count()

        context = {
            'my_courses': my_courses,
            'my_quizzes': my_quizzes,
            'total_students': total_students,
            'total_attempts': total_attempts,
            'courses_count': my_courses.count(),
            'quizzes_count': my_quizzes.count(),
        }
        return render(request, 'users/teacher_dashboard.html', context)

    else:
        # ── STUDENT DASHBOARD ──────────────────────────────
        from quiz.models import Result
        enrolled_courses = user.enrollment_set.all()
        recent_results = Result.objects.filter(student=user).order_by('-created_at')[:5]
        context = {
            'enrolled_courses': enrolled_courses,
            'recent_results': recent_results,
        }
        return render(request, 'users/dashboard.html', context)


@login_required
def profile_edit_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            lang = request.session.get('lang', 'en')
            if lang == 'ru':
                msg = 'Профиль успешно обновлен! ✅'
            elif lang == 'tj':
                msg = 'Профил бомуваффақият нав карда шуд! ✅'
            else:
                msg = 'Profile updated successfully! ✅'
            messages.success(request, msg)
            return redirect('dashboard')
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def become_teacher_view(request):
    """Faqat student foydalanuvchilar teacher bo'lishi mumkin."""
    if request.method != 'POST':
        return redirect('dashboard')
    user = request.user
    lang = request.session.get('lang', 'en')
    if user.role == 'student':
        user.role = 'teacher'
        user.save(update_fields=['role'])
        if lang == 'ru':
            msg = 'Поздравляем! Вы успешно зарегистрировались как преподаватель. 🎓'
        elif lang == 'tj':
            msg = 'Табрик мекунем! Шумо бомуваффақият ҳамчун омӯзгор бақайд гирифта шудед. 🎓'
        else:
            msg = 'Congratulations! You have successfully registered as a teacher. 🎓'
        messages.success(request, msg)
    else:
        if lang == 'ru':
            msg = 'Ваша роль уже обновлена.'
        elif lang == 'tj':
            msg = 'Нақши шумо аллакай иваз карда шудааст.'
        else:
            msg = 'Your role is already updated.'
        messages.info(request, msg)
    return redirect('dashboard')
