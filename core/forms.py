from django import forms
from django.core.exceptions import ValidationError
from .models import Resource, Category, CloudType
from PIL import Image
import os


class ResourceUploadForm(forms.ModelForm):
    """资源上传表单"""
    # 截图字段，允许多个文件上传
    # 修改这一部分：
    screenshot = forms.ImageField(
        label='资源截图',
        required=False,
        help_text='上传资源截图（可选）'
    )

    class Meta:
        model = Resource
        fields = ['title', 'category', 'cloud_type', 'description',
                  'keywords', 'resource_url', 'extract_code', 'screenshot']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入资源标题'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'cloud_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请输入资源描述（可选）'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '用逗号分隔，如：电影,科幻,2023'
            }),
            'resource_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入资源链接（可包含中文）'
            }),
            'extract_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入提取码（可选）'
            }),
            'screenshot': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }
        labels = {
            'title': '资源标题',
            'category': '资源分类',
            'cloud_type': '网盘类型',
            'description': '资源描述',
            'keywords': '关键词',
            'resource_url': '资源链接',
            'extract_code': '提取码',
            'screenshot': '资源截图',
        }
        help_texts = {
            'keywords': '用逗号分隔多个关键词',
            'resource_url': '请输入完整的资源链接，可包含中文',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 只显示激活的分类和网盘类型
        self.fields['category'].queryset = Category.objects.all()
        self.fields['cloud_type'].queryset = CloudType.objects.filter(is_active=True)



    def clean_resource_url(self):
        """验证资源链接"""
        resource_url = self.cleaned_data.get('resource_url', '').strip()

        if not resource_url:
            raise ValidationError('资源链接不能为空')

        # 简单的链接格式验证（允许包含中文）
        if len(resource_url) < 10:
            raise ValidationError('链接长度太短，请检查链接是否正确')

        # 检查是否包含常见协议
        if not (resource_url.startswith('http://') or
                resource_url.startswith('https://') or
                resource_url.startswith('pan.baidu.com/') or
                resource_url.startswith('www.aliyundrive.com/')):
            # 这里可以添加更多常见网盘域名检查
            pass

        return resource_url

    def clean_keywords(self):
        """验证关键词"""
        keywords = self.cleaned_data.get('keywords', '').strip()

        if keywords:
            # 分割关键词并清理
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]

            # 限制关键词数量
            if len(keyword_list) > 10:
                raise ValidationError('关键词最多不能超过10个')

            # 限制每个关键词的长度
            for keyword in keyword_list:
                if len(keyword) > 20:
                    raise ValidationError(f'关键词 "{keyword}" 过长，每个关键词不能超过20个字符')

            # 重新组合为字符串
            keywords = ', '.join(keyword_list)

        return keywords

    def clean_screenshot(self):
        """验证截图"""
        screenshot = self.cleaned_data.get('screenshot')

        if screenshot:
            # 检查文件大小
            max_size = 5 * 1024 * 1024  # 5MB
            if screenshot.size > max_size:
                raise ValidationError('图片大小不能超过5MB')

            # 检查文件扩展名
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            import os
            ext = os.path.splitext(screenshot.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError('只支持JPG、PNG、GIF、WebP格式的图片')

        return screenshot

    def save(self, commit=True):
        """保存资源，但截图在视图中处理"""
        resource = super().save(commit=False)

        if commit:
            resource.save()

        return resource