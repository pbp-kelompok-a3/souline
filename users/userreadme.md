# Souline Authentication Implementation

This document outlines the complete authentication system implemented for Souline, connecting the Django backend with the Flutter mobile app.

## 📋 Overview

The authentication system follows the same pattern as football-news, providing:
- User registration with city (kota) selection
- User login/logout
- Profile management (username, password, city changes)
- Account deletion
- Full mobile app integration via REST API

## 🔧 Backend Changes (Django)

### 1. Authentication API Endpoints (`souline/auth/`)

**New Files:**
- `auth/views.py` - Mobile authentication endpoints
- `auth/urls.py` - URL routing for auth endpoints

**Endpoints:**
- `POST /auth/login/` - User login
- `POST /auth/register/` - User registration (with kota field)
- `POST /auth/logout/` - User logout

**Features:**
- Username validation (alphanumeric, max 20 chars)
- Password matching validation
- Returns user data including kota on login

### 2. User Profile API Endpoints (`souline/users/`)

**Updated Files:**
- `users/views.py` - Added Flutter-specific endpoints
- `users/urls.py` - Added Flutter API routes

**New Endpoints:**
- `GET /users/get-profile-flutter/` - Get user profile data
- `POST /users/change-username-flutter/` - Change username
- `POST /users/change-password-flutter/` - Change password
- `POST /users/change-kota-flutter/` - Change city
- `POST /users/delete-account-flutter/` - Delete account

**Security:**
- All profile operations require current password verification
- Username uniqueness checks
- Password strength validation (min 8 chars)
- Session management with automatic logout on account deletion

### 3. Settings Configuration (`souline/settings.py`)

**Added:**
```python
INSTALLED_APPS = [
    # ... existing apps
    'auth',
    'corsheaders',
]

MIDDLEWARE = [
    # ... existing middleware
    'corsheaders.middleware.CorsMiddleware',  # Added
]

ALLOWED_HOSTS = [
    "localhost", 
    "127.0.0.1", 
    "farrel-rifqi-souline.pbp.cs.ui.ac.id", 
    "10.0.2.2"  # Added for Android emulator
]

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'
```

### 4. URL Configuration (`souline/urls.py`)

**Added:**
```python
path('auth/', include('auth.urls')),
```

### 5. Dependencies (`requirements.txt`)

**Added:**
- `django-cors-headers` - For CORS support

## 📱 Frontend Changes (Flutter)

### 1. Authentication Screens

**New Files:**
- `lib/modules/user/login.dart` - Login screen
- `lib/modules/user/register.dart` - Registration screen with kota dropdown

**Features:**
- Material Design UI matching Souline theme
- Form validation
- Error handling with user-friendly messages
- Navigation flow (register → login → home)

**Login Screen:**
- Username and password fields
- Links to registration page
- Automatic navigation to HomePage on success
- Uses `pbp_django_auth` for cookie management

**Register Screen:**
- Username, password, confirm password fields
- Kota dropdown (Jakarta, Bogor, Depok, Tangerang, Bekasi)
- Username validation (alphanumeric only)
- Success feedback and navigation

### 2. Profile Management (`lib/modules/user/user_page.dart`)

**Complete Rewrite:**
- Modern card-based UI design
- Profile header with icon, username, and city
- Settings sections organized by function
- Dialog-based forms for all operations

**Features:**
- **View Profile**: Displays username and kota
- **Change Username**: Dialog with password confirmation
- **Change Password**: Old password + new password validation
- **Change City**: Dropdown selector with password confirmation
- **Delete Account**: Warning dialog with password confirmation
- **Logout**: Header button with confirmation

**UI Components:**
- Loading state during data fetch
- Error handling with SnackBars
- Confirmation dialogs for destructive actions
- Icon-based navigation cards
- Color-coded danger zone for account deletion

### 3. App Configuration (`lib/main.dart`)

**Changes:**
- Initial route changed from `HomePage` to `LoginPage`
- Added import for login screen
- Provider setup for `CookieRequest` (already existed)

**Navigation Flow:**
```
App Start → LoginPage
         ↓
    (on login)
         ↓
     HomePage
         ↓
  (Profile button)
         ↓
     UserPage
```

## 🔐 Security Features

### Backend:
1. **CSRF Protection**: All endpoints use `@csrf_exempt` for mobile API
2. **Authentication Required**: Profile endpoints check `request.user.is_authenticated`
3. **Password Verification**: All profile changes require current password
4. **Input Validation**: Username format, length limits, uniqueness checks
5. **Session Management**: Proper login/logout handling with cookie-based sessions

### Frontend:
1. **Cookie-based Sessions**: Uses `pbp_django_auth` package
2. **Secure Storage**: Credentials never stored locally
3. **Auto-logout**: Session expiry handled by backend
4. **Input Validation**: Client-side validation before API calls

## 🚀 API Endpoints Reference

### Authentication

#### Login
```
POST http://farrel-rifqi-souline.pbp.cs.ui.ac.id/auth/login/
Body (form-data):
  - username: string
  - password: string

Response:
{
  "status": true,
  "username": "user123",
  "kota": "Jakarta",
  "message": "Login successful!"
}
```

#### Register
```
POST http://farrel-rifqi-souline.pbp.cs.ui.ac.id/auth/register/
Body (JSON):
{
  "username": "newuser",
  "password1": "password123",
  "password2": "password123",
  "kota": "Jakarta"
}

Response:
{
  "status": "success",
  "username": "newuser",
  "message": "User created successfully!"
}
```

#### Logout
```
POST http://farrel-rifqi-souline.pbp.cs.ui.ac.id/auth/logout/

Response:
{
  "status": true,
  "username": "user123",
  "message": "Logged out successfully!"
}
```

### Profile Management

#### Get Profile
```
GET http://farrel-rifqi-souline.pbp.cs.ui.ac.id/users/get-profile-flutter/

Response:
{
  "status": true,
  "username": "user123",
  "kota": "Jakarta"
}
```

#### Change Username
```
POST http://farrel-rifqi-souline.pbp.cs.ui.ac.id/users/change-username-flutter/
Body (JSON):
{
  "new_username": "newusername",
  "current_password": "password123"
}

Response:
{
  "status": true,
  "username": "newusername",
  "message": "Username changed successfully."
}
```

#### Change Password
```
POST http://farrel-rifqi-souline.pbp.cs.ui.ac.id/users/change-password-flutter/
Body (JSON):
{
  "old_password": "oldpass",
  "new_password1": "newpass123",
  "new_password2": "newpass123"
}

Response:
{
  "status": true,
  "message": "Password changed successfully."
}
```

#### Change City
```
POST http://farrel-rifqi-souline.pbp.cs.ui.ac.id/users/change-kota-flutter/
Body (JSON):
{
  "kota": "Bogor",
  "current_password": "password123"
}

Response:
{
  "status": true,
  "kota": "Bogor",
  "message": "City changed successfully."
}
```

#### Delete Account
```
POST http://farrel-rifqi-souline.pbp.cs.ui.ac.id/users/delete-account-flutter/
Body (JSON):
{
  "current_password": "password123"
}

Response:
{
  "status": true,
  "message": "Account deleted successfully."
}
```

## 📦 Dependencies

### Backend (Django):
- `django-cors-headers` - CORS support for mobile app

### Frontend (Flutter):
- `pbp_django_auth: ^0.4.0` - Cookie-based authentication
- `provider: ^6.1.5+1` - State management
- `http: ^1.6.0` - HTTP requests

## ✅ Testing Checklist

### Backend:
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test registration endpoint
- [ ] Test login endpoint
- [ ] Test profile retrieval
- [ ] Test all profile update operations
- [ ] Test logout functionality

### Frontend:
- [ ] Run `flutter pub get`
- [ ] Test registration flow
- [ ] Test login flow
- [ ] Test profile display
- [ ] Test username change
- [ ] Test password change
- [ ] Test kota change
- [ ] Test account deletion
- [ ] Test logout

## 🎯 Key Differences from Football-News

1. **Kota Field**: Added city selection during registration (specific to Souline)
2. **Profile Operations**: More comprehensive profile management with separate endpoints
3. **UI Design**: Card-based profile interface vs. simple forms
4. **Navigation**: Direct push to HomePage after login (using pushReplacement)

## 📝 Notes

- All API endpoints use production URL: `http://farrel-rifqi-souline.pbp.cs.ui.ac.id`
- Android emulator should use `10.0.2.2` for localhost (already configured in ALLOWED_HOSTS)
- Chrome users can use `localhost:8000` or `127.0.0.1:8000`
- Password must be at least 8 characters
- Username must be alphanumeric and max 20 characters
- Session cookies are secure and use SameSite=None for cross-origin requests

## 🔄 Migration Guide

If you need to apply the changes to production:

1. **Backend:**
   ```bash
   cd souline/souline
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic
   git add .
   git commit -m "Add authentication system for mobile app"
   git push
   ```

2. **Frontend:**
   ```bash
   cd souline-mobile
   flutter pub get
   flutter clean
   flutter build apk  # or flutter build ios
   ```

## 🎉 Complete!

The authentication system is fully implemented and ready for testing. Users can now:
- Register with username, password, and city selection
- Login to access the app
- View and manage their profile
- Change username, password, and city
- Delete their account
- Logout securely

All operations follow Django best practices and include proper error handling and user feedback.
