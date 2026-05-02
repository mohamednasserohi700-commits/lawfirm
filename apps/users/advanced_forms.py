from django import forms
from django.utils import timezone

from apps.cases.models import ApprovalRequest, CaseExpense, ContractRecord, Invoice, Lead


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "company",
            "case",
            "invoice_number",
            "issue_date",
            "due_date",
            "amount",
            "paid_amount",
            "status",
            "notes",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["issue_date"].initial = today
        self.fields["due_date"].initial = today


class CaseExpenseForm(forms.ModelForm):
    class Meta:
        model = CaseExpense
        fields = ["case", "title", "category", "amount", "expense_date", "notes"]
        widgets = {
            "expense_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["expense_date"].initial = timezone.localdate()


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["company_name", "contact_name", "phone", "email", "stage", "owner", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}


class ContractRecordForm(forms.ModelForm):
    class Meta:
        model = ContractRecord
        fields = [
            "title",
            "company",
            "case",
            "start_date",
            "end_date",
            "value",
            "status",
            "document_ref",
            "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_date"].initial = timezone.localdate()


class ApprovalRequestForm(forms.ModelForm):
    class Meta:
        model = ApprovalRequest
        fields = ["title", "request_type", "case", "assigned_to", "amount", "status", "notes", "decision_note"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2}), "decision_note": forms.Textarea(attrs={"rows": 2})}
