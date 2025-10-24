from django.urls import path
from . import views

app_name = 'events'
urlpatterns = [
    path('', views.show_events, name='event_list'),
    path('add/', views.add_event, name='add_event'),
    path('json/', views.show_json, name='show_json'),
    path('json/<str:filter_type>/', views.show_json_filtered, name='show_json_filtered'),
]
