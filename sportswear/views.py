import json
from django.shortcuts import render, redirect, get_object_or_404
#from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, Http404
from .models import SportswearBrand
from .forms import SportswearBrandForm
from .serializers import serialize_brand_list, serialize_brand_detail
from sportswear import serializers 

def is_admin(user):
    return user.is_authenticated and user.is_staff

@csrf_exempt 
def list_brands_api(request):
    tag = request.GET.get('tag')
    query = request.GET.get('q')

    brands = SportswearBrand.objects.all().order_by('brand_name')

    if tag and tag.strip() and tag.lower() != 'all' and tag != 'null':
        brands = brands.filter(category_tag__iexact=tag)

    if query and query.strip():
        brands = brands.filter(
            Q(brand_name__icontains=query) | 
            Q(description__icontains=query)
        )

    data = serialize_brand_list(brands, user=request.user) 
    return JsonResponse(data, safe=False)

@csrf_exempt
def create_brand_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            brand = SportswearBrand.objects.create(
                brand_name=data.get("name"),
                description=data.get("description"),
                category_tag=data.get("tag"),
                thumbnail_url=data.get("thumbnail"),
                average_rating=float(data.get("rating", 5.0)),
                link=data.get("link") 
            )
            return JsonResponse({'status': 'success', 'id': brand.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def update_brand_api(request): 
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            brand_id = data.get("id") 
            brand = SportswearBrand.objects.get(pk=brand_id)
            
            brand.brand_name = data.get("name", brand.brand_name)
            brand.description = data.get("description", brand.description)
            brand.category_tag = data.get("tag", brand.category_tag)
            brand.thumbnail_url = data.get("thumbnail", brand.thumbnail_url)
            brand.link = data.get("link", brand.link)
            brand.save()
            
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_brand_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            brand_id = data.get("id")
            brand = SportswearBrand.objects.get(pk=brand_id)
            brand.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
  
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
def show_sportswear(request):
    brands = SportswearBrand.objects.all().order_by('brand_name')
    for brand in brands:
        brand.latest_reviews = brand.reviews.all()[:3] 
        
    context = {
        'brands': brands,
    }
    return render(request, 'sportswear/sportswear_list.html', context)

#@login_required
@require_http_methods(["GET", "POST"])
def add_brand(request):
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

#@login_required
@require_http_methods(["GET", "POST"])
def edit_brand(request, pk):
        
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

#@login_required
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