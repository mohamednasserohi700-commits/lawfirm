"""
نماذج تطبيق المستخدمين
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        DEVELOPER = 'developer', 'مطور النظام'
        ADMIN = 'admin', 'مدير النظام'
        LAWYER = 'lawyer', 'محامي'
        EMPLOYEE = 'employee', 'موظف'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE, verbose_name='الدور الوظيفي')
    phone = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='صورة الملف الشخصي')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    # تتبع الاتصال
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name='آخر ظهور')
    last_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='آخر IP')
    last_device = models.CharField(max_length=300, blank=True, verbose_name='آخر جهاز')
    is_online = models.BooleanField(default=False, verbose_name='متصل الآن')

    # صلاحية مشاهدة المتصلين - يمنحها الأدمن أو المطور يدوياً
    can_view_online = models.BooleanField(default=False, verbose_name='يمكنه مشاهدة المتصلين')
    # صلاحيات يدوية إضافية يحددها الأدمن/المطور
    can_edit_manual = models.BooleanField(default=False, verbose_name='صلاحية تعديل يدوية')
    can_delete_manual = models.BooleanField(default=False, verbose_name='صلاحية حذف يدوية')
    can_manage_users_manual = models.BooleanField(default=False, verbose_name='صلاحية إدارة المستخدمين يدويا')

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_developer(self):
        return self.role == self.Role.DEVELOPER

    @property
    def is_admin(self):
        return self.role in [self.Role.ADMIN, self.Role.DEVELOPER]

    @property
    def is_real_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_lawyer(self):
        return self.role == self.Role.LAWYER

    @property
    def is_employee(self):
        return self.role == self.Role.EMPLOYEE

    @property
    def can_manage_users(self):
        return self.role in [self.Role.ADMIN, self.Role.DEVELOPER] or self.can_manage_users_manual

    @property
    def can_delete(self):
        return self.role in [self.Role.ADMIN, self.Role.DEVELOPER, self.Role.LAWYER] or self.can_delete_manual

    @property
    def can_edit(self):
        return self.role in [self.Role.ADMIN, self.Role.DEVELOPER, self.Role.LAWYER] or self.can_edit_manual
