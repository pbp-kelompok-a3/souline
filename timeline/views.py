from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from .forms import PostForm, CommentForm
from .models import Post, Comment


def timeline_list(request):
    """
    Show timeline. Accept normal GET. New posts are created via AJAX POST to create_post.
    """
    posts_qs = Post.objects.select_related('author').prefetch_related('likes', 'comments__author').all()
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
        # return JSON errors for AJAX
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    # prepare minimal HTML for the newly created post (render partial)
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
    form = CommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
    from django.template.loader import render_to_string
    html = render_to_string('_comment.html', {'comment': comment}, request=request)
    return JsonResponse({'success': True, 'html': html})
    
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