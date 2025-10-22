from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import datetime

# Import models
from studio.models import Studio
from users.models import UserProfile

# Create your views here.

# Cek apakah user adalah admin
def is_admin(user):
    return user.is_superuser or user.is_staff

def show_main(request):
    context = {
        'user': request.user
    }

    if request.user.is_authenticated:
        user_kota = request.user.profile.kota
        if user_kota:
            studios = Studio.objects.filter(kota=user_kota).order_by('?')[:6]
            context['studios'] = studios
    else:
        context['studios'] = Studio.objects.all().order_by('?')[:6]

    return render(request, "main/main.html", context)


