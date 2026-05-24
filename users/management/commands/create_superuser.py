import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Superuserni env variables orqali yaratadi (Render deploy uchun)'

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv('DJANGO_SUPERUSER_USERNAME', '')
        email    = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_* env variables topilmadi — superuser yaratilmadi.'
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(
                f'Superuser "{username}" allaqachon mavjud — o\'tkazib yuborildi.'
            ))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f'✅ Superuser "{username}" muvaffaqiyatli yaratildi!'
        ))
