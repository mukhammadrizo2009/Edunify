from django.core.management.base import BaseCommand
from users.models import CustomUser
from courses.models import Category, Course, Lesson
from quiz.models import Quiz, Question

class Command(BaseCommand):
    help = 'Baza uchun demo ma\'lumotlarni yuklaydi'

    def handle(self, *args, **kwargs):
        self.stdout.write('Demo ma\'lumotlarni yuklash boshlandi...')

        # 1. Superuser va Teacher yaratish
        teacher, created = CustomUser.objects.get_or_create(
            username='admin',
            email='admin@edunify.uz',
            defaults={
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'bio': 'Edunify loyihasining bosh administratori va muallifi.'
            }
        )
        if created:
            teacher.set_password('admin123')
            teacher.save()
            self.stdout.write('Superuser yaratildi: admin (parol: admin123)')
        else:
            self.stdout.write('Superuser allaqachon mavjud.')

        # 2. Kategoriyalar yaratish
        math_cat, _ = Category.objects.get_or_create(name='Matematika', defaults={'icon': '📐', 'name_tj': 'Математика', 'name_ru': 'Математика', 'name_en': 'Mathematics'})
        phys_cat, _ = Category.objects.get_or_create(name='Fizika', defaults={'icon': '⚡', 'name_tj': 'Физика', 'name_ru': 'Физика', 'name_en': 'Physics'})
        eng_cat, _ = Category.objects.get_or_create(name='Ingliz Tili', defaults={'icon': '🇬🇧', 'name_tj': 'Забони англисӣ', 'name_ru': 'Английский язык', 'name_en': 'English Language'})

        # 3. Kurslar yaratish
        c1, _ = Course.objects.get_or_create(
            title='Algebra Asoslari',
            defaults={
                'category': math_cat,
                'teacher': teacher,
                'description': 'Ushbu kurs algebraik ifodalar, tenglamalar va funksiyalarni o\'z ichiga oladi.',
                'title_tj': 'Асосҳои алгебра',
                'description_tj': 'Ин курс ибораҳои алгебравӣ, муодилаҳо ва функсияҳоро дар бар мегирад.',
                'title_ru': 'Основы алгебры',
                'description_ru': 'Этот курс охватывает алгебраические выражения, уравнения и функции.',
                'title_en': 'Basics of Algebra',
                'description_en': 'This course covers algebraic expressions, equations, and functions.'
            }
        )

        c2, _ = Course.objects.get_or_create(
            title='Kvant Fizikasi',
            defaults={
                'category': phys_cat,
                'teacher': teacher,
                'description': 'Kvant dunyosining g\'aroyib qonunlari va elementar zarralar fizikasi.',
                'title_tj': 'Физикаи квантӣ',
                'description_tj': 'Қонунҳои аҷиби ҷаҳони квантӣ ва физикаи зарраҳои элементарӣ.',
                'title_ru': 'Квантовая физика',
                'description_ru': 'Удивительные законы квантового мира и физика элементарных частиц.',
                'title_en': 'Quantum Physics',
                'description_en': 'Amazing laws of the quantum world and elementary particle physics.'
            }
        )

        # 4. Darslar yaratish
        l1, _ = Lesson.objects.get_or_create(
            course=c1,
            title='Tenglamalar va ularni yechish',
            defaults={
                'content': 'Tenglama — bu noma\'lum qatnashgan tenglikdir. Chiziqli tenglamalarni yechish uchun noma\'lumlarni bir tomonga, ma\'lumlarni ikkinchi tomonga o\'tkazamiz.',
                'title_tj': 'Муодилаҳо ва ҳалли онҳо',
                'content_tj': 'Муодила баробариест, ки дар он номаълум иштирок мекунад. Барои ҳалли муодилаҳои хаттӣ номаълумҳоро ба як тараф ва маълумҳоро ба тарафи дигар мегузаронем.',
                'title_ru': 'Уравнения и их решения',
                'content_ru': 'Уравнение — это равенство, содержащее неизвестное. Для решения линейных уравнений переносим неизвестные в одну сторону, известные — в другую.',
                'title_en': 'Equations and Their Solutions',
                'content_en': 'An equation is an equality containing an unknown. To solve linear equations, we transfer unknowns to one side and knowns to the other.',
                'order': 1
            }
        )

        l2, _ = Lesson.objects.get_or_create(
            course=c1,
            title='Kvadrat tenglamalar',
            defaults={
                'content': 'Kvadrat tenglama ax^2 + bx + c = 0 ko\'rinishida bo\'ladi. Uning yechimlari diskriminant D = b^2 - 4ac orqali topiladi.',
                'title_tj': 'Муодилаҳои квадратӣ',
                'content_tj': 'Муодилаи квадратӣ намуди ax^2 + bx + c = 0-ро дорад. Ҳалли он тавассути дискриминанти D = b^2 - 4ac ёфт мешавад.',
                'title_ru': 'Квадратные уравнения',
                'content_ru': 'Квадратное уравнение имеет вид ax^2 + bx + c = 0. Его решения находятся через дискриминант D = b^2 - 4ac.',
                'title_en': 'Quadratic Equations',
                'content_en': 'A quadratic equation has the form ax^2 + bx + c = 0. Its solutions are found via the discriminant D = b^2 - 4ac.',
                'order': 2
            }
        )

        # 5. Quiz yaratish
        q1, _ = Quiz.objects.get_or_create(
            lesson=l1,
            defaults={
                'title': 'Tenglamalar bo\'yicha test',
                'passing_score': 60
            }
        )

        # 6. Savollar yaratish
        Question.objects.get_or_create(
            quiz=q1,
            text='2x + 5 = 15 tenglamadan x ni toping.',
            defaults={
                'option_a': '5',
                'option_b': '10',
                'option_c': '15',
                'option_d': '20',
                'correct_answer': 'A',
                'order': 1,
                'text_tj': 'Аз муодилаи 2x + 5 = 15 номаълуми x-ро ёбед.',
                'text_ru': 'Найдите x из уравнения 2x + 5 = 15.',
                'text_en': 'Find x from the equation 2x + 5 = 15.'
            }
        )

        Question.objects.get_or_create(
            quiz=q1,
            text='Tenglama nima?',
            defaults={
                'option_a': 'Noma\'lum qatnashgan tenglik',
                'option_b': 'Sonli ifoda',
                'option_c': 'Kvadratlar yig\'indisi',
                'option_d': 'Geometrik shakl',
                'correct_answer': 'A',
                'order': 2,
                'text_tj': 'Муодила чист?',
                'text_ru': 'Что такое уравнение?',
                'text_en': 'What is an equation?'
            }
        )

        Question.objects.get_or_create(
            quiz=q1,
            text='x - 7 = 3 tenglamada x nechaga teng?',
            defaults={
                'option_a': '4',
                'option_b': '10',
                'option_c': '21',
                'option_d': '-4',
                'correct_answer': 'B',
                'order': 3,
                'text_tj': 'Дар муодилаи x - 7 = 3 номаълуми x ба чанд баробар аст?',
                'text_ru': 'Чему равен x в уравнении x - 7 = 3?',
                'text_en': 'What is x equal to in the equation x - 7 = 3?'
            }
        )

        self.stdout.write(self.style.SUCCESS('Demo ma\'lumotlar muvaffaqiyatli yuklandi!'))
