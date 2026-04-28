from django.urls import path
from . import views

urlpatterns = [
    # تسجيل الدخول والخروج
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # إدارة المستخدمين (للأدمن)
    path('', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('<int:pk>/change-password/', views.admin_change_password, name='admin_change_password'),
    path('<int:pk>/permissions/', views.user_permissions, name='user_permissions'),

    # صفحة المتصلين
    path('online/', views.online_users_view, name='online_users'),

    # لوحة المطور (مخفية)
    path('dev/panel/', views.developer_panel, name='developer_panel'),
    path('dev/change-password/<int:pk>/', views.developer_change_password, name='developer_change_password'),
    path('dev/toggle-user/<int:pk>/', views.developer_toggle_user, name='developer_toggle_user'),
]
