"""
نماذج تطبيق القضايا والجلسات
"""
from django.db import models
from apps.users.models import CustomUser
from apps.companies.models import Company


class Case(models.Model):
    """نموذج القضية"""

    class Status(models.TextChoices):
        OPEN = 'open', 'مفتوحة'
        CLOSED = 'closed', 'مغلقة'
        POSTPONED = 'postponed', 'مؤجلة'

    class CaseType(models.TextChoices):
        COMMERCIAL = 'commercial', 'تجارية'
        CIVIL = 'civil', 'مدنية'
        CRIMINAL = 'criminal', 'جنائية'
        LABOR = 'labor', 'عمالية'
        FAMILY = 'family', 'أسرية'
        ADMINISTRATIVE = 'administrative', 'إدارية'
        OTHER = 'other', 'أخرى'

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='cases', verbose_name='الشركة'
    )
    case_number = models.CharField(max_length=100, verbose_name='رقم القضية')
    court_name = models.CharField(max_length=200, verbose_name='اسم المحكمة')
    case_type = models.CharField(
        max_length=30, choices=CaseType.choices,
        default=CaseType.OTHER, verbose_name='نوع القضية'
    )
    opponent_name = models.CharField(max_length=200, verbose_name='اسم الخصم')
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.OPEN, verbose_name='حالة القضية'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    assigned_lawyer = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_cases', verbose_name='المحامي المسؤول'
    )
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name='created_cases', verbose_name='أنشأه'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')

    class Meta:
        verbose_name = 'قضية'
        verbose_name_plural = 'القضايا'
        ordering = ['-created_at']

    def __str__(self):
        return f"القضية {self.case_number} - {self.company.name}"

    def get_status_badge(self):
        badges = {
            'open': 'badge-success',
            'closed': 'badge-danger',
            'postponed': 'badge-warning',
        }
        return badges.get(self.status, 'badge-secondary')

    @property
    def next_session(self):
        from datetime import date
        return self.sessions.filter(
            session_date__gte=date.today(),
            status='scheduled'
        ).order_by('session_date').first()


class Session(models.Model):
    """نموذج جلسة المحكمة"""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'مجدولة'
        HELD = 'held', 'منعقدة'
        POSTPONED = 'postponed', 'مؤجلة'
        CANCELLED = 'cancelled', 'ملغاة'

    case = models.ForeignKey(
        Case, on_delete=models.CASCADE,
        related_name='sessions', verbose_name='القضية'
    )
    session_date = models.DateField(verbose_name='تاريخ الجلسة')
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.SCHEDULED, verbose_name='حالة الجلسة'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات الجلسة')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name='created_sessions', verbose_name='أنشأه'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'جلسة'
        verbose_name_plural = 'الجلسات'
        ordering = ['-session_date']

    def __str__(self):
        return f"جلسة {self.session_date} - {self.case}"

    def get_status_badge(self):
        badges = {
            'scheduled': 'badge-primary',
            'held': 'badge-success',
            'postponed': 'badge-warning',
            'cancelled': 'badge-danger',
        }
        return badges.get(self.status, 'badge-secondary')
