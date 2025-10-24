from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.resource_list_page, name='resource_list'), 
    path('add/', views.resource_form_page, name='resource_form_page'),
    path('edit/<int:pk>/', views.resource_edit_page, name='resource_edit_page'),
    path('<int:pk>/', views.resource_detail_page, name='resource_detail_page'),
                
    path('api/', views.resource_list_api, name='resource_list_api'),      
    path('api/add/', views.add_resource, name='add_resource_api'),   
    path('api/edit/<int:pk>/', views.edit_resource, name='edit_resource_api'),  
    path('api/delete/<int:pk>/', views.delete_resource, name='delete_resource_api'),  
]