from django.urls import path
from users.views import (
    register, login_user, logout_user, profile,
    delete_account, change_username, change_password,
    get_profile_flutter, change_username_flutter, change_password_flutter,
    change_kota_flutter, delete_account_flutter
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
    # Flutter API endpoints
    path('get-profile-flutter/', get_profile_flutter, name='get_profile_flutter'),
    path('change-username-flutter/', change_username_flutter, name='change_username_flutter'),
    path('change-password-flutter/', change_password_flutter, name='change_password_flutter'),
    path('change-kota-flutter/', change_kota_flutter, name='change_kota_flutter'),
    path('delete-account-flutter/', delete_account_flutter, name='delete_account_flutter'),
]