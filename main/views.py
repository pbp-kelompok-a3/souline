from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date, timedelta
import datetime

# Import models
from studio.models import Studio
from users.models import UserProfile
from timeline.models import Post
from timeline.forms import PostForm
from resources.models import Resource
from events.models import Event
from sportswear.models import SportswearBrand
# Create your views here.

# Cek apakah user adalah admin
def is_admin(user):
    return user.is_superuser or user.is_staff

def show_main(request):
    context = {
        'user': request.user
    }

    # Studios
    if request.user.is_authenticated and request.user.profile.kota:
        studios = Studio.objects.filter(kota=request.user.profile.kota).order_by('?')[:10]
        context['studios'] = studios
    else:
        context['studios'] = Studio.objects.all().order_by('?')[:10]

    # Resources - Get 6 recent resources
    resources = Resource.objects.all().order_by('-created_at')[:6]
    context['resources'] = resources

    # Timeline - Get 5 recent posts
    posts = (
        Post.objects
        .select_related('author')
        .prefetch_related('likes', 'comments__author')
        .order_by('-created_at')[:2]
    )
    post_form = PostForm()
    context['posts'] = posts
    context['post_form'] = post_form

    # Events - Get 3 upcoming events
    today = date.today()
    events = Event.objects.filter(date__gte=today).order_by('date')[:3]
    context['events'] = events

    # Sportswear - Get 6 brands
    sportswear_brands = SportswearBrand.objects.all().order_by('brand_name')[:6]
    context['sportswear_brands'] = sportswear_brands

    return render(request, "main/main.html", context)