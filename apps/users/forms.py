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
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    can_view_online = forms.BooleanField(label='مشاهدة المتصلين', required=False)
    can_edit_manual = forms.BooleanField(label='صلاحية تعديل يدوية', required=False)
    can_delete_manual = forms.BooleanField(label='صلاحية حذف يدوية', required=False)
    can_manage_users_manual = forms.BooleanField(label='إدارة المستخدمين يدويًا', required=False)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'phone', 'role',
            'can_view_online', 'can_edit_manual', 'can_delete_manual', 'can_manage_users_manual',
            'password1', 'password2'
        )
        labels = {'username': 'اسم المستخدم'}
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].label = 'تأكيد كلمة المرور'
        # منع إنشاء حساب مطور من واجهة النظام نهائيا
        self.fields['role'].choices = [
            (value, label)
            for value, label in CustomUser.Role.choices
            if value != CustomUser.Role.DEVELOPER
        ]


class UserEditForm(forms.ModelForm):
    """نموذج تعديل بيانات المستخدم"""
    new_password1 = forms.CharField(
        label='كلمة مرور جديدة',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'اتركها فارغة بدون تغيير'})
    )
    new_password2 = forms.CharField(
        label='تأكيد كلمة المرور الجديدة',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أعد كتابة كلمة المرور'})
    )

    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'email', 'phone', 'role', 'is_active',
            'can_view_online', 'can_edit_manual', 'can_delete_manual', 'can_manage_users_manual'
        )
        labels = {
            'first_name': 'الاسم الأول',
            'last_name': 'اسم العائلة',
            'email': 'البريد الإلكتروني',
            'phone': 'رقم الهاتف',
            'role': 'الدور الوظيفي',
            'is_active': 'نشط',
            'can_view_online': 'مشاهدة المتصلين',
            'can_edit_manual': 'صلاحية تعديل يدوية',
            'can_delete_manual': 'صلاحية حذف يدوية',
            'can_manage_users_manual': 'إدارة المستخدمين يدويًا',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # لا يظهر دور المطور لاي مستخدم داخل واجهات الادارة
        self.fields['role'].choices = [
            (value, label)
            for value, label in CustomUser.Role.choices
            if value != CustomUser.Role.DEVELOPER
        ]

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 or p2:
            if len(p1 or '') < 6:
                self.add_error('new_password1', 'كلمة المرور يجب أن تكون 6 أحرف على الأقل.')
            if p1 != p2:
                self.add_error('new_password2', 'تأكيد كلمة المرور غير متطابق.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
