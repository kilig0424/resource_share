from django.contrib import admin
from .models import Category, CloudType, Resource, Favorite, Comment, Report
from django.urls import reverse
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    ordering = ['-weight', 'name']


@admin.register(CloudType)
class CloudTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_class', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['name']
    list_filter = ['is_active', 'created_at']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'cloud_type', 'user', 'view_count',
                    'copy_count', 'like_count', 'collect_count', 'comment_count',
                    'report_count', 'is_approved', 'is_featured', 'created_at']

    # 默认按创建时间倒序排列
    ordering = ['-created_at']

    # 添加可点击排序的字段
    sortable_by = ['view_count', 'copy_count', 'like_count', 'collect_count',
                   'comment_count', 'report_count', 'created_at']

    # 筛选器 - 修改这里，移除 report_count，因为它不适合作为筛选器
    list_filter = ['category', 'cloud_type', 'is_approved', 'is_featured', 'created_at']

    search_fields = ['title', 'description', 'keywords', 'user__username']

    # 批量操作
    actions = ['approve_resources', 'reject_resources', 'clear_reports', 'toggle_featured']

    readonly_fields = ['view_count', 'copy_count', 'like_count', 'collect_count',
                       'comment_count', 'report_count', 'created_at', 'updated_at']

    # 为举报数添加自定义排序链接的方法
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # 检查是否有排序参数
        ordering = request.GET.get('o', '')

        # 为各种统计字段添加排序支持
        if ordering == '10':  # view_count 倒序
            return qs.order_by('-view_count')
        elif ordering == '11':  # copy_count 倒序
            return qs.order_by('-copy_count')
        elif ordering == '12':  # like_count 倒序
            return qs.order_by('-like_count')
        elif ordering == '13':  # collect_count 倒序
            return qs.order_by('-collect_count')
        elif ordering == '14':  # comment_count 倒序
            return qs.order_by('-comment_count')
        elif ordering == '15':  # report_count 倒序
            return qs.order_by('-report_count')

        return qs

    # 批量操作：审核通过
    def approve_resources(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'已审核通过{updated}个资源')

    approve_resources.short_description = "审核通过选中资源"

    # 批量操作：审核拒绝
    def reject_resources(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'已拒绝{updated}个资源')

    reject_resources.short_description = "审核拒绝选中资源"

    # 批量操作：清除举报
    def clear_reports(self, request, queryset):
        updated = queryset.update(report_count=0)
        # 同时删除举报记录
        for resource in queryset:
            Report.objects.filter(resource=resource).delete()
        self.message_user(request, f'已清除{updated}个资源的举报记录')

    clear_reports.short_description = "清除选中资源的举报"

    # 批量操作：切换推荐状态
    def toggle_featured(self, request, queryset):
        for resource in queryset:
            resource.is_featured = not resource.is_featured
            resource.save(update_fields=['is_featured'])
        self.message_user(request, f'已切换{queryset.count()}个资源的推荐状态')

    toggle_featured.short_description = "切换推荐状态"

    # fieldsets 保持不变
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'keywords', 'user')
        }),
        ('资源信息', {
            'fields': ('category', 'cloud_type', 'resource_url', 'extract_code', 'screenshot')
        }),
        ('状态信息', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('统计信息', {
            'fields': ('view_count', 'copy_count', 'like_count', 'collect_count',
                       'comment_count', 'report_count'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # 自定义列表视图，添加排序链接
    def changelist_view(self, request, extra_context=None):
        # 添加上下文信息，用于在前端显示排序选项
        extra_context = extra_context or {}
        extra_context['sort_options'] = [
            {'name': '查看次数', 'param': 'o=10'},
            {'name': '复制次数', 'param': 'o=11'},
            {'name': '点赞数', 'param': 'o=12'},
            {'name': '收藏数', 'param': 'o=13'},
            {'name': '评论数', 'param': 'o=14'},
            {'name': '举报数', 'param': 'o=15'},
        ]
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'resource__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # 修改字段显示顺序，添加view_resource
    list_display = ['user', 'resource', 'content_preview', 'created_at', 'report_count', 'view_resource']
    list_filter = ['created_at', 'user', 'resource']
    search_fields = ['user__username', 'resource__title', 'content']
    actions = ['delete_selected_comments']
    date_hierarchy = 'created_at'  # 添加日期层次导航

    def content_preview(self, obj):
        """显示评论内容的前50个字符"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = '评论内容'

    # 显示资源的举报数
    def report_count(self, obj):
        return obj.resource.report_count

    report_count.short_description = '资源举报数'

    # 添加批量删除操作
    def delete_selected_comments(self, request, queryset):
        # 更新相关资源的评论计数
        for comment in queryset:
            resource = comment.resource
            if resource.comment_count > 0:
                resource.comment_count -= 1
                resource.save(update_fields=['comment_count'])

        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已删除{count}条评论')

    delete_selected_comments.short_description = "删除选中评论"

    # 添加快速跳转到资源的功能
    def view_resource(self, obj):
        url = reverse('admin:core_resource_change', args=[obj.resource.id])
        return format_html('<a href="{}">查看资源</a>', url)

    view_resource.short_description = '相关资源'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource_link', 'resource_status', 'resource_uploader', 'created_at', 'action_buttons']
    list_filter = ['created_at', 'user', 'resource__user']
    search_fields = ['user__username', 'resource__title', 'resource__user__username']
    actions = ['process_reports', 'ignore_reports', 'delete_reports_and_resources']
    date_hierarchy = 'created_at'

    # 显示资源链接（可点击）
    def resource_link(self, obj):
        url = reverse('admin:core_resource_change', args=[obj.resource.id])
        return format_html('<a href="{}">{}</a>', url, obj.resource.title[:50])

    resource_link.short_description = '被举报资源'
    resource_link.admin_order_field = 'resource__title'

    # 显示资源状态
    def resource_status(self, obj):
        if obj.resource.is_approved:
            return format_html('<span style="color: green;">✓ 已审核</span>')
        else:
            return format_html('<span style="color: red;">✗ 未审核</span>')

    resource_status.short_description = '资源状态'
    resource_status.admin_order_field = 'resource__is_approved'

    # 显示资源上传者
    def resource_uploader(self, obj):
        return obj.resource.user.username

    resource_uploader.short_description = '上传者'
    resource_uploader.admin_order_field = 'resource__user__username'

    # 显示举报数量
    def report_count(self, obj):
        return obj.resource.report_count

    report_count.short_description = '总举报数'
    report_count.admin_order_field = 'resource__report_count'

    # 移除默认的删除批量操作，强制使用自定义操作
    def get_actions(self, request):
        actions = super().get_actions(request)
        # 移除默认的删除操作
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

    # 添加操作按钮
    def action_buttons(self, obj):
        resource_url = reverse('admin:core_resource_change', args=[obj.resource.id])
        delete_url = reverse('admin:core_report_delete', args=[obj.id])

        buttons = [
            format_html(
                '<a class="button" href="{}" style="background: #417690; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;">处理资源</a>',
                resource_url),
        ]

        return format_html(''.join(buttons))



    action_buttons.short_description = '操作'

    # 批量操作：处理举报（标记资源为需要审核）
    def process_reports(self, request, queryset):
        for report in queryset:
            report.resource.is_approved = False  # 设置为需要重新审核
            report.resource.save(update_fields=['is_approved'])

        count = queryset.count()
        self.message_user(request, f'已处理{count}个举报，相关资源已标记为待审核')

    process_reports.short_description = "处理举报（标记为待审核）"

    # 批量操作：忽略举报（删除举报记录）
    def ignore_reports(self, request, queryset):
        # 更新相关资源的举报计数
        for report in queryset:
            resource = report.resource
            if resource.report_count > 0:
                resource.report_count -= 1
                resource.save(update_fields=['report_count'])

        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'已忽略{count}个举报')

    ignore_reports.short_description = "忽略举报（删除记录）"

    # 批量操作：删除举报并下架资源
    def delete_reports_and_resources(self, request, queryset):
        resources_to_delete = set()

        # 收集需要删除的资源
        for report in queryset:
            resources_to_delete.add(report.resource)

        # 先删除举报记录
        count = queryset.count()
        queryset.delete()

        # 删除相关资源
        resource_count = 0
        for resource in resources_to_delete:
            resource.delete()
            resource_count += 1

        self.message_user(request, f'已删除{count}个举报记录和{resource_count}个资源')

    delete_reports_and_resources.short_description = "删除举报并下架资源"

    # 添加自定义CSS
    class Media:
        css = {
            'all': ('admin/css/report_admin.css',)
        }


