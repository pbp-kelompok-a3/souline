from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import datetime

# Import models
from studio.models import Studio
from users.models import UserProfile
from timeline.models import Post
from timeline.forms import PostForm
# Create your views here.

# Cek apakah user adalah admin
def is_admin(user):
    return user.is_superuser or user.is_staff

def show_main(request):
    context = {
        'user': request.user
    }

    if request.user.is_authenticated and request.user.profile.kota:
        studios = Studio.objects.filter(kota=request.user.profile.kota).order_by('?')[:10]
        context['studios'] = studios
    else:
        context['studios'] = Studio.objects.all().order_by('?')[:10]

    posts = (
        Post.objects
        .select_related('author')
        .prefetch_related('likes', 'comments__author')
        .order_by('-created_at')[:10]
    )
    post_form = PostForm()

    context['posts'] = posts
    context['post_form'] = post_form

    return render(request, "main/main.html", context)