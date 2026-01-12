from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Category, Resource
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ResourceUploadForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, CloudType, Resource, Favorite, Comment


def index(request):
    """首页视图"""
    # 获取所有分类
    categories = Category.objects.all()

    # 获取最新的10个资源，按创建时间倒序排列
    latest_resources = Resource.objects.filter(is_approved=True).order_by('-created_at')[:10]

    context = {
        'categories': categories,
        'latest_resources': latest_resources,
    }
    return render(request, 'core/index.html', context)


def resource_detail(request, resource_id):
    """资源详情页面"""
    # 获取资源对象，如果不存在则返回404
    resource = get_object_or_404(Resource.objects.select_related('category', 'cloud_type', 'user'),
                                 id=resource_id, is_approved=True)

    # 增加查看次数
    resource.view_count += 1
    resource.save(update_fields=['view_count'])

    # 获取相关资源（同一分类下的其他资源，排除当前资源）
    related_resources = Resource.objects.filter(
        category=resource.category,
        is_approved=True
    ).exclude(id=resource.id).order_by('-created_at')[:6]

    # 获取评论，按创建时间倒序排列（最新的在最前面）
    comments = resource.comment_set.all().order_by('-created_at').select_related('user')

    context = {
        'resource': resource,
        'related_resources': related_resources,
        'comments': comments,  # 添加评论到上下文
    }
    return render(request, 'core/resource_detail.html', context)


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def category_resources(request, category_id):
    """分类页面"""
    # 获取分类对象
    category = get_object_or_404(Category, id=category_id)

    # 获取排序参数
    sort = request.GET.get('sort', 'newest')

    # 获取该分类下的资源，根据排序参数排序
    resources = Resource.objects.filter(category=category, is_approved=True)

    if sort == 'newest':
        resources = resources.order_by('-created_at')
    elif sort == 'hot':
        resources = resources.order_by('-view_count')
    elif sort == 'views':
        resources = resources.order_by('-view_count')
    elif sort == 'likes':
        resources = resources.order_by('-like_count')
    elif sort == 'copies':
        resources = resources.order_by('-copy_count')
    else:
        resources = resources.order_by('-created_at')

    # 分页处理
    paginator = Paginator(resources, 12)  # 每页12个资源
    page = request.GET.get('page')

    try:
        resources = paginator.page(page)
    except PageNotAnInteger:
        resources = paginator.page(1)
    except EmptyPage:
        resources = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'resources': resources,
        'sort': sort,
    }
    return render(request, 'core/category.html', context)


from django.db.models import Q


def search_resources(request):
    """搜索资源"""
    query = request.GET.get('q', '').strip()

    if not query:
        # 如果没有输入搜索词，返回首页
        return redirect('core:index')

    # 构建搜索查询
    # 搜索标题、描述和关键词
    resources = Resource.objects.filter(is_approved=True).filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(keywords__icontains=query)
    ).distinct().order_by('-created_at')

    # 统计搜索到的资源数量
    total_count = resources.count()

    # 分页处理
    paginator = Paginator(resources, 12)  # 每页12个结果
    page = request.GET.get('page')

    try:
        resources = paginator.page(page)
    except PageNotAnInteger:
        resources = paginator.page(1)
    except EmptyPage:
        resources = paginator.page(paginator.num_pages)

    context = {
        'query': query,
        'resources': resources,
        'total_count': total_count,
    }
    return render(request, 'core/search_results.html', context)


@login_required
def upload_resource(request):
    """上传资源视图"""
    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES)

        if form.is_valid():
            # 保存资源基本信息（包括截图）
            resource = form.save(commit=False)
            resource.user = request.user
            resource.is_approved = True
            resource.save()

            messages.success(request, '资源上传成功！')
            return redirect('core:resource_detail', resource_id=resource.id)
        else:
            messages.error(request, '表单填写有误，请检查后重新提交')
    else:
        form = ResourceUploadForm()

    context = {
        'form': form,
        'page_title': '上传资源',
    }
    return render(request, 'core/upload_resource.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
@require_POST
def like_resource(request, resource_id):
    """点赞或取消点赞资源"""
    resource = get_object_or_404(Resource, id=resource_id)
    user = request.user

    # 检查用户是否已经点赞过该资源
    from .models import Like
    like, created = Like.objects.get_or_create(user=user, resource=resource)

    if not created:
        # 如果已经点赞过，则取消点赞（删除记录）
        like.delete()
        resource.like_count -= 1
        liked = False
    else:
        # 新增点赞
        resource.like_count += 1
        liked = True

    resource.save(update_fields=['like_count'])

    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'like_count': resource.like_count
    })


@login_required
@require_POST
def favorite_resource(request, resource_id):
    """收藏或取消收藏资源"""
    resource = get_object_or_404(Resource, id=resource_id)
    user = request.user

    # 检查用户是否已经收藏过该资源
    favorite, created = Favorite.objects.get_or_create(user=user, resource=resource)

    if not created:
        # 如果已经收藏过，则取消收藏（删除记录）
        favorite.delete()
        resource.collect_count -= 1
        favorited = False
    else:
        # 新增收藏
        resource.collect_count += 1
        favorited = True

    resource.save(update_fields=['collect_count'])

    return JsonResponse({
        'status': 'success',
        'favorited': favorited,
        'collect_count': resource.collect_count
    })


@login_required
@require_POST
def add_comment(request, resource_id):
    """添加评论"""
    resource = get_object_or_404(Resource, id=resource_id)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({
            'status': 'error',
            'message': '评论内容不能为空'
        }, status=400)

    # 检查评论长度（不超过200字）
    if len(content) > 200:
        return JsonResponse({
            'status': 'error',
            'message': '评论内容不能超过200字'
        }, status=400)

    # 检查是否包含链接
    import re
    link_patterns = [
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        r'www\\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}',  # 邮箱地址
    ]

    for pattern in link_patterns:
        if re.search(pattern, content):
            return JsonResponse({
                'status': 'error',
                'message': '评论内容不能包含链接或邮箱地址'
            }, status=400)

    # 创建评论
    comment = Comment.objects.create(
        user=request.user,
        resource=resource,
        content=content
    )

    # 更新资源的评论计数
    resource.comment_count += 1
    resource.save(update_fields=['comment_count'])

    return JsonResponse({
        'status': 'success',
        'comment_id': comment.id,
        'username': request.user.username,
        'content': content,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
        'comment_count': resource.comment_count
    })


@login_required
@require_POST
def delete_comment(request, comment_id):
    """删除评论"""
    comment = get_object_or_404(Comment, id=comment_id)

    # 检查用户是否有权限删除（评论作者或管理员）
    if comment.user != request.user and not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': '您没有权限删除此评论'
        }, status=403)

    # 获取关联的资源，以便更新评论计数
    resource = comment.resource

    # 删除评论
    comment.delete()

    # 更新资源的评论计数
    resource.comment_count = max(0, resource.comment_count - 1)  # 确保不为负数
    resource.save(update_fields=['comment_count'])

    return JsonResponse({
        'status': 'success',
        'message': '评论已删除',
        'comment_count': resource.comment_count
    })