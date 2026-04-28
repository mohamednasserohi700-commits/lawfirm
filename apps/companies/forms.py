"""
نماذج تطبيق الشركات
"""
from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):
    """نموذج إضافة / تعديل شركة"""

    class Meta:
        model = Company
        fields = ('name', 'client_name', 'phone', 'email', 'address', 'notes')
        labels = {
            'name': 'اسم الشركة',
            'client_name': 'اسم العميل',
            'phone': 'رقم الهاتف',
            'email': 'البريد الإلكتروني',
            'address': 'العنوان',
            'notes': 'ملاحظات',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم الشركة'
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم العميل'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 0501234567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@domain.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل العنوان الكامل'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'أي ملاحظات إضافية...'
            }),
        }
