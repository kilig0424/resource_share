from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # 添加自定义字段
    upload_permission = models.BooleanField(default=False, verbose_name="上传权限")
    agreed_to_terms = models.BooleanField(default=False, verbose_name="已同意条款")
    apply_time = models.DateTimeField(null=True, blank=True, verbose_name="申请时间")

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username