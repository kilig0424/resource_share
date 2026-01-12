from django.contrib import admin
from .models import Category, CloudType, Resource, Favorite, Comment, Report



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
                    'copy_count', 'like_count', 'report_count', 'is_approved',
                    'is_featured', 'created_at']
    list_filter = ['category', 'cloud_type', 'is_approved', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'keywords']
    readonly_fields = ['view_count', 'copy_count', 'like_count', 'collect_count',
                       'comment_count', 'report_count', 'created_at', 'updated_at']


    # 修改 fieldsets，移除 screenshot 字段
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'keywords', 'user')
        }),
        ('资源信息', {
            'fields': ('category', 'cloud_type', 'resource_url', 'extract_code','screenshot')
        }),
        ('状态信息', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('统计信息', {
            'fields': ('view_count', 'copy_count', 'like_count', 'collect_count',
                       'comment_count', 'report_count'),
            'classes': ('collapse',)  # 可折叠
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # 可折叠
        }),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'resource__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'resource__title', 'content']

    def content_preview(self, obj):
        """显示评论内容的前50个字符"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = '评论内容'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'resource__title']


