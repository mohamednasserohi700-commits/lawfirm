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

ROLE_DEVELOPER = CustomUser.Role.DEVELOPER
ROLE_ADMIN = CustomUser.Role.ADMIN


def _can_access_user_admin(request_user):
    return request_user.is_real_admin or request_user.is_developer


def _can_manage_target_user(request_user, target_user):
    """قواعد الإدارة:
    - المطور يدير الجميع ما عدا المطورين.
    - الأدمن يدير الجميع ما عدا المطورين.
    """
    if target_user.role == ROLE_DEVELOPER:
        return False
    if request_user.is_developer:
        return True
    if request_user.is_real_admin:
        return True
    return False


# ==================== تسجيل الدخول والخروج ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ArabicLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'مرحباً {form.get_user().get_full_name() or form.get_user().username}!')
        return redirect('dashboard')
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        CustomUser.objects.filter(pk=request.user.pk).update(is_online=False)
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('users:login')


# ==================== إدارة المستخدمين (للأدمن) ====================

@login_required
def user_list(request):
    if not _can_access_user_admin(request.user):
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة.')
        return redirect('dashboard')
    # المطور يرى جميع الحسابات (بما فيها حساب المطور)
    # باقي المستخدمين لا يرون حساب المطور
    if request.user.is_developer:
        users = CustomUser.objects.all()
    else:
        users = CustomUser.objects.exclude(role=ROLE_DEVELOPER)
    users = users.order_by('-created_at')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def user_create(request):
    if not _can_access_user_admin(request.user):
        messages.error(request, 'ليس لديك صلاحية لإضافة مستخدمين.')
        return redirect('dashboard')
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم إنشاء المستخدم بنجاح.')
        return redirect('users:user_list')
    return render(request, 'users/user_form.html', {'form': form, 'title': 'إضافة مستخدم جديد'})


@login_required
def user_edit(request, pk):
    if not _can_access_user_admin(request.user):
        messages.error(request, 'ليس لديك صلاحية لتعديل المستخدمين.')
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if not _can_manage_target_user(request.user, user):
        messages.error(request, 'لا يمكنك تعديل هذا المستخدم.')
        return redirect('users:user_list')
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم تعديل بيانات المستخدم والصلاحيات بنجاح.')
        return redirect('users:user_list')
    return render(request, 'users/user_form.html', {'form': form, 'title': 'تعديل بيانات المستخدم', 'user_obj': user})


@login_required
def user_delete(request, pk):
    if not _can_access_user_admin(request.user):
        messages.error(request, 'ليس لديك صلاحية لحذف المستخدمين.')
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if not _can_manage_target_user(request.user, user):
        messages.error(request, 'لا يمكنك حذف هذا المستخدم.')
        return redirect('users:user_list')
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'لا يمكنك حذف حسابك الخاص.')
        else:
            user.delete()
            messages.success(request, 'تم حذف المستخدم بنجاح.')
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_delete.html', {'user_obj': user})


@login_required
def admin_change_password(request, pk):
    if not _can_access_user_admin(request.user):
        messages.error(request, 'ليس لديك صلاحية.')
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, pk=pk)
    if not _can_manage_target_user(request.user, user):
        messages.error(request, 'لا يمكنك تغيير كلمة مرور هذا المستخدم.')
        return redirect('users:user_list')
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        if len(new_password) >= 6:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'تم تغيير كلمة مرور {user.username} بنجاح.')
            return redirect('users:user_list')
        else:
            messages.error(request, 'كلمة المرور يجب أن تكون 6 أحرف على الأقل.')
    return render(request, 'users/change_password.html', {'user_obj': user})


# ==================== صفحة المتصلين ====================

@login_required
def online_users_view(request):
    """صفحة المتصلين - للأدمن والمطور + من منحهم صلاحية"""
    if not (request.user.is_real_admin or request.user.is_developer or request.user.can_view_online):
        messages.error(request, 'ليس لديك صلاحية للوصول إلى هذه الصفحة.')
        return redirect('dashboard')

    all_users = CustomUser.objects.exclude(role='developer').order_by('-is_online', '-last_seen')

    if request.method == 'POST':
        user_pk = request.POST.get('user_pk')
        action = request.POST.get('action')
        target = get_object_or_404(CustomUser, pk=user_pk)
        if not target.is_developer:
            if action == 'grant':
                target.can_view_online = True
                target.save()
                messages.success(request, f'تم منح {target.username} صلاحية مشاهدة المتصلين.')
            elif action == 'revoke':
                target.can_view_online = False
                target.save()
                messages.success(request, f'تم سحب صلاحية {target.username}.')
            elif action == 'force_logout':
                # تسجيل خروج إجباري - مسح السيشن وتحديث الحالة
                from django.contrib.sessions.models import Session
                from django.utils import timezone as tz
                # مسح كل السيشنز النشطة للمستخدم
                active_sessions = Session.objects.filter(expire_date__gte=tz.now())
                for session in active_sessions:
                    data = session.get_decoded()
                    if str(data.get('_auth_user_id')) == str(target.pk):
                        session.delete()
                # تحديث حالة الاتصال
                CustomUser.objects.filter(pk=target.pk).update(is_online=False)
                messages.success(request, f'تم تسجيل خروج {target.username} بنجاح.')
        return redirect('users:online_users')

    return render(request, 'users/online_users.html', {'all_users': all_users})


# ==================== لوحة تحكم المطور ====================

def developer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_developer:
            return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@developer_required
def developer_panel(request):
    all_users = CustomUser.objects.all().order_by('-last_seen')
    online_users = all_users.filter(is_online=True)
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
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        if len(new_password) >= 6:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'تم تغيير كلمة مرور {user.username} بنجاح.')
        else:
            messages.error(request, 'كلمة المرور يجب أن تكون 6 أحرف على الأقل.')
    return redirect('users:developer_panel')


@developer_required
def developer_toggle_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if not user.is_developer:
        user.is_active = not user.is_active
        user.save()
        # لو تعطيل — مسح السيشن
        if not user.is_active:
            from django.contrib.sessions.models import Session
            from django.utils import timezone as tz
            active_sessions = Session.objects.filter(expire_date__gte=tz.now())
            for session in active_sessions:
                data = session.get_decoded()
                if str(data.get('_auth_user_id')) == str(user.pk):
                    session.delete()
            CustomUser.objects.filter(pk=user.pk).update(is_online=False)
        status = 'تفعيل' if user.is_active else 'تعطيل'
        messages.success(request, f'تم {status} المستخدم {user.username}.')
    return redirect('users:developer_panel')


# ==================== إدارة صلاحيات المستخدم ====================

@login_required
def user_permissions(request, pk):
    """صفحة صلاحيات مستخدم - للأدمن والمطور حسب القواعد"""
    if not _can_access_user_admin(request.user):
        messages.error(request, 'ليس لديك صلاحية.')
        return redirect('dashboard')
    target = get_object_or_404(CustomUser, pk=pk)
    if not _can_manage_target_user(request.user, target):
        return redirect('users:user_list')

    PERMISSIONS = [
        ('can_view_online', 'مشاهدة المتصلين'),
        ('can_edit_manual', 'صلاحية تعديل يدوية'),
        ('can_delete_manual', 'صلاحية حذف يدوية'),
        ('can_manage_users_manual', 'إدارة المستخدمين يدويًا'),
    ]

    if request.method == 'POST':
        for perm, _ in PERMISSIONS:
            val = request.POST.get(perm) == 'on'
            setattr(target, perm, val)
        target.save()
        messages.success(request, f'تم تحديث صلاحيات {target.username} بنجاح.')
        return redirect('users:user_permissions', pk=pk)

    if request.user.is_developer:
        users = CustomUser.objects.all()
    else:
        users = CustomUser.objects.exclude(role=ROLE_DEVELOPER)
    users = users.order_by('-created_at')
    return render(request, 'users/user_list.html', {
        'users': users,
        'selected_user': target,
        'PERMISSIONS': PERMISSIONS,
    })
