from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path
from . import views


# URL patterns for the blog app
# Each path maps a URL to a view function in views.py
# - The name argument allows reverse URL resolution in templates and redirects


urlpatterns = [
    # Home page: list all published posts
    path("", views.post_list, name="post_list"),

    # Post detail and CRUD
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/new/", views.post_new, name="post_new"),
    path("post/<int:pk>/edit/", views.post_edit, name="post_edit"),

    # Drafts, publish, and delete
    path("drafts/", views.post_draft_list, name="post_draft_list"),
    path("post/<int:pk>/publish/", views.post_publish, name="post_publish"),
    path("post/<int:pk>/remove/", views.post_remove, name="post_remove"),

    # Comments: add, approve, remove, reply
    path(
        "post/<int:pk>/comment/", views.add_comment_to_post, name="add_comment_to_post"
    ),
    path("comment/<int:pk>/approve/", views.comment_approve, name="comment_approve"),
    path("comment/<int:pk>/remove/", views.comment_remove, name="comment_remove"),
    
    # Add a reply to an existing comment (AJAX or normal POST)
    path(
        "comment/<int:pk>/reply/",
        views.add_reply_to_comment,
        name="add_reply_to_comment",
    ),
]
