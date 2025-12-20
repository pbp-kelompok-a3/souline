import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.http import JsonResponse, HttpResponseForbidden, Http404
from .models import SportswearBrand
from .forms import SportswearBrandForm
from .serializers import serialize_brand_list, serialize_brand_detail 

def is_admin(user):
    return user.is_authenticated and user.is_staff

@csrf_exempt
@require_GET
def list_brands_api(request):
    brands = SportswearBrand.objects.prefetch_related(
        'reviews', 
        'posts', 
        'posts__author'
    ).all()
    
    # Filtering (Search and Tag)
    query = request.GET.get('q', '')
    tag = request.GET.get('tag', '')

    if query:
        brands = brands.filter(
            Q(brand_name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if tag and tag.lower() != 'all':
        brands = brands.filter(category_tag__iexact=tag)
    
    brands = brands.order_by('-average_rating', 'brand_name')
    
    # Serialisasi data 
    serialized_data = serialize_brand_list(brands, user=request.user)
    
    return JsonResponse(serialized_data, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
@login_required 
def create_brand_api(request):
    
    if not is_admin(request.user):
        return JsonResponse({'status': 'error', 'message': 'Akses Ditolak (Admin Only).'}, status=403)
    
    if not request.body:
        return JsonResponse({'status': 'error', 'message': 'Request body is empty.'}, status=400)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    
    if 'name' in data:
        data['brand_name'] = data.pop('name')
    if 'thumbnail' in data:
        data['thumbnail_url'] = data.pop('thumbnail')
    if 'tag' in data:
        data['category_tag'] = data.pop('tag')
    if 'rating' in data:
        data['average_rating'] = data.pop('rating')
    
    form = SportswearBrandForm(data)
    
    if form.is_valid():
        brand = form.save()
        # Mengembalikan data brand yang baru dibuat
        return JsonResponse(serialize_brand_detail(brand, user=request.user), status=201)
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@csrf_exempt
@require_http_methods(["PUT"]) 
@login_required 
def update_brand_api(request, pk):
    """Endpoint API untuk mengupdate brand (UPDATE - Method PUT)."""
        
    brand = get_object_or_404(SportswearBrand, pk=pk)
    
    if not request.body:
        return JsonResponse({'status': 'error', 'message': 'Request body is empty.'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)

    if 'name' in data:
        data['brand_name'] = data.pop('name')
        
    if 'thumbnail' in data:
        data['thumbnail_url'] = data.pop('thumbnail')
        
    if 'tag' in data:
        data['category_tag'] = data.pop('tag')
        
    if 'rating' in data:
        data['average_rating'] = data.pop('rating')

    form = SportswearBrandForm(data, instance=brand)
    
    if form.is_valid():
        brand = form.save()
        return JsonResponse(serialize_brand_detail(brand, user=request.user), status=200)
    else:
        print(form.errors) 
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"]) 
@login_required 
def delete_brand_api(request, pk):
    """Endpoint API untuk menghapus brand (DELETE - Method DELETE)."""
    
    if not is_admin(request.user):
      return JsonResponse({'status': 'error', 'message': 'Akses Ditolak (Admin Only).'}, status=403)
    
    try:
        brand = get_object_or_404(SportswearBrand, pk=pk)
        brand.delete()
        
        return JsonResponse({'status': 'success', 'message': f'Brand ID {pk} deleted successfully.'}, status=200)
        
    except Http404:
        return JsonResponse({'status': 'error', 'message': f'Brand ID {pk} not found.'}, status=404)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def show_sportswear(request):
    brands = SportswearBrand.objects.all().order_by('brand_name')
    for brand in brands:
        brand.latest_reviews = brand.reviews.select_related('reviewer').all()[:3]
        
    context = {
        'brands': brands,
    }
    return render(request, 'sportswear/sportswear_list.html', context)

@require_GET
def filter_brands_ajax(request):
    """Endpoint AJAX untuk mencari brand (Web Search Bar)."""
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        raise Http404
        
    query = request.GET.get('q', '')

    brands = SportswearBrand.objects.all()

    # Filter Berdasarkan Pencarian Teks
    if query:
        brands = brands.filter(
            Q(brand_name__icontains=query) | 
            Q(description__icontains=query)
        )
        
    brands = brands.order_by('brand_name')
        
    return render(request, 'sportswear/brand_cards.html', {'brands': brands})


# CRUD ADMIN (HTML/AJAX)

@login_required
@require_http_methods(["GET", "POST"])
def add_brand(request):
    # if not is_admin(request.user): ...
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = SportswearBrandForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success', 'message': 'Brand berhasil ditambahkan!'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        
        form = SportswearBrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sportswear:show_sportswear') 
    else:
        form = SportswearBrandForm()
        
    return render(request, 'sportswear/add_edit_brand.html', {'form': form, 'title': 'Add New Brand'})

@login_required
@require_http_methods(["GET", "POST"])
def edit_brand(request, pk):
    # if not is_admin(request.user): ...
        
    brand = get_object_or_404(SportswearBrand, pk=pk)
    
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = SportswearBrandForm(request.POST, instance=brand)
            if form.is_valid():
                form.save()
                return JsonResponse({'status': 'success', 'message': f'Brand {brand.brand_name} berhasil diupdate!'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

        form = SportswearBrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('sportswear:show_sportswear') 
    else:
        form = SportswearBrandForm(instance=brand)
        
    return render(request, 'sportswear/add_edit_brand.html', {'form': form, 'title': 'Edit Brand'})

@login_required
@require_POST
def delete_brand(request, pk):
    """Fungsi Hapus Brand untuk Web Admin (Menerima Method POST)."""
    if not is_admin(request.user):
        return JsonResponse({'status': 'error', 'message': 'Access Denied.'}, status=403) 
        
    try:
        brand = get_object_or_404(SportswearBrand, pk=pk)
        brand.delete()
        return JsonResponse({'status': 'success'}, status=200) 
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)