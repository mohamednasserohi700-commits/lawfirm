from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('بيانات إضافية', {'fields': ('role', 'phone', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('بيانات إضافية', {'fields': ('role', 'phone', 'first_name', 'last_name', 'email')}),
    )
