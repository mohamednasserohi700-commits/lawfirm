from django.contrib import admin
from .models import Case, Session

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'company', 'court_name', 'case_type', 'status', 'assigned_lawyer')
    list_filter = ('status', 'case_type')
    search_fields = ('case_number', 'company__name', 'opponent_name')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('case', 'session_date', 'status')
    list_filter = ('status',)
