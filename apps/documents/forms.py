"""
نماذج تطبيق المستندات
"""
from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    """نموذج رفع مستند"""

    class Meta:
        model = Document
        fields = ('title', 'file', 'notes')
        labels = {
            'title': 'عنوان المستند',
            'file': 'الملف',
            'notes': 'ملاحظات',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل عنوان المستند'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.xlsx,.xls'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ملاحظات اختيارية...'
            }),
        }
