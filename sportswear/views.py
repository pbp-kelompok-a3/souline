from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.http import JsonResponse, HttpResponseForbidden, Http404
from .models import SportswearBrand
from .forms import SportswearBrandForm

def is_admin(user):
    return user.is_authenticated and user.is_staff

# READ dan FILTER 

def show_sportswear(request):
    brands = SportswearBrand.objects.all().order_by('brand_name')
    context = {
        'brands': brands,
    }
    return render(request, 'sportswear/sportswear_list.html', context)


def filter_brands_ajax(request):
    """Endpoint AJAX untuk mencari brand (hanya Search Bar)."""
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


# CRUD ADMIN 

@login_required
def add_brand(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Akses Ditolak.")
        
    if request.method == 'POST':
        form = SportswearBrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sportswear:show_sportswear')
    else:
        form = SportswearBrandForm()
        
    return render(request, 'sportswear/add_edit_brand.html', {'form': form, 'title': 'Add New Brand'})

@login_required
def edit_brand(request, pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Akses Ditolak.")
        
    brand = get_object_or_404(SportswearBrand, pk=pk)
    
    if request.method == 'POST':
        form = SportswearBrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('sportswear:show_sportswear')
    else:
        form = SportswearBrandForm(instance=brand)
        
    return render(request, 'sportswear/add_edit_brand.html', {'form': form, 'title': 'Edit Brand'})

@login_required
def delete_brand(request, pk):
    if not is_admin(request.user):
        return JsonResponse({'status': 'error', 'message': 'Akses Ditolak.'}, status=403)
        
    if request.method == 'POST':
        try:
            brand = get_object_or_404(SportswearBrand, pk=pk)
            brand.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Metode tidak diizinkan.'}, status=405)