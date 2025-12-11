from django import forms
from .models import Post, Comment

# ------------------------------
# FORM FOR BLOG POSTS
# ------------------------------


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ("title", "text", "image")


# ------------------------------
# FORM FOR COMMENTS
# ------------------------------


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            "author",
            "text",
        )
