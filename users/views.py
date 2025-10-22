from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from users.forms import CustomUserCreationForm
from users.models import UserProfile


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
            return redirect('main:login')
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

@login_required(login_url='/login/')
def logout_user(request):
    logout(request)
    return redirect('main:login')