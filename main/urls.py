from django.urls import path
from main.views import show_main, is_admin_flutter

app_name = 'main'

app_name = 'main'
urlpatterns = [
    path('', show_main, name='main'),
    path('is-admin/', is_admin_flutter, name='is_admin_flutter'),
]