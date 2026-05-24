# Edunify
# Edunify — Online Ta'lim Platformasi

> Tojikiston maktab o'quvchilari uchun AI yordamida ishlaydigan online ta'lim platformasi.
> "Yosh Dasturchi Olimpiadasi" — Veb Dasturlash yo'nalishi uchun qurilgan.

---

## Texnologiyalar

- **Backend:** Django 5.x (Python)
- **Database:** MySQL
- **Frontend:** Django Template + Bootstrap 5 + JavaScript
- **AI:** Google Gemini API (bepul)
- **Tillar:** O'zbekcha, Tojikcha, Ruscha, Inglizcha

---

## Loyiha Strukturasi

```
edunify/
├── config/                  # Django asosiy sozlamalar
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                   # Foydalanuvchi tizimi
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── courses/                 # Kurslar moduli
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── quiz/                    # Test moduli
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── ai_assistant/            # AI moduli
│   ├── views.py
│   ├── urls.py
│   └── utils.py
├── static/                  # CSS, JS, Rasmlar
│   ├── css/
│   ├── js/
│   └── images/
├── media/                   # Yuklangan fayllar
├── templates/               # Umumiy templatelar
│   ├── base.html
│   ├── navbar.html
│   └── footer.html
├── locale/                  # Til fayllari (TJ, RU, EN)
├── .env                     # Maxfiy sozlamalar
├── requirements.txt
└── manage.py
```

---

## O'rnatish va Ishga Tushirish

### 1. Loyihani yuklab olish

```bash
git clone https://github.com/username/Edunify.git
cd Edunify
```

### 2. Virtual environment yaratish

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

`requirements.txt` tarkibi:

```
django==5.0
mysqlclient
pillow
python-dotenv
google-generativeai
django-crispy-forms
crispy-bootstrap5
```

### 4. .env faylini sozlash

Loyiha papkasida `.env` fayl yarating:

```env
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
DB_NAME=edutj_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
GEMINI_API_KEY=your_gemini_api_key
```

### 5. MySQL database yaratish

```bash
mysql -u root -p
```

```sql
CREATE DATABASE edutj_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 6. Migratsiyalar

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Superuser yaratish

```bash
python manage.py createsuperuser
```

### 8. Serverni ishga tushirish

```bash
python manage.py runserver
```

Brauzerda oching: `http://127.0.0.1:8000`

---

## Missiyalar — Nima Qilamiz?

Loyiha 6 ta missiyadan iborat. Har bir missiya alohida bosqich.

---

## MISSION 1 — Loyiha Setup ✅

**Maqsad:** Django loyihasini yaratish, MySQL ulash, applarni sozlash.

**Bajarilishi kerak bo'lgan ishlar:**

- Python, pip, virtualenv tekshirish
- Django va barcha kutubxonalarni o'rnatish
- `config/settings.py` ni to'liq sozlash
- MySQL database yaratish
- `users`, `courses`, `quiz`, `ai_assistant` applarini yaratish
- `.env` faylni sozlash
- `python manage.py check` xatosiz ishlashi

**settings.py asosiy sozlamalari:**

```python
INSTALLED_APPS = [
    ...
    'users',
    'courses',
    'quiz',
    'ai_assistant',
    'crispy_forms',
    'crispy_bootstrap5',
]

AUTH_USER_MODEL = 'users.CustomUser'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
```

---

## MISSION 2 — Database Modellar

**Maqsad:** Barcha modellarni yozish va migratsiya qilish.

### users/models.py

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'O\'quvchi'),
        ('teacher', 'O\'qituvchi'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def is_student(self):
        return self.role == 'student'

    def is_teacher(self):
        return self.role == 'teacher'
```

### courses/models.py

```python
from django.db import models
from users.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100)
    name_tj = models.CharField(max_length=100, blank=True)  # Tojikcha
    name_ru = models.CharField(max_length=100, blank=True)  # Ruscha
    name_en = models.CharField(max_length=100, blank=True)  # Inglizcha
    icon = models.CharField(max_length=10, blank=True)      # Emoji
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    title_tj = models.CharField(max_length=200, blank=True)
    title_ru = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    description_tj = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='courses/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_lessons_count(self):
        return self.lessons.count()

    def get_enrolled_count(self):
        return self.enrollments.count()

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    title_tj = models.CharField(max_length=200, blank=True)
    title_ru = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    content_tj = models.TextField(blank=True)
    content_ru = models.TextField(blank=True)
    content_en = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
```

### quiz/models.py

```python
from django.db import models
from users.models import CustomUser
from courses.models import Lesson

class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    passing_score = models.PositiveIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.title} - Test"

    def get_questions_count(self):
        return self.questions.count()

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    text_tj = models.TextField(blank=True)
    text_ru = models.TextField(blank=True)
    text_en = models.TextField(blank=True)
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A','A'),('B','B'),('C','C'),('D','D')]
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Savol {self.order}"

class Result(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    wrong_questions = models.JSONField(default=list)
    ai_feedback = models.TextField(blank=True)
    time_spent = models.PositiveIntegerField(default=0)  # soniyada
    created_at = models.DateTimeField(auto_now_add=True)

    def get_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)

    def is_passed(self):
        return self.get_percentage() >= self.quiz.passing_score

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.get_percentage()}%"
```

**Migratsiya qilish:**

```bash
python manage.py makemigrations users
python manage.py makemigrations courses
python manage.py makemigrations quiz
python manage.py migrate
```

---

## MISSION 3 — Authentication (Login / Register)

**Maqsad:** Foydalanuvchi tizimini to'liq qurish.

**Bajarilishi kerak bo'lgan ishlar:**

- Ro'yxatdan o'tish (Register) — rol tanlash bilan
- Kirish (Login) — email yoki username bilan
- Chiqish (Logout)
- Dashboard sahifasi — faqat login bo'lganlar uchun
- `@login_required` dekorator ishlatish

### users/views.py asosiy ko'rinish

```python
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from .forms import RegisterForm, LoginForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Username yoki parol noto\'g\'ri!')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    user = request.user
    enrolled_courses = user.enrollment_set.all()
    recent_results = Result.objects.filter(student=user).order_by('-created_at')[:5]
    context = {
        'enrolled_courses': enrolled_courses,
        'recent_results': recent_results,
    }
    return render(request, 'users/dashboard.html', context)
```

---

## MISSION 4 — Kurslar Moduli

**Maqsad:** Kurslarni ko'rish, kursga yozilish, darslarni o'qish.

**Bajarilishi kerak bo'lgan ishlar:**

- Barcha kurslar ro'yxati sahifasi
- Kategoriya bo'yicha filtrlash
- Kurs detail sahifasi
- Darslar ro'yxati
- Dars o'qish sahifasi
- Kursga yozilish tugmasi
- Admin panel orqali kurs va dars qo'shish

### courses/views.py asosiy ko'rinish

```python
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
    context = {
        'courses': courses,
        'categories': categories,
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
    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course
    )
    if created:
        messages.success(request, f'{course.title} kursiga yozildingiz!')
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
```

---

## MISSION 5 — Test Moduli

**Maqsad:** Test ishlash va natijani ko'rish tizimi.

**Bajarilishi kerak bo'lgan ishlar:**

- Test sahifasi — savollar bilan
- Test javoblarini qabul qilish
- Natijani hisoblash
- Natijani saqlash
- AI feedback chaqirish (Mission 6 bilan bog'liq)
- Natija sahifasi

### quiz/views.py asosiy ko'rinish

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Quiz, Question, Result
from ai_assistant.utils import analyze_progress
import json

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

        # AI feedback olish
        ai_feedback = analyze_progress({
            'subject': quiz.lesson.course.category.name,
            'topic': quiz.lesson.title,
            'score': score,
            'total': questions.count(),
            'wrong_questions': wrong_questions,
            'time_spent': time_spent // 60,  # daqiqaga o'tkazish
        })

        # Natijani saqlash
        result = Result.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            total_questions=questions.count(),
            wrong_questions=wrong_questions,
            ai_feedback=ai_feedback,
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
```

---

## MISSION 6 — AI Integration

**Maqsad:** Gemini AI ni loyihaga ulash.

**Gemini API key olish:**

1. `aistudio.google.com` ga kir
2. Google account bilan login
3. "Get API Key" tugmasini bos
4. API key ni `.env` fayliga qo'y

### ai_assistant/utils.py

```python
import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache

genai.configure(api_key=settings.GEMINI_API_KEY)

# =============================================
# AI MUALLIM — Faqat ta'lim mavzularida
# =============================================

AI_TEACHER_PROMPT = """
Sen "EduTJ" online ta'lim platformasining AI muallimisan.

QOIDALAR:
1. FAQAT quyidagi mavzularda javob berasan:
   - Matematika, Algebra, Geometriya
   - Fizika, Kimyo, Biologiya
   - Ingliz tili, Tojik tili, Rus tili
   - Tarix, Geografiya, Informatika

2. Agar o'quvchi boshqa mavzuda savol bersa:
   "Kechirasiz, men faqat ta'lim mavzularida yordam bera olaman." deb javob ber.

3. Javoblarni QISQA va TUSHUNARLI qilib ber.
4. Imkon bo'lsa, misol keltir.
5. O'zbek tilida javob ber (agar o'quvchi boshqa tilda yozsa, o'sha tilda javob ber).
"""

def ai_teacher_response(user_question, user_id):
    # Rate limiting — har foydalanuvchi minutiga 5 ta so'rov
    cache_key = f"ai_limit_{user_id}"
    requests_count = cache.get(cache_key, 0)

    if requests_count >= 5:
        return "Iltimos, 1 daqiqa kuting. So'rovlar limiti tugadi."

    cache.set(cache_key, requests_count + 1, timeout=60)

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"{AI_TEACHER_PROMPT}\n\nO'quvchi savoli: {user_question}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Hozir AI muallim bilan bog'lanib bo'lmadi. Keyinroq urinib ko'ring."


# =============================================
# AI PROGRESS TAHLILCHI — Test so'ng feedback
# =============================================

def analyze_progress(student_data):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')

        percentage = round((student_data['score'] / student_data['total']) * 100)

        prompt = f"""
O'quvchining test natijasini tahlil qil va qisqa feedback ber.

Ma'lumotlar:
- Fan: {student_data['subject']}
- Mavzu: {student_data['topic']}
- Natija: {student_data['score']}/{student_data['total']} ({percentage}%)
- Vaqt: {student_data['time_spent']} daqiqa
- Xato savollar soni: {len(student_data['wrong_questions'])}

Quyidagi formatda javob ber:
1. Qisqa baho (1 gap) — maqtov yoki dalda
2. Kuchli tomoni (1 gap)
3. Zaif tomoni (1 gap)
4. Tavsiya (1 gap) — nima qilsin keyingi?

Mehribon, rag'batlantiruvchi ohangda yoz. O'zbek tilida. 4 gapdan ko'p bo'lmasin.
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "AI tahlil hozir mavjud emas."
```

### ai_assistant/views.py

```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .utils import ai_teacher_response
import json

@login_required
@require_POST
def ai_chat_view(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()

        if not question:
            return JsonResponse({'error': 'Savol bo\'sh'}, status=400)

        if len(question) > 500:
            return JsonResponse({'error': 'Savol juda uzun'}, status=400)

        answer = ai_teacher_response(question, request.user.id)
        return JsonResponse({'answer': answer})

    except Exception as e:
        return JsonResponse({'error': 'Xato yuz berdi'}, status=500)
```

---

## URL Tuzilmasi

### config/urls.py

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    path('users/', include('users.urls')),
    path('quiz/', include('quiz.urls')),
    path('ai/', include('ai_assistant.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Barcha URL lar

| URL | Nima qiladi |
|-----|------------|
| `/` | Landing page — bosh sahifa |
| `/users/register/` | Ro'yxatdan o'tish |
| `/users/login/` | Kirish |
| `/users/logout/` | Chiqish |
| `/dashboard/` | O'quvchi dashboard |
| `/courses/` | Kurslar ro'yxati |
| `/courses/<id>/` | Kurs detail |
| `/courses/<id>/enroll/` | Kursga yozilish |
| `/lessons/<id>/` | Dars o'qish |
| `/quiz/<id>/` | Test ishlash |
| `/quiz/result/<id>/` | Test natijasi |
| `/ai/chat/` | AI muallim API |
| `/admin/` | Admin panel |

---

## Template Tuzilmasi

```
templates/
├── base.html              # Asosiy template (navbar, footer)
├── home.html              # Landing page
├── users/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── courses/
│   ├── course_list.html
│   ├── course_detail.html
│   └── lesson_detail.html
└── quiz/
    ├── quiz.html
    └── result.html
```

### base.html tuzilmasi

```html
<!DOCTYPE html>
<html lang="uz">
<head>
    {% load static %}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}EduTJ{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/bootstrap.min.css' %}">
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    {% include 'navbar.html' %}

    <main>
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    {% include 'footer.html' %}

    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 3 Til Tizimi

Har bir modelda `_tj`, `_ru`, `_en` maydonlar mavjud.

Template da til tanlash:

```html
<!-- Til tugmalari -->
<div class="lang-switcher">
    <a href="?lang=uz" class="{% if lang == 'uz' %}active{% endif %}">UZ</a>
    <a href="?lang=tj" class="{% if lang == 'tj' %}active{% endif %}">TJ</a>
    <a href="?lang=ru" class="{% if lang == 'ru' %}active{% endif %}">RU</a>
    <a href="?lang=en" class="{% if lang == 'en' %}active{% endif %}">EN</a>
</div>

<!-- Kontent ko'rsatish -->
{% if lang == 'tj' %}
    {{ lesson.content_tj }}
{% elif lang == 'ru' %}
    {{ lesson.content_ru }}
{% elif lang == 'en' %}
    {{ lesson.content_en }}
{% else %}
    {{ lesson.content }}
{% endif %}
```

---

## Admin Panel Sozlash

```python
# courses/admin.py
from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'teacher', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_completed']
```

---

## Musobaqa Shartlariga Moslik

| Shart | Holat |
|-------|-------|
| Veb dasturlash yo'nalishi | ✅ To'liq mos |
| Axborot va ma'lumot xususiyati | ✅ Ta'lim platforma |
| HTML, CSS, JavaScript | ✅ Bootstrap + JS |
| MySQL | ✅ Ishlatilgan |
| 3 tilda (TJ, RU, EN) | ✅ Barcha sahifalarda |
| Qulay navigatsiya | ✅ Sidebar + Navbar |
| Dizayn sifati | ✅ Bootstrap 5 |
| Novatorlik | ✅ AI Muallim + Progress Tahlil |

---

## Qo'shimcha Eslatmalar

- Har missiya tugagach `python manage.py check` ishlatib tekshiring
- Har kuni `git commit` qilib boring — ishingiz yo'qolmasin
- `.env` faylni hech qachon GitHub ga yuklamang
- Musobaqada admin panelni ham ko'rsating — hakamlar ta'sirlanadi
- Demo ma'lumotlar qo'shing — bo'sh sayt yaxshi ko'rinmaydi

---

## Muallif

**Muhammad Rizo** — Python Backend Developer  
Django | MySQL | AI Integration  
Tojikiston — "Yosh Dasturchi Olimpiadasi" 2025