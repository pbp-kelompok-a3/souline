from django.urls import path
from . import views

app_name = 'sportswear'
urlpatterns = [
    path('', views.show_sportswear, name='show_sportswear'),
    path('filter_ajax/', views.filter_brands_ajax, name='filter_brands_ajax'),

    path('add/', views.add_brand, name='add_brand'),
    path('edit/<int:pk>/', views.edit_brand, name='edit_brand'),
    path('delete/<int:pk>/', views.delete_brand, name='delete_brand'),

    # API Endpoints
    path('api/list/', views.list_brands_api, name='list_brands_api'),
    path('api/create/', views.create_brand_api, name='create_brand_api'), 
    path('api/update/<int:pk>/', views.update_brand_api, name='update_brand_api'), 
    path('api/delete/<int:pk>/', views.delete_brand_api, name='delete_brand_api'),
]