from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

# Import models
from studio.models import Studio

# Create your views here.

# Cek apakah user adalah admin
def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required(login_url='/login/')
def show_main(request):
    context = {
        'user': request.user,
        'studios': Studio.objects.all().order_by('?')[:6],
    }

    return render(request, "main/main.html", context)

def show_studio(request):
    kota = ['Jakarta', 'Bogor', 'Depok', 'Tangerang', 'Bekasi']
    context = {}
    user_kota = None

    if request.user.is_authenticated:
        try:
            user_kota = request.user.profile.kota
            if user_kota:
                studios = Studio.objects.filter(kota=user_kota).order_by('nama_studio')
                context['user_kota'] = user_kota
                context['user_kota_studios'] = studios
                context['has_user_city'] = True
        except UserProfile.DoesNotExist:
            context['has_user_city'] = False
    else:
        context['has_user_city'] = False

    cities_with_studios = []
    for city in kota:
        if city == user_kota:
            continue
        studios = Studio.objects.filter(kota=city).order_by('nama_studio')
        cities_with_studios.append({
            'name': city,
            'studios': studios
        })
    
    context['cities_with_studios'] = cities_with_studios
    return render(request, "studio.html", context)

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def add_studio(request):
    form = StudioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Studio has been added successfully!')
        return redirect('studio')
    
    context = {'form': form}
    return render(request, 'add_studio.html', context)


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