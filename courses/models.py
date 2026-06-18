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
    LANGUAGE_CHOICES = [
        ('ru', 'Russian'),
        ('tj', 'Tajik'),
        ('en', 'English'),
    ]
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
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
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
