from django.urls import path
from main.views import show_main, show_about

app_name = 'main'
urlpatterns = [
    path('', show_main, name='main'),
    path('about/', show_about, name='about'),
]