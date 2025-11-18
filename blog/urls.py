from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path
from . import views


# A view is a place where we put the "logic" of our application.
# 1.Receive the request information as well as parameters parsed from the url.
# 2.Fetch the information from the model, probably adding some logic.
# 3.Create a response by filling a template with the fetched info.


urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/new/", views.post_new, name="post_new"),
    path("post/<int:pk>/edit/", views.post_edit, name="post_edit"),
    # Drafts / publish / delete
    path("drafts/", views.post_draft_list, name="post_draft_list"),
    path("post/<int:pk>/publish/", views.post_publish, name="post_publish"),
    path("post/<int:pk>/remove/", views.post_remove, name="post_remove"),
    # Comments
    path(
        "post/<int:pk>/comment/", views.add_comment_to_post, name="add_comment_to_post"
    ),
    path("comment/<int:pk>/approve/", views.comment_approve, name="comment_approve"),
    path("comment/<int:pk>/remove/", views.comment_remove, name="comment_remove"),
    path(
        "comment/<int:pk>/reply/",
        views.add_reply_to_comment,
        name="add_reply_to_comment",
    ),
]
