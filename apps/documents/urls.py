from django.urls import path
from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('company/<int:company_pk>/upload/', views.document_upload_company, name='document_upload_company'),
    path('case/<int:case_pk>/upload/', views.document_upload_case, name='document_upload_case'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
    path('<int:pk>/delete/', views.document_delete, name='document_delete'),
]
