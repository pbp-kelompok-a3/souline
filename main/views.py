from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

# Import models
from studio.models import Studio

# Create your views here.

def show_main(request):
    context = {
        'user': request.user,
        'studios': Studio.objects.all().order_by('?')[:6],
    }

    return render(request, "main/main.html", context)

def show_about(request):
    return render(request, "main/about.html")
