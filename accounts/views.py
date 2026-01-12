from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from .forms import CustomUserCreationForm


def login_view(request):
    """用户登录视图"""
    if request.user.is_authenticated:
        return redirect('core:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{username}！')
                next_url = request.GET.get('next', 'core:index')
                return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """用户注册视图"""
    if request.user.is_authenticated:
        return redirect('core:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'注册成功！欢迎，{user.username}！')
            return redirect('core:index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    """用户退出视图"""
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('core:index')


@login_required
def apply_upload_permission(request):
    """申请上传权限"""
    if request.method == 'POST':
        user = request.user
        if not user.agreed_to_terms:
            user.agreed_to_terms = True
            user.apply_time = timezone.now()
            user.save()
            messages.success(request, '申请已提交，请等待管理员审核')
        else:
            messages.info(request, '您已经提交过申请，请等待管理员审核')
        return redirect('core:index')

    return render(request, 'accounts/apply_permission.html')