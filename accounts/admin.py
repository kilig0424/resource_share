from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # 在用户列表显示中添加自定义字段
    list_display = UserAdmin.list_display + ('upload_permission', 'agreed_to_terms', 'apply_time')

    # 在用户编辑表单中添加自定义字段
    fieldsets = UserAdmin.fieldsets + (
        ('上传权限', {
            'fields': ('upload_permission', 'agreed_to_terms', 'apply_time'),
        }),
    )

    # 在添加用户表单中添加自定义字段
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('上传权限', {
            'fields': ('upload_permission', 'agreed_to_terms'),
        }),
    )

    # 添加筛选功能
    list_filter = UserAdmin.list_filter + ('upload_permission', 'agreed_to_terms')

    # 添加搜索功能
    search_fields = UserAdmin.search_fields + ('upload_permission',)


admin.site.register(CustomUser, CustomUserAdmin)