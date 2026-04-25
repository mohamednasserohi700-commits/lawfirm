from django.urls import path
from . import views

urlpatterns = [
    path('', views.case_list, name='case_list'),
    path('<int:pk>/', views.case_detail, name='case_detail'),
    path('company/<int:company_pk>/create/', views.case_create, name='case_create'),
    path('<int:pk>/edit/', views.case_edit, name='case_edit'),
    path('<int:pk>/delete/', views.case_delete, name='case_delete'),
    # الجلسات
    path('<int:case_pk>/sessions/create/', views.session_create, name='session_create'),
    path('sessions/<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('sessions/<int:pk>/delete/', views.session_delete, name='session_delete'),
]
