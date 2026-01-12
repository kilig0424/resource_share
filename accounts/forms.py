from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """自定义用户注册表单"""
    email = forms.EmailField(required=True, label='邮箱')
    agree_to_terms = forms.BooleanField(
        required=True,
        label='同意服务条款',
        help_text='请阅读并同意我们的服务条款'
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'agree_to_terms')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.agreed_to_terms = self.cleaned_data['agree_to_terms']

        if commit:
            user.save()
        return user