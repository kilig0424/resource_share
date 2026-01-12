from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # 在用户列表显示中添加自定义字段
    list_display = UserAdmin.list_display + ('upload_permission', 'apply_status', 'apply_time', 'is_staff')

    # 在用户编辑表单中添加自定义字段
    fieldsets = UserAdmin.fieldsets + (
        ('上传权限管理', {
            'fields': ('upload_permission', 'agreed_to_terms', 'apply_status',
                       'apply_time', 'review_time', 'review_message'),
        }),
    )

    # 在添加用户表单中添加自定义字段
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('上传权限', {
            'fields': ('upload_permission', 'agreed_to_terms'),
        }),
    )

    # 添加筛选功能
    list_filter = UserAdmin.list_filter + ('upload_permission', 'agreed_to_terms', 'apply_status')

    # 添加搜索功能
    search_fields = UserAdmin.search_fields + ('upload_permission',)

    # 添加批量操作
    actions = ['enable_upload_permission', 'disable_upload_permission',
               'approve_applications', 'reject_applications']

    # 只读字段
    readonly_fields = ('apply_time', 'review_time')

    def enable_upload_permission(self, request, queryset):
        """批量开启上传权限"""
        updated = queryset.update(upload_permission=True)
        self.message_user(request, f'已为{updated}个用户开启上传权限')

    enable_upload_permission.short_description = "批量开启上传权限"

    def disable_upload_permission(self, request, queryset):
        """批量关闭上传权限"""
        updated = queryset.update(upload_permission=False)
        self.message_user(request, f'已为{updated}个用户关闭上传权限')

    disable_upload_permission.short_description = "批量关闭上传权限"

    def approve_applications(self, request, queryset):
        """批量批准申请"""
        from django.utils import timezone
        count = 0
        for user in queryset:
            if user.apply_status == 'pending':  # 只处理待审核的申请
                user.approve_upload_permission(f"批量审核通过（管理员：{request.user.username}）")
                count += 1
        self.message_user(request, f'已批准{count}个申请')

    approve_applications.short_description = "批量批准申请"

    def reject_applications(self, request, queryset):
        """批量拒绝申请"""
        from django.utils import timezone
        count = 0
        for user in queryset:
            if user.apply_status == 'pending':  # 只处理待审核的申请
                user.reject_upload_permission(f"批量审核拒绝（管理员：{request.user.username}）")
                count += 1
        self.message_user(request, f'已拒绝{count}个申请')

    reject_applications.short_description = "批量拒绝申请"



admin.site.register(CustomUser, CustomUserAdmin)