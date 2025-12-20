from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from .models import Bookmark
import json

@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    data = []
    
    for bookmark in bookmarks:
        # Prevent errors if referenced object is deleted
        if bookmark.content_object:
            item = {
                'id': bookmark.id,
                'content_type': bookmark.content_type.model,
                'object_id': bookmark.object_id,
                'created_at': bookmark.created_at.isoformat(),
            }
            # Try to add a string representation or specific fields if possible
            try:
                item['title'] = str(bookmark.content_object)
                # You might want to customize this based on the model if needed
                # e.g., if model == 'studio', item['image'] = bookmark.content_object.thumbnail
            except:
                item['title'] = "Unknown Object"
                
            data.append(item)
            
    return JsonResponse({'status': 'success', 'bookmarks': data})

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def add_bookmark(request):
    try:
        data = json.loads(request.body)
        app_label = data.get('app_label')
        model_name = data.get('model')
        object_id = data.get('id')

        if not all([app_label, model_name, object_id]):
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)

        # Check if object exists (optional, but good practice)
        model_class = content_type.model_class()
        if not model_class.objects.filter(pk=object_id).exists():
             return JsonResponse({'status': 'error', 'message': 'Object not found'}, status=404)

        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=str(object_id)
        )

        if created:
            message = "Bookmark added"
        else:
            message = "Bookmark already exists"

        return JsonResponse({'status': 'success', 'message': message, 'bookmark_id': bookmark.id})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST", "DELETE"])
def remove_bookmark(request, bookmark_id=None):
    # Support both removing by ID in URL (typical REST) 
    # and removing by payload (referencing object) if needed.
    # Here implementing removal by bookmark_id for simplicity 
    # or by object details if bookmark_id not provided in URL?
    # Let's stick to simple URL param for delete usually, but user might send object details.
    
    # If using POST for everything (often easier in some mobile contexts if not strict REST),
    # let's parse body if bookmark_id is not in args.
    
    if bookmark_id:
        try:
            bookmark = Bookmark.objects.get(pk=bookmark_id, user=request.user)
            bookmark.delete()
            return JsonResponse({'status': 'success', 'message': 'Bookmark removed'})
        except Bookmark.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Bookmark not found'}, status=404)
            
    # If no ID provided, maybe they sent the object details to remove?
    # Let's handle parsing body for removal by object params
    try:
        data = json.loads(request.body)
        app_label = data.get('app_label')
        model_name = data.get('model')
        object_id = data.get('id')
        
        if all([app_label, model_name, object_id]):
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                bookmark = Bookmark.objects.get(
                    user=request.user,
                    content_type=content_type,
                    object_id=str(object_id)
                )
                bookmark.delete()
                return JsonResponse({'status': 'success', 'message': 'Bookmark removed'})
            except (ContentType.DoesNotExist, Bookmark.DoesNotExist):
                return JsonResponse({'status': 'error', 'message': 'Bookmark or Type not found'}, status=404)
    except:
        pass

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

