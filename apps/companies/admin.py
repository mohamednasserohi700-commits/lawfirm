from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'client_name', 'phone')
    list_filter = ('created_at',)
