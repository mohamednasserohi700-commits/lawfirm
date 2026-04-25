"""
عروض تطبيق المستخدمين
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CustomUser
from .forms import ArabicLoginForm, UserCreateForm, UserEditForm
from apps.companies.models import Company
from apps.cases.models import Case, Session
from datetime import date, timedelta


def login_view(request):
    """صفحة تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ArabicLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'مرحباً {form.get_user().get_full_name() or form.get_user().username}!')
        return redirect('dashboard')
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('login')


@login_required
def user_list(request):
    """قائمة المستخدمين - للمدير فقط"""
    if not request.user.is_admin:
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة.')
        return redirect('dashboard')
    users = CustomUser.objects.all().order_by('-created_at')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def user_create(request):
    """إنشاء مستخدم جديد - للمدير فقط"""
    if not request.user.is_admin:
        messages.error(request, 'ليس لديك صلاحية لإضافة مستخدمين.')
        return redirect('dashboard')
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم إنشاء المستخدم بنجاح.')
        return redirect('user_list')
    return render(request, 'users/user_form.html', {'form': form, 'title': 'إضافة مستخدم جديد'})


@login_required
def user_edit(request, pk):
    """تعديل بيانات مستخدم"""
    if not request.user.is_admin:
        messages.error(request, 'ليس لديك صلاحية لتعديل المستخدمين.')
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم تعديل بيانات المستخدم بنجاح.')
        return redirect('user_list')
    return render(request, 'users/user_form.html', {'form': form, 'title': 'تعديل بيانات المستخدم', 'user_obj': user})


@login_required
def user_delete(request, pk):
    """حذف مستخدم"""
    if not request.user.is_admin:
        messages.error(request, 'ليس لديك صلاحية لحذف المستخدمين.')
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'لا يمكنك حذف حسابك الخاص.')
        else:
            user.delete()
            messages.success(request, 'تم حذف المستخدم بنجاح.')
        return redirect('user_list')
    return render(request, 'users/user_confirm_delete.html', {'user_obj': user})
