"""
أمر إنشاء مستخدم أدمن
python manage.py create_admin
"""
import os
from django.core.management.base import BaseCommand
from apps.users.models import CustomUser


class Command(BaseCommand):
    help = 'إنشاء مستخدم أدمن'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--password', type=str, default='Admin@2026')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        if CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.get(username=username)
            user.set_password(password)
            user.role = 'admin'
            user.is_active = True
            user.save(update_fields=['password', 'role', 'is_active'])
            self.stdout.write(self.style.WARNING(f'✓ تم تحديث الأدمن: {username}'))
        else:
            user = CustomUser(
                username=username,
                role='admin',
                is_active=True,
            )
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ تم إنشاء الأدمن: {username}'))

        self.stdout.write(self.style.SUCCESS(f'✓ اسم المستخدم: {username}'))
        self.stdout.write(self.style.SUCCESS(f'✓ كلمة المرور: {password}'))
