"""
نماذج تطبيق الشركات
"""
from django.db import models
from apps.users.models import CustomUser


class Company(models.Model):
    """نموذج الشركة / العميل"""

    name = models.CharField(max_length=200, verbose_name='اسم الشركة')
    client_name = models.CharField(max_length=200, verbose_name='اسم العميل')
    phone = models.CharField(max_length=20, blank=True, verbose_name='رقم الهاتف')
    email = models.EmailField(blank=True, verbose_name='البريد الإلكتروني')
    address = models.TextField(blank=True, verbose_name='العنوان')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name='created_companies', verbose_name='أنشأه'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')

    class Meta:
        verbose_name = 'شركة'
        verbose_name_plural = 'الشركات'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.client_name}"

    @property
    def open_cases_count(self):
        return self.cases.filter(status='open').count()

    @property
    def total_cases_count(self):
        return self.cases.count()
