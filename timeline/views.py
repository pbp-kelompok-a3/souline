import json
from django.shortcuts import render 
from django.contrib.auth.decorators import login_required 
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden 
from django.shortcuts import get_object_or_404, render, redirect 
from django.views.decorators.http import require_POST 
from django.core.paginator import Paginator 
from django.template.loader import render_to_string 
from .forms import PostForm, CommentForm 
from .models import Post, Comment, Resource, SportswearBrand
from django.views.decorators.csrf import csrf_exempt

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
        'comment_form': comment_form, } 
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

    from django.template.loader import render_to_string
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
    body = json.loads(request.body.decode('utf-8'))
    content = body.get('content')
    if not content:
        return JsonResponse({'error': 'empty'}, status=400)
    comment = Comment.objects.create(post=post, author=request.user, text=content)
    return JsonResponse({'id': comment.id, 'author_username': comment.author.username, 'content': comment.text}, status=201)
    
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
            # "id": post.id,
            "username": post.author.username,
            "text": post.text,
            "image": post.image.url if post.image else None,
            "created_at": post.created_at.isoformat(),
        })

    return JsonResponse(data, safe=False)

def timeline_json(request):
    page = int(request.GET.get('page', 1))
    posts_qs = Post.objects.select_related('author').all().order_by('-created_at')
    paginator = Paginator(posts_qs, 10)
    page_obj = paginator.get_page(page)

    next_url = None
    if page_obj.has_next():
        next_url = f"?page={page_obj.next_page_number()}"

    results = []
    for p in page_obj.object_list:
        results.append({
        'id': p.id,
        'author_username': p.author.username,
        'text': p.text,
        'image': p.image.url if p.image else None,
        'resource_title': p.resource.title if getattr(p, 'resource', None) else None,
        'resource_thumbnail': p.resource.thumbnail_url if getattr(p, 'resource', None) else None,
        'like_count': p.like_count,
        'liked_by_user': False, # if auth: detect
        'comment_count': p.comments.count(),
    })

    return JsonResponse({
        'results': results,
        'next': next_url,
        'previous': None,
    })

def comments_list(request, pk):
    post = get_object_or_404(Post, pk=pk)
    data = []
    for c in post.comments.select_related('author').all().order_by('-created_at'):
        data.append({
        'id': c.id,
        'author_username': c.author.username,
        'content': c.text,
        'created_at': c.created_at.isoformat(),
    })
    return JsonResponse(data, safe=False)

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
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    text = request.POST.get('text')
    resource_id = request.POST.get('resource_id')
    sportswear_id = request.POST.get('sportswear_id')

    post = Post.objects.create(
        author=request.user,
        text=text or ''
    )

    if resource_id:
        post.resource_id = resource_id

    if sportswear_id:
        post.sportswear_id = sportswear_id

    if 'image' in request.FILES:
        post.image = request.FILES['image']

    post.save()

    return JsonResponse({"success": True, "post_id": post.id})