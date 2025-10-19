from django.urls import path
from main.views import show_main, show_studio, register, add_studio

urlpatterns = [
    path('', show_main, name='main'),
    path('studio/', show_studio, name='studio'),
    path('register/', register, name='register'),
    path('add-studio/', add_studio, name='add_studio'),
]