from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('resource/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('category/<int:category_id>/', views.category_resources, name='category_resources'),
    path('search/', views.search_resources, name='search_resources'),
    path('upload/', views.upload_resource, name='upload_resource'),  # 添加上传页面
    path('resource/<int:resource_id>/like/', views.like_resource, name='like_resource'),
    path('resource/<int:resource_id>/favorite/', views.favorite_resource, name='favorite_resource'),
    path('resource/<int:resource_id>/comment/', views.add_comment, name='add_comment'),  # 添加评论
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),  # 删除评论
    path('resource/<int:resource_id>/report/', views.report_resource, name='report_resource'),
    path('resource/<int:resource_id>/increase-copy/', views.increase_copy_count, name='increase_copy_count'),
    #path('hot/', views.hot_resources, name='hot_resources'),
]