from django import forms
from .models import Post, Comment
from django.contrib.auth.forms import SetPasswordForm

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


# ------------------------------
# CUSTOM PASSWORD RESET FORM
# ------------------------------


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password2"].help_text = ""
