"""
عروض تطبيق القضايا والجلسات
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Case, Session
from .forms import CaseForm, SessionForm
from apps.companies.models import Company
from apps.documents.models import Document
from apps.documents.forms import DocumentForm


@login_required
def case_list(request):
    """قائمة القضايا مع التصفية والبحث"""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    cases = Case.objects.select_related('company', 'assigned_lawyer').all()

    if query:
        cases = cases.filter(
            Q(case_number__icontains=query) |
            Q(company__name__icontains=query) |
            Q(company__client_name__icontains=query) |
            Q(opponent_name__icontains=query) |
            Q(court_name__icontains=query)
        )
    if status_filter:
        cases = cases.filter(status=status_filter)

    cases = cases.order_by('-created_at')
    return render(request, 'cases/case_list.html', {
        'cases': cases,
        'query': query,
        'status_filter': status_filter,
        'status_choices': Case.Status.choices,
    })


@login_required
def case_detail(request, pk):
    """تفاصيل القضية مع الجلسات والمستندات"""
    case = get_object_or_404(Case, pk=pk)
    sessions = case.sessions.all().order_by('-session_date')
    documents = case.documents.all().order_by('-uploaded_at')
    session_form = SessionForm()
    doc_form = DocumentForm()
    return render(request, 'cases/case_detail.html', {
        'case': case,
        'sessions': sessions,
        'documents': documents,
        'session_form': session_form,
        'doc_form': doc_form,
    })


@login_required
def case_create(request, company_pk):
    """إضافة قضية جديدة لشركة"""
    if not request.user.can_edit:
        messages.error(request, 'ليس لديك صلاحية لإضافة قضايا.')
        return redirect('company_list')
    company = get_object_or_404(Company, pk=company_pk)
    form = CaseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        case = form.save(commit=False)
        case.company = company
        case.created_by = request.user
        case.save()
        messages.success(request, f'تم إضافة القضية "{case.case_number}" بنجاح.')
        return redirect('case_detail', pk=case.pk)
    return render(request, 'cases/case_form.html', {
        'form': form,
        'company': company,
        'title': f'إضافة قضية لـ {company.name}',
    })


@login_required
def case_edit(request, pk):
    """تعديل بيانات قضية"""
    if not request.user.can_edit:
        messages.error(request, 'ليس لديك صلاحية لتعديل القضايا.')
        return redirect('case_list')
    case = get_object_or_404(Case, pk=pk)
    form = CaseForm(request.POST or None, instance=case)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'تم تعديل القضية "{case.case_number}" بنجاح.')
        return redirect('case_detail', pk=case.pk)
    return render(request, 'cases/case_form.html', {
        'form': form,
        'case': case,
        'company': case.company,
        'title': f'تعديل القضية: {case.case_number}',
    })


@login_required
def case_delete(request, pk):
    """حذف قضية"""
    if not request.user.can_delete:
        messages.error(request, 'ليس لديك صلاحية لحذف القضايا.')
        return redirect('case_list')
    case = get_object_or_404(Case, pk=pk)
    company_pk = case.company.pk
    if request.method == 'POST':
        number = case.case_number
        case.delete()
        messages.success(request, f'تم حذف القضية "{number}" بنجاح.')
        return redirect('company_detail', pk=company_pk)
    return render(request, 'cases/case_confirm_delete.html', {'case': case})


# ---- الجلسات ----

@login_required
def session_create(request, case_pk):
    """إضافة جلسة لقضية"""
    case = get_object_or_404(Case, pk=case_pk)
    form = SessionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        session = form.save(commit=False)
        session.case = case
        session.created_by = request.user
        session.save()
        messages.success(request, 'تم إضافة الجلسة بنجاح.')
        return redirect('case_detail', pk=case_pk)
    return render(request, 'cases/session_form.html', {
        'form': form,
        'case': case,
        'title': 'إضافة جلسة جديدة',
    })


@login_required
def session_edit(request, pk):
    """تعديل جلسة"""
    session = get_object_or_404(Session, pk=pk)
    if not request.user.can_edit:
        messages.error(request, 'ليس لديك صلاحية لتعديل الجلسات.')
        return redirect('case_detail', pk=session.case.pk)
    form = SessionForm(request.POST or None, instance=session)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'تم تعديل الجلسة بنجاح.')
        return redirect('case_detail', pk=session.case.pk)
    return render(request, 'cases/session_form.html', {
        'form': form,
        'case': session.case,
        'session': session,
        'title': 'تعديل الجلسة',
    })


@login_required
def session_delete(request, pk):
    """حذف جلسة"""
    session = get_object_or_404(Session, pk=pk)
    case_pk = session.case.pk
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'تم حذف الجلسة بنجاح.')
        return redirect('case_detail', pk=case_pk)
    return render(request, 'cases/session_confirm_delete.html', {'session': session})
