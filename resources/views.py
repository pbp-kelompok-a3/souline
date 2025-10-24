import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Resource
from django.views.decorators.csrf import csrf_exempt

#  HALAMAN UTAMA (menampilkan template list video)
def resource_list_page(request):
    return render(request, 'resources/resources_list.html')

def resource_form_page(request):
    return render(request, 'resources/resources_form.html')

def resource_edit_page(request, pk):
    return render(request, 'resources/resources_edit.html', {'resource_id': pk})

def resource_detail_page(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return render(request, 'resources/resources_detail.html', {'resource': resource})

#  API - READ
def resource_list_api(request):
    resources = Resource.objects.all().order_by('-created_at')
    data = []

    for r in resources:  # ← ini harus diindent di dalam fungsi
        video_id = ""
        if "embed/" in r.youtube_url:
            video_id = r.youtube_url.split("embed/")[1].split("?")[0]
        elif "v=" in r.youtube_url:
            video_id = r.youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in r.youtube_url:
            video_id = r.youtube_url.split("youtu.be/")[1].split("?")[0]

        data.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "youtube_url": r.youtube_url,
            "video_id": video_id,
            "thumbnail_url": r.thumbnail_url,
            "level": r.level,
        })

    return JsonResponse(data, safe=False)  


#  API - CREATE
@csrf_exempt
def add_resource(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        resource = Resource.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            youtube_url=data['youtube_url'],
            level=data.get('level', 'beginner'),
        )
        return JsonResponse({"status": "success", "id": resource.id})
    return JsonResponse({"status": "error"}, status=400)

#  API - UPDATE
@csrf_exempt
def edit_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        resource.title = data.get('title', resource.title)
        resource.description = data.get('description', resource.description)
        resource.youtube_url = data.get('youtube_url', resource.youtube_url)
        resource.level = data.get('level', resource.level)
        resource.save()
        return JsonResponse({"status": "updated"})
    return JsonResponse({"status": "error"}, status=400)

#  API - DELETE
@csrf_exempt
def delete_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    resource.delete()
    return JsonResponse({"status": "deleted"})