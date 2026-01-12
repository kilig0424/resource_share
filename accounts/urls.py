from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('apply-permission/', views.apply_upload_permission, name='apply_permission'),
    path('permission-status/', views.permission_status, name='permission_status'),  # 查看申请状态
]