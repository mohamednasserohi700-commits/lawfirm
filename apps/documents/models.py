"""
نماذج تطبيق المستندات
"""
import os
from django.db import models
from django.core.exceptions import ValidationError
from apps.users.models import CustomUser
from apps.companies.models import Company
from apps.cases.models import Case


def validate_file_extension(value):
    """التحقق من نوع الملف المرفوع"""
    allowed = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.xlsx', '.xls']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed:
        raise ValidationError(f'نوع الملف غير مسموح به. الأنواع المسموحة: {", ".join(allowed)}')


def validate_file_size(value):
    """التحقق من حجم الملف"""
    max_size = 10 * 1024 * 1024  # 10 MB
    if value.size > max_size:
        raise ValidationError('حجم الملف يتجاوز الحد المسموح به (10 ميجابايت).')


def upload_path(instance, filename):
    """تحديد مسار رفع الملف"""
    if instance.company:
        return f'documents/companies/{instance.company.pk}/{filename}'
    elif instance.case:
        return f'documents/cases/{instance.case.pk}/{filename}'
    return f'documents/general/{filename}'


class Document(models.Model):
    """نموذج المستند / الملف"""

    class FileType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        WORD = 'word', 'Word'
        IMAGE = 'image', 'صورة'
        EXCEL = 'excel', 'Excel'
        OTHER = 'other', 'أخرى'

    title = models.CharField(max_length=200, verbose_name='عنوان المستند')
    file = models.FileField(
        upload_to=upload_path,
        validators=[validate_file_extension, validate_file_size],
        verbose_name='الملف'
    )
    file_type = models.CharField(
        max_length=20, choices=FileType.choices,
        default=FileType.OTHER, verbose_name='نوع الملف'
    )
    # ربط المستند بشركة أو قضية (اختياري)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True,
        related_name='documents', verbose_name='الشركة'
    )
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=True, blank=True,
        related_name='documents', verbose_name='القضية'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    uploaded_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name='uploaded_documents', verbose_name='رُفع بواسطة'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')

    class Meta:
        verbose_name = 'مستند'
        verbose_name_plural = 'المستندات'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def get_file_icon(self):
        """إرجاع أيقونة مناسبة لنوع الملف"""
        icons = {
            'pdf': 'fa-file-pdf text-danger',
            'word': 'fa-file-word text-primary',
            'image': 'fa-file-image text-success',
            'excel': 'fa-file-excel text-success',
            'other': 'fa-file text-secondary',
        }
        return icons.get(self.file_type, 'fa-file text-secondary')

    def get_file_size_display(self):
        """عرض حجم الملف بشكل مقروء"""
        try:
            size = self.file.size
            if size < 1024:
                return f'{size} بايت'
            elif size < 1024 * 1024:
                return f'{size / 1024:.1f} كيلوبايت'
            else:
                return f'{size / (1024 * 1024):.1f} ميجابايت'
        except Exception:
            return 'غير معروف'

    def save(self, *args, **kwargs):
        """تحديد نوع الملف تلقائياً عند الحفظ"""
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext == '.pdf':
                self.file_type = self.FileType.PDF
            elif ext in ['.doc', '.docx']:
                self.file_type = self.FileType.WORD
            elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                self.file_type = self.FileType.IMAGE
            elif ext in ['.xls', '.xlsx']:
                self.file_type = self.FileType.EXCEL
            else:
                self.file_type = self.FileType.OTHER
        super().save(*args, **kwargs)
