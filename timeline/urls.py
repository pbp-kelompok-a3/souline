from django.urls import path
from . import views

app_name = 'timeline'

urlpatterns = [
    path('', views.timeline_list, name='list'),
    path('post/<int:pk>/', views.post_detail, name='detail'),
    path('post/create/', views.create_post, name='create'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete'),
    path('post/<int:pk>/like/', views.toggle_like, name='like'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('json/', views.show_json, name='show_json'),


    path('api/timeline/', views.timeline_json, name='api_timeline'),
    path('is-admin', views.is_admin, name='is_admin'),
    path('api/create_post/', views.create_post_api, name='create_post_api'),
    path('api/post/<int:pk>/edit/', views.edit_post_api, name='edit_post_api'),
    path('api/post/<int:pk>/delete/', views.delete_post_api, name='delete_post_api'),    
    path('api/post/<int:pk>/like/', views.toggle_like_api, name='like_post_api'),
    path('api/post/<int:pk>/comment/', views.add_comment_api, name='add_comment_api'),
    path('api/comment/<int:pk>/edit/', views.edit_comment_api, name='edit_comment_api'),
    path('api/comment/<int:pk>/delete/', views.delete_comment_api, name='delete_comment_api'),
]