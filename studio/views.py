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
    kota = ['Jakarta', 'Bogor', 'Depok', 'Tangerang', 'Bekasi']
    context = {}
    user_kota = None

    try:
        if request.user.is_authenticated:
            user_kota = request.user.profile.kota
            if user_kota:
                studios = Studio.objects.filter(kota=user_kota).order_by('nama_studio')
                context['user_kota'] = user_kota
                context['user_kota_studios'] = studios
                context['has_user_city'] = True
        else:
            context['has_user_city'] = False
    except UserProfile.DoesNotExist:
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
    return render(request, "studio/studio.html", context)

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

def show_json(request):
    studios = Studio.objects.all()
    data = serializers.serialize('json', studios)
    return HttpResponse(data, content_type='application/json')

def show_json_by_id(request, id):
    studio = Studio.objects.get(id=id)
    data = serializers.serialize('json', studio)
    return HttpResponse(data, content_type='application/json')