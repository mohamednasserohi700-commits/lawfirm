"""
نماذج تطبيق القضايا والجلسات
"""
from django.db import models
from apps.users.models import CustomUser
from apps.companies.models import Company


class Case(models.Model):
    """نموذج القضية"""

    class Status(models.TextChoices):
        OPEN = 'open', 'مفتوحة'
        CLOSED = 'closed', 'مغلقة'
        POSTPONED = 'postponed', 'مؤجلة'

    class CaseType(models.TextChoices):
        COMMERCIAL = 'commercial', 'تجارية'
        CIVIL = 'civil', 'مدنية'
        CRIMINAL = 'criminal', 'جنائية'
        LABOR = 'labor', 'عمالية'
        FAMILY = 'family', 'أسرية'
        ADMINISTRATIVE = 'administrative', 'إدارية'
        OTHER = 'other', 'أخرى'

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='cases', verbose_name='الشركة'
    )
    case_number = models.CharField(max_length=100, verbose_name='رقم القضية')
    court_name = models.CharField(max_length=200, verbose_name='اسم المحكمة')
    case_type = models.CharField(
        max_length=30, choices=CaseType.choices,
        default=CaseType.OTHER, verbose_name='نوع القضية'
    )
    opponent_name = models.CharField(max_length=200, verbose_name='اسم الخصم')
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.OPEN, verbose_name='حالة القضية'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    assigned_lawyer = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_cases', verbose_name='المحامي المسؤول'
    )
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name='created_cases', verbose_name='أنشأه'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')

    class Meta:
        verbose_name = 'قضية'
        verbose_name_plural = 'القضايا'
        ordering = ['-created_at']

    def __str__(self):
        return f"القضية {self.case_number} - {self.company.name}"

    def get_status_badge(self):
        badges = {
            'open': 'badge-success',
            'closed': 'badge-danger',
            'postponed': 'badge-warning',
        }
        return badges.get(self.status, 'badge-secondary')

    @property
    def next_session(self):
        from datetime import date
        return self.sessions.filter(
            session_date__gte=date.today(),
            status='scheduled'
        ).order_by('session_date').first()


class Session(models.Model):
    """نموذج جلسة المحكمة"""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'مجدولة'
        HELD = 'held', 'منعقدة'
        POSTPONED = 'postponed', 'مؤجلة'
        CANCELLED = 'cancelled', 'ملغاة'

    case = models.ForeignKey(
        Case, on_delete=models.CASCADE,
        related_name='sessions', verbose_name='القضية'
    )
    session_date = models.DateField(verbose_name='تاريخ الجلسة')
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.SCHEDULED, verbose_name='حالة الجلسة'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات الجلسة')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name='created_sessions', verbose_name='أنشأه'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'جلسة'
        verbose_name_plural = 'الجلسات'
        ordering = ['-session_date']

    def __str__(self):
        return f"جلسة {self.session_date} - {self.case}"

    def get_status_badge(self):
        badges = {
            'scheduled': 'badge-primary',
            'held': 'badge-success',
            'postponed': 'badge-warning',
            'cancelled': 'badge-danger',
        }
        return badges.get(self.status, 'badge-secondary')


class Invoice(models.Model):
    """فواتير الأتعاب"""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        SENT = 'sent', 'مرسلة'
        PARTIAL = 'partial', 'مدفوعة جزئياً'
        PAID = 'paid', 'مدفوعة'
        OVERDUE = 'overdue', 'متأخرة'

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='invoices', verbose_name='الشركة'
    )
    case = models.ForeignKey(
        Case, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name='القضية'
    )
    invoice_number = models.CharField(max_length=60, unique=True, verbose_name='رقم الفاتورة')
    issue_date = models.DateField(verbose_name='تاريخ الإصدار')
    due_date = models.DateField(verbose_name='تاريخ الاستحقاق')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='قيمة الفاتورة')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='المبلغ المسدد')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='الحالة')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_invoices', verbose_name='أنشأه'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'فاتورة'
        verbose_name_plural = 'الفواتير'
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.company.name}"

    @property
    def balance(self):
        return max(self.amount - self.paid_amount, 0)


class CaseExpense(models.Model):
    """مصروفات القضايا"""

    class Category(models.TextChoices):
        COURT_FEES = 'court_fees', 'رسوم محكمة'
        TRANSPORT = 'transport', 'انتقالات'
        EXPERT = 'expert', 'أتعاب خبرة'
        DOCUMENTS = 'documents', 'نسخ ومطبوعات'
        ADMIN = 'admin', 'إداري'
        OTHER = 'other', 'أخرى'

    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, related_name='expenses', verbose_name='القضية'
    )
    title = models.CharField(max_length=200, verbose_name='وصف المصروف')
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.OTHER, verbose_name='التصنيف')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='المبلغ')
    expense_date = models.DateField(verbose_name='تاريخ المصروف')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_expenses', verbose_name='أنشأه'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'مصروف قضية'
        verbose_name_plural = 'مصروفات القضايا'
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.case.case_number} - {self.title}"


class Lead(models.Model):
    """عميل محتمل CRM"""

    class Stage(models.TextChoices):
        NEW = "new", "جديد"
        CONTACTED = "contacted", "تم التواصل"
        QUALIFIED = "qualified", "مؤهل"
        PROPOSAL = "proposal", "عرض سعر"
        WON = "won", "تم التحويل"
        LOST = "lost", "مفقود"

    company_name = models.CharField(max_length=200, verbose_name="اسم الجهة")
    contact_name = models.CharField(max_length=200, blank=True, verbose_name="اسم المسؤول")
    phone = models.CharField(max_length=30, blank=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد")
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.NEW, verbose_name="المرحلة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    owner = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_leads", verbose_name="المسؤول"
    )
    converted_company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="source_leads", verbose_name="الشركة بعد التحويل"
    )
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="created_leads", verbose_name="أنشأه"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التعديل")

    class Meta:
        verbose_name = "عميل محتمل"
        verbose_name_plural = "العملاء المحتملون"
        ordering = ["-created_at"]

    def __str__(self):
        return self.company_name


class ContractRecord(models.Model):
    """سجل عقود"""

    class Status(models.TextChoices):
        DRAFT = "draft", "مسودة"
        ACTIVE = "active", "نشط"
        EXPIRED = "expired", "منتهي"
        TERMINATED = "terminated", "ملغي"

    title = models.CharField(max_length=250, verbose_name="عنوان العقد")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contracts", verbose_name="الشركة")
    case = models.ForeignKey(
        Case, on_delete=models.SET_NULL, null=True, blank=True, related_name="contracts", verbose_name="القضية"
    )
    start_date = models.DateField(verbose_name="بداية العقد")
    end_date = models.DateField(null=True, blank=True, verbose_name="نهاية العقد")
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="قيمة العقد")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name="الحالة")
    document_ref = models.CharField(max_length=255, blank=True, verbose_name="مرجع ملف العقد")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="created_contracts", verbose_name="أنشأه"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "عقد"
        verbose_name_plural = "العقود"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ApprovalRequest(models.Model):
    """طلب موافقة داخلي"""

    class Type(models.TextChoices):
        EXPENSE = "expense", "اعتماد مصروف"
        DISCOUNT = "discount", "اعتماد خصم"
        CONTRACT = "contract", "اعتماد عقد"
        LEGAL_STEP = "legal_step", "إجراء قانوني"
        OTHER = "other", "أخرى"

    class Status(models.TextChoices):
        PENDING = "pending", "قيد الانتظار"
        APPROVED = "approved", "مقبول"
        REJECTED = "rejected", "مرفوض"

    title = models.CharField(max_length=250, verbose_name="عنوان الطلب")
    request_type = models.CharField(max_length=30, choices=Type.choices, default=Type.OTHER, verbose_name="نوع الطلب")
    case = models.ForeignKey(
        Case, on_delete=models.SET_NULL, null=True, blank=True, related_name="approval_requests", verbose_name="القضية"
    )
    requested_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="approval_requests", verbose_name="مقدم الطلب"
    )
    assigned_to = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="approvals_to_review", verbose_name="مسؤول الاعتماد"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="قيمة مرتبطة")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="تفاصيل")
    decision_note = models.TextField(blank=True, verbose_name="ملاحظة القرار")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    decided_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ القرار")

    class Meta:
        verbose_name = "طلب موافقة"
        verbose_name_plural = "طلبات الموافقة"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
