from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.get_bookmarks, name='get_bookmarks'),
    path('add/', views.add_bookmark, name='add_bookmark'),
    path('remove/<int:bookmark_id>/', views.remove_bookmark, name='remove_bookmark_by_id'),
    path('remove/', views.remove_bookmark, name='remove_bookmark_by_object'),
]
