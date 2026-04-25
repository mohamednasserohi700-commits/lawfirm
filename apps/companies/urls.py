from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('<int:pk>/', views.company_detail, name='company_detail'),
    path('create/', views.company_create, name='company_create'),
    path('<int:pk>/edit/', views.company_edit, name='company_edit'),
    path('<int:pk>/delete/', views.company_delete, name='company_delete'),
]
