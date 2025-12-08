from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from studio.models import Studio
from studio.forms import StudioForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json, requests

from users.models import UserProfile

# Create your views here.

def show_studio(request):
    # Using AJAX to load studios
    return render(request, "studio/studio.html")

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required(login_url='/users/login/')
@user_passes_test(is_admin, login_url='/users/login/')
def add_studio(request):
    form = StudioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Studio has been added successfully!')
        return redirect('studio:show_studio')
    
    context = {'form': form}
    return render(request, 'studio/add_studio.html', context)

@login_required(login_url='/users/login/')
@user_passes_test(is_admin, login_url='/users/login/')
def edit_studio(request, id):
    studio = get_object_or_404(Studio, id=id)
    form = StudioForm(request.POST or None, instance=studio)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Studio "{studio.nama_studio}" has been updated successfully!')
        return redirect('studio:show_studio')
    
    context = {'form': form, 'studio': studio}
    return render(request, 'studio/edit_studio.html', context)

@login_required(login_url='/users/login/')
@user_passes_test(is_admin, login_url='/users/login/')
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
                'rating': studio.rating,
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
                'rating': studio.rating,
            } for studio in studios]
        })
    
    return JsonResponse(response_data)

@csrf_exempt
def create_studio_flutter(request):
    if request.method == 'POST':
        if not request.user.is_authenticated or not is_admin(request.user):
            return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)
            
        try:
            data = json.loads(request.body)
            new_studio = Studio.objects.create(
                nama_studio=data["nama_studio"],
                thumbnail=data.get("thumbnail", ""),
                kota=data["kota"],
                area=data["area"],
                alamat=data["alamat"],
                gmaps_link=data.get("gmaps_link", ""),
                nomor_telepon=data["nomor_telepon"],
                rating=data.get("rating", 5.0),
            )
            new_studio.save()
            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def edit_studio_flutter(request, id):
    if request.method == 'POST':
        if not request.user.is_authenticated or not is_admin(request.user):
            return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

        try:
            studio = Studio.objects.get(id=id)
            data = json.loads(request.body)
            
            studio.nama_studio = data.get("nama_studio", studio.nama_studio)
            studio.thumbnail = data.get("thumbnail", studio.thumbnail)
            studio.kota = data.get("kota", studio.kota)
            studio.area = data.get("area", studio.area)
            studio.alamat = data.get("alamat", studio.alamat)
            studio.gmaps_link = data.get("gmaps_link", studio.gmaps_link)
            studio.nomor_telepon = data.get("nomor_telepon", studio.nomor_telepon)
            studio.rating = data.get("rating", studio.rating)
            
            studio.save()
            return JsonResponse({"status": "success"}, status=200)
        except Studio.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Studio not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def delete_studio_flutter(request, id):
    if request.method == 'POST':
        if not request.user.is_authenticated or not is_admin(request.user):
            return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

        try:
            studio = Studio.objects.get(id=id)
            studio.delete()
            return JsonResponse({"status": "success"}, status=200)
        except Studio.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Studio not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=401)

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500) 