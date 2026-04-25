"""
عرض لوحة التحكم الرئيسية
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.companies.models import Company
from apps.cases.models import Case, Session
from datetime import date, timedelta


@login_required
def dashboard(request):
    """لوحة التحكم الرئيسية"""
    today = date.today()
    next_week = today + timedelta(days=7)

    # إحصائيات عامة
    total_companies = Company.objects.count()
    open_cases = Case.objects.filter(status='open').count()
    closed_cases = Case.objects.filter(status='closed').count()
    postponed_cases = Case.objects.filter(status='postponed').count()
    total_cases = Case.objects.count()

    # الجلسات القادمة (خلال 7 أيام)
    upcoming_sessions = Session.objects.filter(
        session_date__gte=today,
        session_date__lte=next_week,
        status='scheduled'
    ).select_related('case', 'case__company').order_by('session_date')[:10]

    # أحدث الشركات
    recent_companies = Company.objects.order_by('-created_at')[:5]

    # أحدث القضايا
    recent_cases = Case.objects.select_related('company').order_by('-created_at')[:5]

    # البحث
    search_query = request.GET.get('q', '')
    search_results = None
    if search_query:
        companies_found = Company.objects.filter(
            Q(name__icontains=search_query) |
            Q(client_name__icontains=search_query)
        )
        cases_found = Case.objects.filter(
            Q(case_number__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(company__client_name__icontains=search_query)
        ).select_related('company')
        search_results = {
            'companies': companies_found,
            'cases': cases_found,
            'query': search_query,
        }

    context = {
        'total_companies': total_companies,
        'open_cases': open_cases,
        'closed_cases': closed_cases,
        'postponed_cases': postponed_cases,
        'total_cases': total_cases,
        'upcoming_sessions': upcoming_sessions,
        'recent_companies': recent_companies,
        'recent_cases': recent_cases,
        'search_results': search_results,
        'search_query': search_query,
        'today': today,
    }
    return render(request, 'dashboard.html', context)
