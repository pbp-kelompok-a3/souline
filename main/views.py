from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from main.models import Studio
from users.models import UserProfile
from main.forms import StudioForm
import datetime

# Create your views here.

# Cek apakah user adalah admin
def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required(login_url='/login/')
def show_main(request):
    context = {}
    user_kota = None

    if request.user.is_authenticated:
        try:
            user_kota = request.user.profile.kota
            if user_kota:
                studios = Studio.objects.filter(kota=user_kota).order_by('?')[:6]
                context['studios'] = studios
            else:
                context['studios'] = Studio.objects.all().order_by('?')[:6]
        except UserProfile.DoesNotExist:
            context['studios'] = Studio.objects.all().order_by('?')[:6]
    else:
        context['studios'] = Studio.objects.all().order_by('?')[:6]
    
    context['user_kota'] = user_kota
    return render(request, "main.html", context)

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


