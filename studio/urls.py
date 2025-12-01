from django.urls import path, include
from studio.views import *

app_name = 'studio'
urlpatterns = [
    path('', show_studio, name='show_studio'),
    path('add/', add_studio, name='add_studio'),
    path('edit/<uuid:id>/', edit_studio, name='edit_studio'),
    path('json/', show_json, name='show_json'),
    path('delete/<uuid:id>/', delete_studio, name='delete_studio'),
    path('create-flutter/', create_studio_flutter, name='create_studio_flutter'),
    path('edit-flutter/<uuid:id>/', edit_studio_flutter, name='edit_studio_flutter'),
    path('delete-flutter/<uuid:id>/', delete_studio_flutter, name='delete_studio_flutter')
]

