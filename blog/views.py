from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpResponseRedirect

# AJAX endpoints for liking/disliking comments
from django.views.decorators.http import require_POST
from django.http import JsonResponse


# LIST VIEW – show published posts on the homepage
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by(
        "-published_date"
    )
    return render(request, "blog/post_list.html", {"posts": posts})


# DETAIL VIEW – show a single post when its title is clicked
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if not request.user.is_authenticated:
        post.increment_views()
    return render(request, "blog/post_detail.html", {"post": post})


# DRAFT LIST VIEW – show all posts that are drafts (not published)
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
            if "publish_immediately" in request.POST:
                post.published_date = timezone.now()
                post.save()
                return redirect("post_list")
            else:
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
            # Handle image removal if requested
            if request.POST.get("remove_image") == "1":
                if post.image:
                    post.image.delete(save=False)
                    post.image = None
            post.save()
            # Redirect based on whether post is published or still a draft
            if post.published_date:
                return redirect("post_detail", pk=post.pk)
            else:
                return redirect("post_draft_list")
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
    was_published = bool(post.published_date)
    post.delete()
    return redirect("post_list" if was_published else "post_draft_list")


# ADD COMMENT VIEW – add a comment to a post
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.approved_comment = False  # New comment requires admin approval
            comment.save()

            # AJAX: If AJAX request, return only the comments list fragment
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

            # Redirect to post detail
            url = reverse("post_detail", kwargs={"pk": post.pk})
            if request.user.is_authenticated:
                # If the user is authenticated and it was an AJAX request,
                # add an anchor so it scrolls to the comments section on reload
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    url += "#comments-part"
            # Redirect back to the post detail page (with or without anchor)
            return HttpResponseRedirect(url)

        return render(
            request, "blog/add_comment_to_post.html", {"form": form, "post": post}
        )
    # If the request is not POST (GET), render an empty form for the user to fill
    else:
        form = CommentForm()
        return render(
            request, "blog/add_comment_to_post.html", {"form": form, "post": post}
        )


# APPROVE COMMENT VIEW – admin approves a comment
@login_required
@require_POST
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approved_comment = True
    comment.save()
    post = comment.post
    # AJAX: update comments section instantly
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(
            request,
            "blog/comments_list.html",
            {"post": post, "user": request.user},
        )
    return redirect("post_detail", pk=post.pk)


# LIKE COMMENT VIEW
@require_POST
def comment_like(request, pk):
    from .models import Comment, CommentReaction

    comment = get_object_or_404(Comment, pk=pk)
    if request.user.is_authenticated:
        user = request.user
        reaction, created = CommentReaction.objects.get_or_create(
            user=user, comment=comment
        )
        if not created:
            if reaction.reaction == "like":
                result = JsonResponse(
                    {"likes": comment.likes, "dislikes": comment.dislikes}
                )
            elif reaction.reaction == "dislike":
                comment.dislikes = max(comment.dislikes - 1, 0)
                reaction.reaction = "like"
                comment.likes += 1
                reaction.save()
                comment.save(update_fields=["likes", "dislikes"])
                result = JsonResponse(
                    {"likes": comment.likes, "dislikes": comment.dislikes}
                )
        else:
            reaction.reaction = "like"
            reaction.save()
            comment.likes += 1
            comment.save(update_fields=["likes"])
            result = JsonResponse(
                {"likes": comment.likes, "dislikes": comment.dislikes}
            )
    else:
        # Unauthenticated: use session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        # Store reaction in session
        key = f"comment_{comment.pk}_reaction"
        prev_reaction = request.session.get(key)
        if prev_reaction == "like":
            result = JsonResponse(
                {"likes": comment.likes, "dislikes": comment.dislikes}
            )
        elif prev_reaction == "dislike":
            comment.dislikes = max(comment.dislikes - 1, 0)
            comment.likes += 1
            request.session[key] = "like"
            comment.save(update_fields=["likes", "dislikes"])
            result = JsonResponse(
                {"likes": comment.likes, "dislikes": comment.dislikes}
            )
        else:
            comment.likes += 1
            request.session[key] = "like"
            comment.save(update_fields=["likes"])
            result = JsonResponse(
                {"likes": comment.likes, "dislikes": comment.dislikes}
            )

    # AJAX: allows the website to update the comments section without refreshing the entire page
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(
            request,
            "blog/comments_list.html",
            {"post": comment.post, "user": request.user},
        )

    return redirect("post_detail", pk=comment.post.pk)


# DISLIKE COMMENT VIEW
@require_POST
def comment_dislike(request, pk):
    from .models import Comment, CommentReaction

    comment = get_object_or_404(Comment, pk=pk)
    if request.user.is_authenticated:
        user = request.user
        reaction, created = CommentReaction.objects.get_or_create(
            user=user, comment=comment
        )
        if not created:
            if reaction.reaction == "dislike":
                return JsonResponse(
                    {"likes": comment.likes, "dislikes": comment.dislikes}
                )
            elif reaction.reaction == "like":
                comment.likes = max(comment.likes - 1, 0)
                reaction.reaction = "dislike"
                comment.dislikes += 1
                reaction.save()
                comment.save(update_fields=["likes", "dislikes"])
                return JsonResponse(
                    {"likes": comment.likes, "dislikes": comment.dislikes}
                )
        else:
            reaction.reaction = "dislike"
            reaction.save()
            comment.dislikes += 1
            comment.save(update_fields=["dislikes"])
            return JsonResponse({"likes": comment.likes, "dislikes": comment.dislikes})
    else:
        # Unauthenticated: use session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        key = f"comment_{comment.pk}_reaction"
        prev_reaction = request.session.get(key)
        if prev_reaction == "dislike":
            return JsonResponse({"likes": comment.likes, "dislikes": comment.dislikes})
        elif prev_reaction == "like":
            comment.likes = max(comment.likes - 1, 0)
            comment.dislikes += 1
            request.session[key] = "dislike"
            comment.save(update_fields=["likes", "dislikes"])
            return JsonResponse({"likes": comment.likes, "dislikes": comment.dislikes})
        else:
            comment.dislikes += 1
            request.session[key] = "dislike"
            comment.save(update_fields=["dislikes"])
            return JsonResponse({"likes": comment.likes, "dislikes": comment.dislikes})

    # AJAX: allows the website to update the comments section without refreshing the entire page
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(
            request,
            "blog/comments_list.html",
            {"post": comment.post, "user": request.user},
        )

    return redirect("post_detail", pk=comment.post.pk)


# REMOVE COMMENT VIEW – delete a comment from a post
@login_required
@require_POST
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    comment.delete()

    # AJAX: allows the website to update the comments section without refreshing the entire page
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(
            request, "blog/comments_list.html", {"post": post, "user": request.user}
        )

    return HttpResponseRedirect(reverse("post_detail", args=[post.pk]))


# ADD REPLY TO COMMENT VIEW – add a reply to a comment (AJAX or POST)
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse


@csrf_protect
def add_reply_to_comment(request, pk):
    from .models import Comment

    parent_comment = get_object_or_404(Comment, pk=pk)
    if request.method == "POST":
        text = request.POST.get("text")
        # If admin is replying, set author to 'admin'
        if request.user.is_authenticated:
            author = "admin"
        else:
            author = request.POST.get("author")
        if author and text:
            # Approve reply automatically if admin, else require approval
            is_approved = (
                request.user.is_authenticated if hasattr(request, "user") else False
            )
            reply = Comment.objects.create(
                post=parent_comment.post,
                author=author,
                text=text,
                approved_comment=is_approved,
            )
            reply.parent = parent_comment
            reply.save()
        # AJAX: If AJAX request, return updated comments list
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(
                request,
                "blog/comments_list.html",
                {"post": parent_comment.post, "user": request.user},
            )
        # Fallback: redirect to post detail
        return redirect("post_detail", pk=parent_comment.post.pk)
    # Fallback: redirect to post detail if not POST
    return redirect("post_detail", pk=parent_comment.post.pk)
