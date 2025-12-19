from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from users.forms import CustomUserCreationForm
from users.models import UserProfile
from users.forms import UserProfileModelForm
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def register(request):
    if request.user.is_authenticated:
        return redirect('main:main')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            kota = form.cleaned_data.get('kota')
            UserProfile.objects.create(user=user, kota=kota)
            
            messages.success(request, 'Registration successful. Please login.')
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.user.is_authenticated:
        return redirect('main:main')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('main:main')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = AuthenticationForm()
    
    context = {'form': form}
    return render(request, 'login.html', context)

@login_required(login_url='users:login')
def logout_user(request):
    logout(request)
    return redirect('users:login')


@login_required(login_url='users:login')
def profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserProfileModelForm(request.POST, instance=profile)
        current_password = request.POST.get('current_password')
        
        if not user.check_password(current_password):
            messages.error(request, 'Incorrect password.')
            return redirect('users:profile')
            
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileModelForm(instance=profile)

    return render(request, 'profile.html', {'form': form})


@login_required(login_url='users:login')
@require_POST
def change_username(request):
    user = request.user
    new_username = request.POST.get('new_username')
    current_password = request.POST.get('current_password')
    
    if not user.check_password(current_password):
        messages.error(request, 'Incorrect password.')
        return redirect('users:profile')
    
    if not new_username:
        messages.error(request, 'Please provide a new username.')
        return redirect('users:profile')
        
    if get_user_model().objects.filter(username=new_username).exclude(id=user.id).exists():
        messages.error(request, 'This username is already taken.')
        return redirect('users:profile')
        
    user.username = new_username
    user.save()
    messages.success(request, 'Username changed successfully.')
    return redirect('users:profile')

@login_required(login_url='users:login')
@require_POST
def change_password(request):
    user = request.user
    form = PasswordChangeForm(user, request.POST)
    
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Your password was successfully updated!')
    else:
        messages.error(request, 'Please correct the error below.')
    
    return redirect('users:profile')

@login_required(login_url='users:login')
@require_POST
def delete_account(request):
    user = request.user
    current_password = request.POST.get('current_password')
    
    if not user.check_password(current_password):
        messages.error(request, 'Incorrect password.')
        return redirect('users:profile')
        
    logout(request)
    user.delete()
    messages.success(request, 'Your account has been deleted.')
    return redirect('main:main')
# Mobile API endpoints
@csrf_exempt
def get_profile_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": False,
            "message": "User not authenticated."
        }, status=401)
    
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        kota = profile.kota
    except UserProfile.DoesNotExist:
        kota = None
    
    return JsonResponse({
        "status": True,
        "username": user.username,
        "kota": kota,
    }, status=200)

@csrf_exempt
def change_username_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": False,
            "message": "User not authenticated."
        }, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        new_username = data.get('new_username')
        current_password = data.get('current_password')
        
        user = request.user
        
        if not user.check_password(current_password):
            return JsonResponse({
                "status": False,
                "message": "Incorrect password."
            }, status=400)
        
        if not new_username:
            return JsonResponse({
                "status": False,
                "message": "Please provide a new username."
            }, status=400)
        
        # Validate username format
        if not new_username.isalnum():
            return JsonResponse({
                "status": False,
                "message": "Username must contain only letters and numbers."
            }, status=400)
        
        if len(new_username) > 20:
            return JsonResponse({
                "status": False,
                "message": "Username must be 20 characters or less."
            }, status=400)
            
        if get_user_model().objects.filter(username=new_username).exclude(id=user.id).exists():
            return JsonResponse({
                "status": False,
                "message": "This username is already taken."
            }, status=400)
            
        user.username = new_username
        user.save()
        return JsonResponse({
            "status": True,
            "message": "Username changed successfully.",
            "username": new_username
        }, status=200)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)

@csrf_exempt
def change_password_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": False,
            "message": "User not authenticated."
        }, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password1 = data.get('new_password1')
        new_password2 = data.get('new_password2')
        
        user = request.user
        
        if not user.check_password(old_password):
            return JsonResponse({
                "status": False,
                "message": "Incorrect old password."
            }, status=400)
        
        if new_password1 != new_password2:
            return JsonResponse({
                "status": False,
                "message": "New passwords do not match."
            }, status=400)
        
        if len(new_password1) < 8:
            return JsonResponse({
                "status": False,
                "message": "Password must be at least 8 characters long."
            }, status=400)
        
        user.set_password(new_password1)
        user.save()
        update_session_auth_hash(request, user)
        
        return JsonResponse({
            "status": True,
            "message": "Password changed successfully."
        }, status=200)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)

@csrf_exempt
def change_kota_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": False,
            "message": "User not authenticated."
        }, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        new_kota = data.get('kota')
        current_password = data.get('current_password')
        
        user = request.user
        
        if not user.check_password(current_password):
            return JsonResponse({
                "status": False,
                "message": "Incorrect password."
            }, status=400)
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.kota = new_kota
        profile.save()
        
        return JsonResponse({
            "status": True,
            "message": "City changed successfully.",
            "kota": new_kota
        }, status=200)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)

@csrf_exempt
def delete_account_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": False,
            "message": "User not authenticated."
        }, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        current_password = data.get('current_password')
        
        user = request.user
        
        if not user.check_password(current_password):
            return JsonResponse({
                "status": False,
                "message": "Incorrect password."
            }, status=400)
            
        logout(request)
        user.delete()
        
        return JsonResponse({
            "status": True,
            "message": "Account deleted successfully."
        }, status=200)
    
    return JsonResponse({
        "status": False,
        "message": "Invalid request method."
    }, status=400)
