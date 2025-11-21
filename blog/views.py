from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpResponseRedirect


# LIST VIEW – show published posts on the homepage
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by(
        "-published_date"
    )
    return render(request, "blog/post_list.html", {"posts": posts})


# DETAIL VIEW – show a single post when its title is clicked
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


# Get posts that do NOT have a published_date (drafts only)
@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by("-created_date")
    return render(request, "blog/post_draft_list.html", {"posts": posts})


# NEW POST VIEW – create a new blog post (draft by default)
@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post_draft_list")
    else:
        form = PostForm()
    return render(request, "blog/post_edit.html", {"form": form})


# EDIT POST VIEW – update an existing blog post
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # Handle image removal
            if request.POST.get("remove_image") == "1":
                if post.image:
                    post.image.delete(save=False)
                    post.image = None
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "blog/post_edit.html", {"form": form})


# PUBLISH POST VIEW – publish a blog post
@login_required
@require_POST
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect("post_list")


# DELETE POST VIEW – delete a blog post
@login_required
@require_POST
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # keep published flag before delete for redirect
    was_published = bool(post.published_date)
    post.delete()
    return redirect("post_list" if was_published else "post_draft_list")


# Add a comment to a post
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.approved_comment = False  # New comment requires approval
            comment.save()

            # AJAX: return only the list fragment
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return render(
                    request,
                    "blog/comments_list.html",
                    {"post": post, "user": request.user},
                )

            # Add notification for all users after comment submission
            from django.contrib import messages

            messages.success(
                request, "Your comment was submitted and is awaiting admin approval."
            )

            # Redirect to post detail (no anchor for unauthenticated users)
            url = reverse("post_detail", kwargs={"pk": post.pk})
            if request.user.is_authenticated:
                # Only add anchor if the request is AJAX (moderation convenience)
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    url += "#comments-part"
            return HttpResponseRedirect(url)

        # validation failed – fallback full page (non-AJAX)
        return render(request, "blog/add_comment_to_post.html", {"form": form, "post": post})
    else:
        form = CommentForm()
        return render(request, "blog/add_comment_to_post.html", {"form": form, "post": post})


# Approve a comment (make it visible)
@login_required
@require_POST
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approved_comment = True
    comment.save()
    post = comment.post

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(
            request, "blog/comments_list.html", {"post": post, "user": request.user}
        )

    return redirect("post_detail", pk=post.pk)


# Remove a comment (delete from DB)
@login_required
@require_POST
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    comment.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(
            request, "blog/comments_list.html", {"post": post, "user": request.user}
        )

    return HttpResponseRedirect(reverse("post_detail", args=[post.pk]))


# Add a reply to a comment
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def add_reply_to_comment(request, pk):
    from .models import Comment

    parent_comment = get_object_or_404(Comment, pk=pk)
    if request.method == "POST":
        author = request.POST.get("author")
        text = request.POST.get("text")
        if author and text:
            # Create reply comment
            reply = Comment.objects.create(
                post=parent_comment.post,
                author=author,
                text=text,
                approved_comment=True,
            )
            # Link reply to parent
            reply.parent = parent_comment
            reply.save()
        # AJAX: return updated comments list
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(
                request,
                "blog/comments_list.html",
                {"post": parent_comment.post, "user": request.user},
            )
        return redirect("post_detail", pk=parent_comment.post.pk)
    return redirect("post_detail", pk=parent_comment.post.pk)
