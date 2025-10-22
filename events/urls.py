from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_events, name='event_list'),
    path('add/', views.add_event, name='add_event'),
]
