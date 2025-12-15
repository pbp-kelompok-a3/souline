import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from .forms import PostForm, CommentForm
from .models import Post, Comment, Resource, SportswearBrand

def timeline_list(request):
    posts_qs = Post.objects.select_related('author').prefetch_related('likes', 'comments__author').all().order_by('created_at')
    paginator = Paginator(posts_qs, 10)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)

    post_form = PostForm()
    comment_form = CommentForm()
    context = {
        'posts': posts,
        'post_form': post_form,
        'comment_form': comment_form,
    }
    return render(request, 'timeline_list.html', context)

@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    post = form.save(commit=False)
    post.author = request.user
    post.save()

    html = render_to_string('_post.html', {'post': post, 'user': request.user}, request=request)
    return JsonResponse({'success': True, 'html': html})

@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
        action = 'unliked'
    else:
        post.likes.add(user)
        action = 'liked'
    return JsonResponse({'success': True, 'action': action, 'like_count': post.like_count})

@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get('text')
    if not content:
        return JsonResponse({'error': 'empty'}, status=400)

    comment = Comment.objects.create(post=post, author=request.user, text=content)
    return JsonResponse({
        'id': comment.id,
        'author_username': comment.author.username,
        'content': comment.text
    }, status=201)

def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author').prefetch_related('comments__author', 'likes'), pk=pk)
    comment_form = CommentForm()
    return render(request, 'post_detail.html', {'post': post, 'comment_form': comment_form})

@login_required
@require_POST
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return JsonResponse({'success': False, 'error': 'permission_denied'}, status=403)

    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'success': False, 'error': 'empty_text'}, status=400)

    post.text = text
    post.save()
    html = render_to_string('_post.html', {'post': post, 'user': request.user}, request=request)
    return JsonResponse({'success': True, 'html': html})

@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return JsonResponse({'success': False, 'error': 'permission_denied'}, status=403)
    post.delete()
    return JsonResponse({'success': True})

def show_json(request):
    posts = Post.objects.all().order_by('-created_at')
    data = []
    for post in posts:
        data.append({
            "username": post.author.username,
            "text": post.text,
            "image": post.image.url if post.image else "",
            "created_at": post.created_at.isoformat(),
        })
    return JsonResponse(data, safe=False)




def timeline_json(request):
    page = int(request.GET.get('page', 1))
    posts_qs = (
        Post.objects
        .select_related('author')
        .prefetch_related('comments__author', 'likes') 
        .order_by('-created_at')
    )

    paginator = Paginator(posts_qs, 10)
    page_obj = paginator.get_page(page)

    next_url = f"?page={page_obj.next_page_number()}" if page_obj.has_next() else None

    results = []
    for p in page_obj.object_list:
        comments_list = [
            {
                'id': c.id,
                'author_username': c.author.username,
                'content': c.text,
                'created_at': c.created_at.isoformat(),
            }
            for c in p.comments.all().order_by('-created_at')
        ]

        attachment_data = None
        if p.resource: 
            attachment_data = {
                "type": "Resources",
                "id": p.resource.id,
                "name": p.resource.title,
                "thumbnail": p.resource.thumbnail_url if p.resource.thumbnail_url else "",
                "link": p.resource.link if hasattr(p.resource, 'link') else ""
            }
        elif p.sportswear: 
            attachment_data = {
                "type": "Sportswear",
                "id": p.sportswear.id,
                "name": p.sportswear.title,
                "thumbnail": p.sportswear.thumbnail_url if p.sportswear.thumbnail_url else "",
                "link": p.sportswear.link if hasattr(p.sportswear, 'link') else ""
            }

        is_liked = False
        if request.user.is_authenticated:
            is_liked = request.user in p.likes.all()

        results.append({
            'id': p.id,
            'author_username': p.author.username,
            'text': p.text,
            'image': p.image.url if p.image else "",
            'like_count': p.like_count,
            'liked_by_user': is_liked,  
            'comment_count': len(comments_list),
            'comments': comments_list,
            'created_at': p.created_at.isoformat(),
            'attachment': attachment_data, 
        })

    return JsonResponse({
        'results': results,
        'next': next_url,
        'previous': None,
    })

def resource_list_json(request):
    resources = Resource.objects.all().order_by('-created_at')
    data = [{
        "id": r.id,
        "title": r.title,
        "thumbnail": r.thumbnail_url,
        "youtube_url": r.youtube_url,
        "level": r.level
    } for r in resources]
    return JsonResponse(data, safe=False)

def sportswear_list_json(request):
    brands = SportswearBrand.objects.all()
    data = [{
        "id": b.id,
        "brand_name": b.brand_name,
        "thumbnail": b.thumbnail_url,
        "link": b.link
    } for b in brands]
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
@require_POST
def create_post_api(request):
    try:
        data = json.loads(request.body)
        text = data.get('text')
        
        post = Post.objects.create(
            author=request.user,
            text=text or ''
        )

        attachment = data.get('attachment')
        if attachment:
            atype = attachment.get('type') or attachment.get('tag')
            aid = attachment.get('id')
            if not aid and 'data' in attachment:
                aid = attachment['data'].get('id')

            if aid:
                if atype == 'Resources':
                    if Resource.objects.filter(id=aid).exists():
                        post.resource_id = aid
                elif atype == 'Sportswear':
                    if SportswearBrand.objects.filter(id=aid).exists():
                        post.sportswear_id = aid
        
        post.save()
        return JsonResponse({"status": "success", "message": "Post created successfully!"})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@login_required
@require_POST
def toggle_like_api(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        message = 'Unliked'
    else:
        post.likes.add(user)
        message = 'Liked'

    return JsonResponse({'status': 'success', 'message': message})

@csrf_exempt
@login_required
@require_POST
def add_comment_api(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    try:
        data = json.loads(request.body)
        content = data.get('content') or data.get('text')

        if not content:
            return JsonResponse({'status': 'error', 'message': 'Comment content cannot be empty'}, status=400)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            text=content
        )
        return JsonResponse({'status': 'success', 'message': 'Comment added'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
@csrf_exempt
@login_required
@require_POST
def edit_comment_api(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        content = data.get('content') or data.get('text')

        if not content:
            return JsonResponse({'status': 'error', 'message': 'Comment content cannot be empty'}, status=400)

        comment.text = content
        comment.save()

        return JsonResponse({'status': 'success', 'message': 'Comment updated successfully'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)


@csrf_exempt
@login_required
@require_POST
def delete_comment_api(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    comment.delete()

    return JsonResponse({'status': 'success', 'message': 'Comment deleted successfully'})