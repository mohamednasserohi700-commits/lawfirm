"""
أمر إنشاء مستخدم المطور
python manage.py create_developer
"""
import os
from django.core.management.base import BaseCommand
from apps.users.models import CustomUser


class Command(BaseCommand):
    help = 'إنشاء مستخدم المطور المخفي'

    def handle(self, *args, **options):
        username = 'administrator'
        password = os.environ.get('DEV_PASSWORD', '3000330210')

        if CustomUser.objects.filter(username=username).exists():
            dev = CustomUser.objects.get(username=username)
            dev.set_password(password)
            dev.role = 'developer'
            dev.is_staff = False
            dev.is_superuser = False
            dev.is_active = True
            dev.save(update_fields=['password', 'role', 'is_staff', 'is_superuser', 'is_active'])
            self.stdout.write(self.style.WARNING(f'✓ تم تحديث مستخدم المطور: {username}'))
        else:
            dev = CustomUser(
                username=username,
                role='developer',
                is_staff=False,
                is_superuser=False,
                is_active=True,
            )
            dev.set_password(password)  # يتجاوز الـ validators
            dev.save()
            self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء مستخدم المطور: {username}'))

        self.stdout.write(self.style.SUCCESS(f'✓ اسم المستخدم: {username}'))
        self.stdout.write(self.style.SUCCESS(f'✓ كلمة المرور: {password}'))
