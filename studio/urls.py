from django.urls import path, include
from studio.views import *

app_name = 'studio'
urlpatterns = [
    path('', show_studio, name='show_studio'),
    path('add/', add_studio, name='add_studio'),
    path('edit/<uuid:id>/', edit_studio, name='edit_studio'),
    path('json/', show_json, name='show_json'),
    path('delete/<uuid:id>/', delete_studio, name='delete_studio'),
]

