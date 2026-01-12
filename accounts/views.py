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


from django.utils import timezone


@login_required
def apply_upload_permission(request):
    """申请上传权限"""
    user = request.user

    # 如果用户已经有权限，重定向到首页
    if user.upload_permission:
        messages.info(request, '您已经有上传权限了')
        return redirect('core:index')

    # 如果已经申请过且正在审核中
    if user.apply_status == 'pending':
        messages.info(request, '您的申请正在审核中，请耐心等待')
        return redirect('accounts:permission_status')

    # 如果之前被拒绝过
    if user.apply_status == 'rejected':
        messages.warning(request, f'您的申请曾被拒绝。原因：{user.review_message or "无"}')

    if request.method == 'POST':
        # 处理申请
        user.apply_for_upload_permission()
        messages.success(request, '申请已提交，请等待管理员审核')
        return redirect('accounts:permission_status')

    # 服务条款内容
    terms_content = """
    <h3>资源分享服务条款</h3>

    <p><strong>请仔细阅读以下条款，确认同意后方可申请上传权限：</strong></p>

    <h4>一、总则</h4>
    <ol>
        <li>您必须遵守中华人民共和国相关法律法规</li>
        <li>不得上传任何违法、违规内容</li>
        <li>尊重他人知识产权，不得上传盗版资源</li>
        <li>不得上传色情、暴力、反动等不良内容</li>
    </ol>

    <h4>二、上传规范</h4>
    <ol>
        <li>上传的资源必须符合国家法律法规</li>
        <li>资源描述应真实准确，不得虚假宣传</li>
        <li>不得上传含有病毒、木马的文件</li>
        <li>网盘链接必须有效，不得使用虚假链接</li>
    </ol>

    <h4>三、违规处理</h4>
    <ol>
        <li>违规上传将被永久封禁账号</li>
        <li>严重违规将移交司法机关处理</li>
        <li>管理员有权删除任何违规内容</li>
    </ol>

    <h4>四、免责声明</h4>
    <ol>
        <li>本站不对用户上传的内容负责</li>
        <li>用户需自行承担上传内容的法律责任</li>
        <li>如发现违规内容，请立即举报</li>
    </ol>

    <p><strong>我已阅读并同意以上所有条款</strong></p>
    """

    context = {
        'terms_content': terms_content,
        'user_status': user.apply_status,
    }
    return render(request, 'accounts/apply_permission.html', context)


@login_required
def permission_status(request):
    """查看申请状态"""
    user = request.user
    context = {
        'user': user,
        'status_display': dict(user.APPLY_STATUS_CHOICES).get(user.apply_status, '未知'),
    }
    return render(request, 'accounts/permission_status.html', context)