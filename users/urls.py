from django.urls import path
from users.views import (
    register, login_user, logout_user, profile,
    delete_account, change_username, change_password
)

app_name = 'users'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('delete/', delete_account, name='delete_account'),
    path('change-username/', change_username, name='change_username'),
    path('change-password/', change_password, name='change_password'),
]