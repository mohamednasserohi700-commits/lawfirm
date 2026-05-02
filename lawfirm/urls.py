"""
روابط URL الرئيسية للنظام
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('users/', include(('apps.users.urls', 'users'), namespace='users')),
    path('dashboard/', include('apps.users.dashboard_urls')),
    path('advanced/', include('apps.users.advanced_urls')),
    path('companies/', include('apps.companies.urls')),
    path('cases/', include('apps.cases.urls')),
    path('documents/', include('apps.documents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
