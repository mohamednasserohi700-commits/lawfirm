"""
نماذج تطبيق المستخدمين
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import CustomUser


class ArabicLoginForm(AuthenticationForm):
    """نموذج تسجيل الدخول بالعربية"""
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم المستخدم',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور',
        })
    )


class UserCreateForm(UserCreationForm):
    """نموذج إنشاء مستخدم جديد"""
    first_name = forms.CharField(
        label='الاسم الأول', max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='اسم العائلة', max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='رقم الهاتف', max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        label='الدور الوظيفي',
        choices=CustomUser.Role.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'role', 'password1', 'password2')
        labels = {'username': 'اسم المستخدم'}
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].label = 'تأكيد كلمة المرور'


class UserEditForm(forms.ModelForm):
    """نموذج تعديل بيانات المستخدم"""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'role', 'is_active')
        labels = {
            'first_name': 'الاسم الأول',
            'last_name': 'اسم العائلة',
            'email': 'البريد الإلكتروني',
            'phone': 'رقم الهاتف',
            'role': 'الدور الوظيفي',
            'is_active': 'نشط',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
