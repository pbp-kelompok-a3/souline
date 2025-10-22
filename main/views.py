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

@login_required(login_url='/login/')
def show_main(request):
    context = {
        'user': request.user,
        'studios': Studio.objects.all().order_by('?')[:6],
    }

    return render(request, "main/main.html", context)


