from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Resource

class ResourceSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        # 返回所有资源（不再按 is_approved 过滤）
        return Resource.objects.all()

    def location(self, obj):
        return reverse('core:resource_detail', args=[obj.id])

    # 以下三个方法用于提供页面的标题、描述和关键词，帮助搜索引擎理解内容
    def title(self, obj):
        return obj.title

    def description(self, obj):
        if obj.description:
            return obj.description[:160]
        return obj.title

    def keywords(self, obj):
        return obj.keywords if obj.keywords else ""