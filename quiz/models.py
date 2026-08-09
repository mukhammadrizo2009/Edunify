from django.db import models
from users.models import CustomUser
from courses.models import Lesson

class Quiz(models.Model):
    LANGUAGE_CHOICES = [
        ('ru', 'Russian'),
        ('tj', 'Tajik'),
        ('en', 'English'),
    ]
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='quizzes/', null=True, blank=True)
    passing_score = models.PositiveIntegerField(default=60)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.title} - Quiz"

    def get_questions_count(self):
        return self.questions.count()

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    text_tj = models.TextField(blank=True)
    text_ru = models.TextField(blank=True)
    text_en = models.TextField(blank=True)
    option_a = models.CharField(max_length=300)
    option_a_ru = models.CharField(max_length=300, blank=True)
    option_a_tj = models.CharField(max_length=300, blank=True)
    option_a_en = models.CharField(max_length=300, blank=True)

    option_b = models.CharField(max_length=300)
    option_b_ru = models.CharField(max_length=300, blank=True)
    option_b_tj = models.CharField(max_length=300, blank=True)
    option_b_en = models.CharField(max_length=300, blank=True)

    option_c = models.CharField(max_length=300)
    option_c_ru = models.CharField(max_length=300, blank=True)
    option_c_tj = models.CharField(max_length=300, blank=True)
    option_c_en = models.CharField(max_length=300, blank=True)

    option_d = models.CharField(max_length=300)
    option_d_ru = models.CharField(max_length=300, blank=True)
    option_d_tj = models.CharField(max_length=300, blank=True)
    option_d_en = models.CharField(max_length=300, blank=True)

    correct_answer = models.CharField(
        max_length=1,
        choices=[('A','A'),('B','B'),('C','C'),('D','D')]
    )
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"

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


# ═══════════════════════════════════════════════
#  STUDENT AI QUIZ — AI bilan mustaqil test
# ═══════════════════════════════════════════════

class StudentAIQuiz(models.Model):
    """Student o'zi tanlagan mavzu bo'yicha AI yaratgan test."""
    LANGUAGE_CHOICES = [
        ('ru', 'Russian'),
        ('tj', 'Tajik'),
        ('en', 'English'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ai_quizzes')
    subject = models.CharField(max_length=200)        # Fan nomi
    topic = models.CharField(max_length=300)           # Mavzu
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    num_questions = models.PositiveIntegerField(default=10)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    questions_data = models.JSONField(default=list)    # AI yaratgan savollar
    score = models.PositiveIntegerField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    wrong_answers = models.JSONField(default=list)     # Noto'g'ri javoblar
    ai_feedback = models.TextField(blank=True)         # AI tahlili va maslahat
    ai_detailed_analysis = models.JSONField(default=dict)  # Batafsil AI tahlil
    time_spent = models.PositiveIntegerField(default=0)    # soniyada
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)

    def __str__(self):
        status = f"{self.get_percentage()}%" if self.is_completed else "In Progress"
        return f"{self.student.username} - {self.subject}: {self.topic} ({status})"
