from django.db import models
from django.utils import timezone


class Category(models.Model):
    """资源分类模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    weight = models.IntegerField(default=0, verbose_name="排序权重", help_text="数字越大，排序越靠前")

    class Meta:
        verbose_name = "资源分类"
        verbose_name_plural = "资源分类"
        ordering = ['-weight', 'name']  # 默认按权重倒序、名称正序排列

    def __str__(self):
        return self.name


class CloudType(models.Model):
    """网盘类型模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name="网盘名称")
    icon_class = models.CharField(max_length=50, blank=True, verbose_name="图标类名",
                                  help_text="前端图标类名，如：baidu-icon、xunlei-icon")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "网盘类型"
        verbose_name_plural = "网盘类型"
        ordering = ['name']

    def __str__(self):
        return self.name


class Resource(models.Model):
    """资源模型"""
    # 基础信息
    title = models.CharField(max_length=200, verbose_name="资源标题")
    description = models.TextField(verbose_name="资源描述", blank=True)
    keywords = models.CharField(max_length=200, verbose_name="关键词",
                                help_text="用逗号分隔，如：电影,科幻,2023")

    # 关联信息
    cloud_type = models.ForeignKey(CloudType, on_delete=models.PROTECT, verbose_name="网盘类型")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="分类")
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, verbose_name="上传用户")

    # 资源信息
    resource_url = models.CharField(max_length=500, verbose_name="资源链接")  # 改为CharField
    extract_code = models.CharField(max_length=20, blank=True, verbose_name="提取码")
    screenshot = models.ImageField(upload_to='screenshots/', blank=True, verbose_name="资源截图")

    # 统计信息
    view_count = models.PositiveIntegerField(default=0, verbose_name="查看次数")
    copy_count = models.PositiveIntegerField(default=0, verbose_name="复制链接次数")
    like_count = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    collect_count = models.PositiveIntegerField(default=0, verbose_name="收藏数")
    comment_count = models.PositiveIntegerField(default=0, verbose_name="评论数")
    report_count = models.PositiveIntegerField(default=0, verbose_name="举报数")

    # 状态信息
    is_approved = models.BooleanField(default=True, verbose_name="审核通过")
    is_featured = models.BooleanField(default=False, verbose_name="是否推荐")

    # 时间信息
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "资源"
        verbose_name_plural = "资源"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-view_count']),
            models.Index(fields=['-copy_count']),
            models.Index(fields=['-like_count']),
        ]

    def __str__(self):
        return self.title

    def get_keywords_list(self):
        """将关键词字符串转换为列表"""
        if self.keywords:
            return [k.strip() for k in self.keywords.split(',')]
        return []


class Favorite(models.Model):
    """收藏模型"""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, verbose_name="用户")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name="资源")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="收藏时间")

    class Meta:
        verbose_name = "收藏记录"
        verbose_name_plural = "收藏记录"
        # 确保一个用户只能收藏同一个资源一次
        unique_together = ['user', 'resource']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.resource.title}"


class Comment(models.Model):
    """评论模型"""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, verbose_name="用户")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name="资源")
    content = models.TextField(max_length=500, verbose_name="评论内容")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="评论时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 评论了 {self.resource.title}"


class Report(models.Model):
    """举报模型"""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, verbose_name="举报用户")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name="被举报资源")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="举报时间")

    class Meta:
        verbose_name = "举报记录"
        verbose_name_plural = "举报记录"
        # 确保一个用户只能举报同一个资源一次
        unique_together = ['user', 'resource']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 举报了 {self.resource.title}"


class Like(models.Model):
    """点赞模型"""
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, verbose_name="用户")
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, verbose_name="资源")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="点赞时间")

    class Meta:
        verbose_name = "点赞记录"
        verbose_name_plural = "点赞记录"
        # 确保一个用户只能点赞同一个资源一次
        unique_together = ['user', 'resource']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 点赞了 {self.resource.title}"


