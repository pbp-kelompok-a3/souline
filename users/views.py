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

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save()
            
            # Get the kota from the POST data
            kota = form.cleaned_data.get('kota')
            
            # Create the user profile
            UserProfile.objects.create(user=user, kota=kota)
            
            # Redirect to login page
            messages.success(request, 'Registration successful. Please login.')
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main:main')
            else:
                messages.error(request, 'Invalid username or password.')
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
    logout(request)
    user.delete()
    messages.success(request, 'Your account has been deleted.')
    return redirect('main:main')