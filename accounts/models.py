from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    # 现有的字段
    upload_permission = models.BooleanField(default=False, verbose_name="上传权限")
    agreed_to_terms = models.BooleanField(default=False, verbose_name="已同意条款")
    apply_time = models.DateTimeField(null=True, blank=True, verbose_name="申请时间")

    # 添加新的字段
    APPLY_STATUS_CHOICES = [
        ('not_applied', '未申请'),
        ('pending', '审核中'),
        ('approved', '已通过'),
        ('rejected', '被拒绝'),
    ]
    apply_status = models.CharField(
        max_length=20,
        choices=APPLY_STATUS_CHOICES,
        default='not_applied',
        verbose_name="申请状态"
    )
    review_time = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")
    review_message = models.TextField(blank=True, verbose_name="审核备注")

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def apply_for_upload_permission(self):
        """用户申请上传权限"""
        self.agreed_to_terms = True
        self.apply_status = 'pending'
        self.apply_time = timezone.now()
        self.save()

    def approve_upload_permission(self, message=""):
        """管理员批准上传权限"""
        self.upload_permission = True
        self.apply_status = 'approved'
        self.review_time = timezone.now()
        self.review_message = message
        self.save()

    def reject_upload_permission(self, message=""):
        """管理员拒绝上传权限"""
        self.upload_permission = False
        self.apply_status = 'rejected'
        self.review_time = timezone.now()
        self.review_message = message
        self.save()