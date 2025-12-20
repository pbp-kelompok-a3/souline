from django.urls import path
from . import views

app_name = 'events'
urlpatterns = [
    path('', views.show_events, name='event_list'),
    path('add/', views.add_event, name='add_event'),
    path('json/', views.events_json, name='events_json'), 
    path('<int:id>/', views.event_detail, name='event_detail'),
    path('edit/<int:id>/', views.edit_event, name='edit_event'),
    path('delete/<int:id>/', views.delete_event, name='delete_event'),
    path('api/create/', views.add_event_api, name='add_event_api'),
    path('api/<int:id>/edit/', views.edit_event_api, name='edit_event_api'),
    path('api/<int:id>/delete/', views.delete_event_api, name='delete_event_api')

]
