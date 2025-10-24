from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from studio.models import Studio
from studio.forms import StudioForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core import serializers

from users.models import UserProfile

# Create your views here.

def show_studio(request):
    # Using AJAX to load studios
    return render(request, "studio/studio.html")

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def add_studio(request):
    form = StudioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Studio has been added successfully!')
        return redirect('studio:show_studio')
    
    context = {'form': form}
    return render(request, 'studio/add_studio.html', context)

@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def delete_studio(request, id):
    studio = get_object_or_404(Studio, id=id)
    studio_name = studio.nama_studio
    studio.delete()
    return JsonResponse({
        'success': True,
        'message': f'Studio "{studio_name}" has been deleted successfully!'
    })

def show_json(request):
    kota_list = ['Jakarta', 'Bogor', 'Depok', 'Tangerang', 'Bekasi']
    user_kota = None
    
    # Check if user has a city preference
    try:
        if request.user.is_authenticated:
            user_kota = request.user.profile.kota
    except UserProfile.DoesNotExist:
        pass
    
    response_data = {
        'user_kota': user_kota,
        'cities': []
    }
    
    # If user has a city, add it first
    if user_kota:
        studios = Studio.objects.filter(kota=user_kota).order_by('nama_studio')
        response_data['cities'].append({
            'name': user_kota,
            'is_user_city': True,
            'studios': [{
                'id': str(studio.id),
                'nama_studio': studio.nama_studio,
                'thumbnail': studio.thumbnail or '',
                'kota': studio.get_kota_display(),
                'area': studio.area,
                'alamat': studio.alamat,
                'gmaps_link': studio.gmaps_link or '',
                'nomor_telepon': studio.nomor_telepon,
            } for studio in studios]
        })
    
    # Add other cities
    for city in kota_list:
        if city == user_kota:
            continue
        studios = Studio.objects.filter(kota=city).order_by('nama_studio')
        response_data['cities'].append({
            'name': city,
            'is_user_city': False,
            'studios': [{
                'id': str(studio.id),
                'nama_studio': studio.nama_studio,
                'thumbnail': studio.thumbnail or '',
                'kota': studio.get_kota_display(),
                'area': studio.area,
                'alamat': studio.alamat,
                'gmaps_link': studio.gmaps_link or '',
                'nomor_telepon': studio.nomor_telepon,
            } for studio in studios]
        })
    
    return JsonResponse(response_data)