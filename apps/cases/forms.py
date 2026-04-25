"""
نماذج تطبيق القضايا
"""
from django import forms
from .models import Case, Session
from apps.users.models import CustomUser


class CaseForm(forms.ModelForm):
    """نموذج إضافة / تعديل قضية"""

    class Meta:
        model = Case
        fields = ('case_number', 'court_name', 'case_type', 'opponent_name',
                  'status', 'assigned_lawyer', 'notes')
        labels = {
            'case_number': 'رقم القضية',
            'court_name': 'اسم المحكمة',
            'case_type': 'نوع القضية',
            'opponent_name': 'اسم الخصم',
            'status': 'حالة القضية',
            'assigned_lawyer': 'المحامي المسؤول',
            'notes': 'ملاحظات',
        }
        widgets = {
            'case_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم القضية'}),
            'court_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المحكمة'}),
            'case_type': forms.Select(attrs={'class': 'form-select'}),
            'opponent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الخصم'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_lawyer': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # عرض المحامين فقط في القائمة
        self.fields['assigned_lawyer'].queryset = CustomUser.objects.filter(
            role__in=['admin', 'lawyer']
        )
        self.fields['assigned_lawyer'].empty_label = '--- اختر المحامي ---'


class SessionForm(forms.ModelForm):
    """نموذج إضافة / تعديل جلسة"""

    class Meta:
        model = Session
        fields = ('session_date', 'status', 'notes')
        labels = {
            'session_date': 'تاريخ الجلسة',
            'status': 'حالة الجلسة',
            'notes': 'ملاحظات الجلسة',
        }
        widgets = {
            'session_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
