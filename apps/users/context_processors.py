"""
معالج السياق للإشعارات - يعمل على جميع الصفحات
يوفر إشعارات الجلسات القادمة والقضايا المفتوحة للمحامي المسجّل
"""
from apps.cases.models import Case, Session
from datetime import date, timedelta


def notifications(request):
    """إرجاع الإشعارات للمستخدم الحالي في كل الصفحات"""
    if not request.user.is_authenticated:
        return {}

    today = date.today()
    notifs = []

    # ===== للمحامي: إشعارات قضاياه فقط =====
    if request.user.role in ('lawyer', 'admin'):

        # جلسات اليوم
        today_sessions = Session.objects.filter(
            session_date=today,
            status='scheduled',
            case__assigned_lawyer=request.user
        ).select_related('case', 'case__company') if request.user.role == 'lawyer' else Session.objects.filter(
            session_date=today,
            status='scheduled'
        ).select_related('case', 'case__company')

        for s in today_sessions:
            notifs.append({
                'type': 'danger',
                'icon': 'fa-calendar-day',
                'title': f'جلسة اليوم — القضية {s.case.case_number}',
                'body': s.case.company.name,
                'url': f'/cases/{s.case.pk}/',
                'priority': 1,
            })

        # جلسات خلال 3 أيام
        soon = today + timedelta(days=3)
        soon_sessions = Session.objects.filter(
            session_date__gt=today,
            session_date__lte=soon,
            status='scheduled',
            case__assigned_lawyer=request.user
        ).select_related('case', 'case__company') if request.user.role == 'lawyer' else Session.objects.filter(
            session_date__gt=today,
            session_date__lte=soon,
            status='scheduled'
        ).select_related('case', 'case__company')

        for s in soon_sessions:
            days_left = (s.session_date - today).days
            notifs.append({
                'type': 'warning',
                'icon': 'fa-clock',
                'title': f'جلسة بعد {days_left} يوم — القضية {s.case.case_number}',
                'body': f'{s.case.company.name} • {s.session_date.strftime("%d/%m/%Y")}',
                'url': f'/cases/{s.case.pk}/',
                'priority': 2,
            })

        # قضايا مفتوحة مُعيَّنة للمحامي
        if request.user.role == 'lawyer':
            open_cases = Case.objects.filter(
                assigned_lawyer=request.user,
                status='open'
            ).select_related('company')[:5]
            for c in open_cases:
                next_s = c.next_session
                if next_s:
                    days_left = (next_s.session_date - today).days
                    if days_left <= 7:
                        notifs.append({
                            'type': 'info',
                            'icon': 'fa-gavel',
                            'title': f'قضية مفتوحة — {c.case_number}',
                            'body': f'{c.company.name} • الجلسة القادمة: {next_s.session_date.strftime("%d/%m/%Y")}',
                            'url': f'/cases/{c.pk}/',
                            'priority': 3,
                        })

    # للموظف: إشعارات الجلسات العامة القادمة فقط
    elif request.user.role == 'employee':
        today_sessions = Session.objects.filter(
            session_date=today,
            status='scheduled'
        ).select_related('case', 'case__company')[:3]
        for s in today_sessions:
            notifs.append({
                'type': 'warning',
                'icon': 'fa-calendar',
                'title': f'جلسة اليوم — {s.case.case_number}',
                'body': s.case.company.name,
                'url': f'/cases/{s.case.pk}/',
                'priority': 2,
            })

    # ترتيب حسب الأولوية
    notifs.sort(key=lambda x: x['priority'])

    return {
        'notifications': notifs,
        'notif_count': len(notifs),
    }
