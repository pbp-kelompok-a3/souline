from django.urls import path, include
from studio.views import *

app_name = 'studio'
urlpatterns = [
    path('', show_studio, name='show_studio'),
    path('add/', add_studio, name='add_studio'),
    path('json/', show_json, name='json_all'),
    path('json/<int:id>/', show_json_by_id, name='json_by_id'),
]

