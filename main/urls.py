from django.urls import path
from main.views import show_main, show_studio, add_studio

app_name = 'main'

urlpatterns = [
    path('', show_main, name='main'),
    path('studio/', show_studio, name='studio'),
    path('add-studio/', add_studio, name='add_studio'),
]