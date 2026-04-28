"""
عروض تطبيق الشركات
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Company
from .forms import CompanyForm
from apps.cases.models import Case
from apps.documents.models import Document
from apps.documents.forms import DocumentForm


@login_required
def company_list(request):
    """قائمة الشركات مع البحث"""
    query = request.GET.get('q', '')
    companies = Company.objects.all()
    if query:
        companies = companies.filter(
            Q(name__icontains=query) |
            Q(client_name__icontains=query) |
            Q(phone__icontains=query)
        )
    companies = companies.order_by('-created_at')
    return render(request, 'companies/company_list.html', {
        'companies': companies,
        'query': query,
    })


@login_required
def company_detail(request, pk):
    """تفاصيل شركة مع قضاياها ومستنداتها"""
    company = get_object_or_404(Company, pk=pk)
    cases = company.cases.all().order_by('-created_at')
    documents = company.documents.all().order_by('-uploaded_at')
    doc_form = DocumentForm()
    return render(request, 'companies/company_detail.html', {
        'company': company,
        'cases': cases,
        'documents': documents,
        'doc_form': doc_form,
    })


@login_required
def company_create(request):
    """إضافة شركة جديدة"""
    if not request.user.can_edit:
        messages.error(request, 'ليس لديك صلاحية لإضافة شركات.')
        return redirect('company_list')
    form = CompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        company = form.save(commit=False)
        company.created_by = request.user
        company.save()
        messages.success(request, f'تم إضافة الشركة "{company.name}" بنجاح.')
        return redirect('company_detail', pk=company.pk)
    return render(request, 'companies/company_form.html', {
        'form': form,
        'title': 'إضافة شركة جديدة',
    })


@login_required
def company_edit(request, pk):
    """تعديل بيانات شركة"""
    if not request.user.can_edit:
        messages.error(request, 'ليس لديك صلاحية لتعديل الشركات.')
        return redirect('company_list')
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(request.POST or None, instance=company)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'تم تعديل بيانات الشركة "{company.name}" بنجاح.')
        return redirect('company_detail', pk=company.pk)
    return render(request, 'companies/company_form.html', {
        'form': form,
        'title': f'تعديل: {company.name}',
        'company': company,
    })


@login_required
def company_delete(request, pk):
    """حذف شركة"""
    if not request.user.can_delete:
        messages.error(request, 'ليس لديك صلاحية لحذف الشركات.')
        return redirect('company_list')
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        name = company.name
        company.delete()
        messages.success(request, f'تم حذف الشركة "{name}" بنجاح.')
        return redirect('company_list')
    return render(request, 'companies/company_confirm_delete.html', {'company': company})
