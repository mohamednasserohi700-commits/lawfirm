"""
عروض تطبيق المستندات
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
import os
from .models import Document
from .forms import DocumentForm
from apps.companies.models import Company
from apps.cases.models import Case


@login_required
def document_list(request):
    """قائمة جميع المستندات"""
    documents = Document.objects.select_related('company', 'case', 'uploaded_by').order_by('-uploaded_at')
    return render(request, 'documents/document_list.html', {'documents': documents})


@login_required
def document_upload_company(request, company_pk):
    """رفع مستند لشركة"""
    company = get_object_or_404(Company, pk=company_pk)
    form = DocumentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save(commit=False)
        doc.company = company
        doc.uploaded_by = request.user
        doc.save()
        messages.success(request, f'تم رفع المستند "{doc.title}" بنجاح.')
        return redirect('company_detail', pk=company_pk)
    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': f'رفع مستند - {company.name}',
        'back_url': f'/companies/{company_pk}/',
    })


@login_required
def document_upload_case(request, case_pk):
    """رفع مستند لقضية"""
    case = get_object_or_404(Case, pk=case_pk)
    form = DocumentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save(commit=False)
        doc.case = case
        doc.uploaded_by = request.user
        doc.save()
        messages.success(request, f'تم رفع المستند "{doc.title}" بنجاح.')
        return redirect('case_detail', pk=case_pk)
    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': f'رفع مستند - القضية {case.case_number}',
        'back_url': f'/cases/{case_pk}/',
    })


@login_required
def document_download(request, pk):
    """تحميل مستند"""
    doc = get_object_or_404(Document, pk=pk)
    try:
        response = FileResponse(doc.file.open('rb'), as_attachment=True, filename=os.path.basename(doc.file.name))
        return response
    except FileNotFoundError:
        raise Http404('الملف غير موجود.')


@login_required
def document_delete(request, pk):
    """حذف مستند"""
    doc = get_object_or_404(Document, pk=pk)
    if not request.user.can_delete:
        messages.error(request, 'ليس لديك صلاحية لحذف المستندات.')
    elif request.method == 'POST':
        # تحديد صفحة الرجوع
        back_pk = doc.company.pk if doc.company else (doc.case.pk if doc.case else None)
        back_type = 'company' if doc.company else ('case' if doc.case else None)
        title = doc.title
        # حذف الملف الفعلي من القرص
        if doc.file and os.path.isfile(doc.file.path):
            os.remove(doc.file.path)
        doc.delete()
        messages.success(request, f'تم حذف المستند "{title}" بنجاح.')
        if back_type == 'company':
            return redirect('company_detail', pk=back_pk)
        elif back_type == 'case':
            return redirect('case_detail', pk=back_pk)
        return redirect('document_list')
    return render(request, 'documents/document_confirm_delete.html', {'doc': doc})
