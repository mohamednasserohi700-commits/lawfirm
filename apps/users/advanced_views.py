import csv
from datetime import date, timedelta
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.cases.models import (
    ApprovalRequest,
    Case,
    CaseExpense,
    ContractRecord,
    Invoice,
    Lead,
    Session,
)
from apps.companies.models import Company
from apps.documents.models import Document
from apps.users.models import CustomUser
from .advanced_forms import (
    ApprovalRequestForm,
    CaseExpenseForm,
    ContractRecordForm,
    InvoiceForm,
    LeadForm,
)


ADVANCED_PAGES = {
    "calendar": {"title": "التقويم القانوني", "icon": "fa-calendar-days", "accent": "gold"},
    "billing": {"title": "الأتعاب والفواتير", "icon": "fa-file-invoice-dollar", "accent": "gold"},
    "expenses": {"title": "مصروفات القضايا", "icon": "fa-receipt", "accent": "teal"},
    "contracts": {"title": "العقود والاتفاقيات", "icon": "fa-file-signature", "accent": "violet"},
    "archive": {"title": "الأرشفة المتقدمة", "icon": "fa-box-archive", "accent": "teal"},
    "deadlines": {"title": "المهل القانونية", "icon": "fa-hourglass-half", "accent": "gold"},
    "crm": {"title": "CRM العملاء المحتملين", "icon": "fa-users-gear", "accent": "violet"},
    "workload": {"title": "عبء العمل", "icon": "fa-scale-balanced", "accent": "teal"},
    "workflow": {"title": "سير عمل القضايا", "icon": "fa-diagram-project", "accent": "violet"},
    "approvals": {"title": "الموافقات الداخلية", "icon": "fa-circle-check", "accent": "gold"},
    "reports": {"title": "التقارير التنفيذية", "icon": "fa-chart-line", "accent": "teal"},
    "client-portal": {"title": "بوابة العميل", "icon": "fa-user-shield", "accent": "gold"},
    "notifications-hub": {"title": "مركز الإشعارات", "icon": "fa-bell", "accent": "teal"},
    "ai-assistant": {"title": "المساعد الذكي", "icon": "fa-robot", "accent": "violet"},
    "audit-trail": {"title": "سجل التدقيق", "icon": "fa-list-check", "accent": "gold"},
    "backup-recovery": {"title": "النسخ الاحتياطي والاستعادة", "icon": "fa-database", "accent": "teal"},
}
WRITE_PAGES = {"billing", "expenses", "crm", "contracts", "approvals"}


def _base_context():
    today = date.today()
    return {
        "kpi": {
            "companies": Company.objects.count(),
            "cases": Case.objects.count(),
            "open_cases": Case.objects.filter(status="open").count(),
            "docs": Document.objects.count(),
            "upcoming_sessions": Session.objects.filter(
                session_date__gte=today, session_date__lte=today + timedelta(days=14)
            ).count(),
        },
        "top_companies": Company.objects.annotate(cases_count=Count("cases")).order_by("-cases_count")[:5],
        "top_lawyers": CustomUser.objects.filter(role="lawyer")
        .annotate(assigned_cases_count=Count("assigned_cases"))
        .order_by("-assigned_cases_count")[:5],
        "recent_cases": Case.objects.select_related("company").order_by("-created_at")[:6],
    }


def _can_view(user, page_key):
    if page_key in {"audit-trail", "backup-recovery"}:
        return user.is_admin
    return True


def _can_write(user, page_key):
    if page_key not in WRITE_PAGES:
        return False
    if page_key in {"billing", "expenses", "contracts", "approvals"}:
        return user.can_edit
    if page_key == "crm":
        return user.can_edit or user.can_manage_users
    return False


@login_required
def advanced_index(request):
    context = _base_context()
    context["pages"] = ADVANCED_PAGES
    return render(request, "advanced/index.html", context)


@login_required
def advanced_page(request, page_key):
    if page_key not in ADVANCED_PAGES:
        return render(request, "advanced/page.html", {"page": {"title": "الصفحة غير موجودة", "icon": "fa-circle-xmark", "accent": "gold"}})

    if not _can_view(request.user, page_key):
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
        return redirect("dashboard")

    if page_key == "calendar":
        return _calendar_page(request)
    if page_key == "billing":
        return _billing_page(request)
    if page_key == "expenses":
        return _expenses_page(request)

    if page_key == "crm":
        return _crm_page(request)
    if page_key == "contracts":
        return _contracts_page(request)
    if page_key == "approvals":
        return _approvals_page(request)
    if page_key == "reports":
        return _reports_page(request)

    context = _base_context()
    context["page"] = ADVANCED_PAGES[page_key]
    context["page_key"] = page_key
    context.update(_feature_context(page_key))
    return render(request, "advanced/feature.html", context)


def _calendar_page(request):
    context = _base_context()
    today = date.today()
    upcoming = (
        Session.objects.select_related("case", "case__company")
        .filter(session_date__gte=today, session_date__lte=today + timedelta(days=30))
        .order_by("session_date")
    )
    overdue = (
        Invoice.objects.select_related("company")
        .filter(due_date__lt=today)
        .exclude(status=Invoice.Status.PAID)
        .order_by("due_date")[:10]
    )
    context.update(
        {
            "page": ADVANCED_PAGES["calendar"],
            "upcoming_sessions_30": upcoming,
            "overdue_invoices": overdue,
        }
    )
    return render(request, "advanced/calendar.html", context)


def _billing_page(request):
    if request.method == "POST" and _can_write(request.user, "billing"):
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, "تم إنشاء الفاتورة بنجاح.")
            return redirect("advanced_page", page_key="billing")
    else:
        form = InvoiceForm()

    invoices = Invoice.objects.select_related("company", "case").order_by("-issue_date", "-id")
    totals = invoices.aggregate(total=Sum("amount"), paid=Sum("paid_amount"))

    context = _base_context()
    context.update(
        {
            "page": ADVANCED_PAGES["billing"],
            "form": form,
            "invoices": invoices[:100],
            "billing_total": totals.get("total") or 0,
            "billing_paid": totals.get("paid") or 0,
            "can_write": _can_write(request.user, "billing"),
        }
    )
    return render(request, "advanced/billing.html", context)


def _expenses_page(request):
    if request.method == "POST" and _can_write(request.user, "expenses"):
        form = CaseExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, "تم تسجيل المصروف بنجاح.")
            return redirect("advanced_page", page_key="expenses")
    else:
        form = CaseExpenseForm()

    expenses = CaseExpense.objects.select_related("case", "case__company").order_by("-expense_date", "-id")
    total_expenses = expenses.aggregate(total=Sum("amount")).get("total") or 0

    context = _base_context()
    context.update(
        {
            "page": ADVANCED_PAGES["expenses"],
            "form": form,
            "expenses": expenses[:100],
            "expenses_total": total_expenses,
            "can_write": _can_write(request.user, "expenses"),
        }
    )
    return render(request, "advanced/expenses.html", context)


def _crm_page(request):
    edit_id = request.GET.get("edit")
    instance = Lead.objects.filter(pk=edit_id).first() if edit_id else None
    if request.method == "POST" and _can_write(request.user, "crm"):
        if request.POST.get("action") == "delete":
            get_object_or_404(Lead, pk=request.POST.get("id")).delete()
            messages.success(request, "تم حذف العميل المحتمل.")
            return redirect("advanced_page", page_key="crm")
        form = LeadForm(request.POST, instance=instance)
        if form.is_valid():
            lead = form.save(commit=False)
            if not lead.created_by_id:
                lead.created_by = request.user
            lead.save()
            messages.success(request, "تم حفظ العميل المحتمل.")
            return redirect("advanced_page", page_key="crm")
    else:
        form = LeadForm(instance=instance)

    context = _base_context()
    context.update(
        {
            "page": ADVANCED_PAGES["crm"],
            "page_key": "crm",
            "form": form,
            "can_write": _can_write(request.user, "crm"),
            "editing": instance,
            "leads": Lead.objects.select_related("owner").order_by("-created_at")[:120],
        }
    )
    return render(request, "advanced/crm.html", context)


def _contracts_page(request):
    edit_id = request.GET.get("edit")
    instance = ContractRecord.objects.filter(pk=edit_id).first() if edit_id else None
    if request.method == "POST" and _can_write(request.user, "contracts"):
        if request.POST.get("action") == "delete":
            get_object_or_404(ContractRecord, pk=request.POST.get("id")).delete()
            messages.success(request, "تم حذف العقد.")
            return redirect("advanced_page", page_key="contracts")
        form = ContractRecordForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.created_by_id:
                obj.created_by = request.user
            obj.save()
            messages.success(request, "تم حفظ العقد.")
            return redirect("advanced_page", page_key="contracts")
    else:
        form = ContractRecordForm(instance=instance)

    context = _base_context()
    context.update(
        {
            "page": ADVANCED_PAGES["contracts"],
            "page_key": "contracts",
            "form": form,
            "can_write": _can_write(request.user, "contracts"),
            "editing": instance,
            "contracts": ContractRecord.objects.select_related("company", "case").order_by("-created_at")[:120],
        }
    )
    return render(request, "advanced/contracts.html", context)


def _approvals_page(request):
    edit_id = request.GET.get("edit")
    instance = ApprovalRequest.objects.filter(pk=edit_id).first() if edit_id else None
    if request.method == "POST" and _can_write(request.user, "approvals"):
        if request.POST.get("action") == "delete":
            get_object_or_404(ApprovalRequest, pk=request.POST.get("id")).delete()
            messages.success(request, "تم حذف الطلب.")
            return redirect("advanced_page", page_key="approvals")
        form = ApprovalRequestForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.requested_by_id:
                obj.requested_by = request.user
            if obj.status in {ApprovalRequest.Status.APPROVED, ApprovalRequest.Status.REJECTED}:
                obj.decided_at = timezone.now()
            obj.save()
            messages.success(request, "تم حفظ الطلب.")
            return redirect("advanced_page", page_key="approvals")
    else:
        form = ApprovalRequestForm(instance=instance)

    context = _base_context()
    context.update(
        {
            "page": ADVANCED_PAGES["approvals"],
            "page_key": "approvals",
            "form": form,
            "can_write": _can_write(request.user, "approvals"),
            "editing": instance,
            "approval_items": ApprovalRequest.objects.select_related("case", "assigned_to").order_by("-created_at")[:120],
        }
    )
    return render(request, "advanced/approvals.html", context)


def _reports_page(request):
    export = request.GET.get("export")
    case_types = list(Case.objects.values("case_type").annotate(total=Count("id")).order_by("-total"))
    status_breakdown = list(Case.objects.values("status").annotate(total=Count("id")).order_by("-total"))
    invoices = Invoice.objects.select_related("company").order_by("-issue_date")[:300]
    expenses = CaseExpense.objects.select_related("case").order_by("-expense_date")[:300]

    if export:
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="report_{export}.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        if export == "case_types":
            writer.writerow(["case_type", "total"])
            for row in case_types:
                writer.writerow([row["case_type"], row["total"]])
        elif export == "status":
            writer.writerow(["status", "total"])
            for row in status_breakdown:
                writer.writerow([row["status"], row["total"]])
        elif export == "invoices":
            writer.writerow(["invoice_number", "company", "amount", "paid", "status"])
            for i in invoices:
                writer.writerow([i.invoice_number, i.company.name, i.amount, i.paid_amount, i.status])
        elif export == "expenses":
            writer.writerow(["case", "title", "amount", "date"])
            for e in expenses:
                writer.writerow([e.case.case_number, e.title, e.amount, e.expense_date])
        return response

    context = _base_context()
    context.update(
        {
            "page": ADVANCED_PAGES["reports"],
            "page_key": "reports",
            "case_types": case_types,
            "status_breakdown": status_breakdown,
            "docs_total": Document.objects.count(),
            "sessions_total": Session.objects.count(),
            "invoices_total": Invoice.objects.count(),
            "expenses_total": CaseExpense.objects.count(),
        }
    )
    return render(request, "advanced/reports.html", context)


def _feature_context(page_key):
    today = date.today()
    ctx = {}

    if page_key == "archive":
        ctx["docs_by_type"] = (
            Document.objects.values("file_type").annotate(total=Count("id")).order_by("-total")
        )
        ctx["latest_docs"] = Document.objects.select_related("company", "case").order_by("-uploaded_at")[:30]

    elif page_key == "deadlines":
        ctx["deadlines"] = Session.objects.select_related("case", "case__company").filter(
            session_date__gte=today, session_date__lte=today + timedelta(days=21)
        ).order_by("session_date")
        ctx["overdue_invoices"] = Invoice.objects.select_related("company").filter(
            due_date__lt=today
        ).exclude(status=Invoice.Status.PAID)[:30]

    elif page_key == "workload":
        ctx["lawyer_workload"] = (
            CustomUser.objects.filter(role="lawyer")
            .annotate(
                open_cases=Count("assigned_cases", filter=Q(assigned_cases__status="open")),
                total_cases=Count("assigned_cases"),
            )
            .order_by("-total_cases")
        )

    elif page_key == "workflow":
        ctx["open_cases"] = Case.objects.filter(status="open").select_related("company")[:40]
        ctx["postponed_cases"] = Case.objects.filter(status="postponed").select_related("company")[:40]
        ctx["closed_cases"] = Case.objects.filter(status="closed").select_related("company")[:40]

    elif page_key == "client-portal":
        ctx["portal_companies"] = Company.objects.annotate(
            total_cases=Count("cases"), total_docs=Count("documents")
        ).order_by("-updated_at")[:60]

    elif page_key == "notifications-hub":
        upcoming_sessions = Session.objects.select_related("case", "case__company").filter(
            session_date__gte=today, session_date__lte=today + timedelta(days=7)
        )[:30]
        overdue_invoices = Invoice.objects.select_related("company").filter(
            due_date__lt=today
        ).exclude(status=Invoice.Status.PAID)[:30]
        ctx["notif_sessions"] = upcoming_sessions
        ctx["notif_invoices"] = overdue_invoices

    elif page_key == "ai-assistant":
        total = Case.objects.count() or 1
        open_count = Case.objects.filter(status="open").count()
        postponed_count = Case.objects.filter(status="postponed").count()
        close_rate = round(((total - open_count) / total) * 100, 1)
        ctx["ai_insights"] = [
            f"نسبة إغلاق القضايا الحالية {close_rate}%.",
            f"لديك {postponed_count} قضية مؤجلة، يُفضّل جدولة مراجعة أسبوعية لها.",
            f"الشركات الأكثر نشاطًا: {', '.join([c.name for c in Company.objects.annotate(cn=Count('cases')).order_by('-cn')[:3]]) or '—'}.",
        ]
        ctx["ai_recommended_cases"] = Case.objects.filter(status__in=["open", "postponed"]).select_related("company")[:20]

    elif page_key == "audit-trail":
        ctx["users_activity"] = CustomUser.objects.order_by("-last_seen", "-date_joined")[:80]
        ctx["latest_records"] = Document.objects.select_related("uploaded_by").order_by("-uploaded_at")[:40]

    elif page_key == "backup-recovery":
        db_path = Path(__file__).resolve().parents[2] / "db.sqlite3"
        size_mb = round((db_path.stat().st_size / (1024 * 1024)), 2) if db_path.exists() else 0
        ctx["backup_info"] = {
            "db_path": str(db_path),
            "db_size_mb": size_mb,
            "generated_at": today,
        }

    return ctx
