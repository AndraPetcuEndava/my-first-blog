from django.conf import settings
from django.db import models
from django.utils import timezone
import re


# ------------------------------
# BLOG POST MODEL
# ------------------------------
class Post(models.Model):
    # Relationship: every Post has one author (a User)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Post content fields
    title = models.CharField(max_length=200)
    from ckeditor_uploader.fields import RichTextUploadingField
    text = RichTextUploadingField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    # Timestamps
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        """Mark post as published by setting the published_date to now."""
        self.published_date = timezone.now()
        self.save()

    def preview_html(self, word_limit=20):
        from django.utils.html import strip_tags
        from django.utils.safestring import mark_safe
        import re

        # Remove HTML tags for word count, but return HTML for display
        text = self.text
        # Strip leading/trailing whitespace and blank lines
        text_stripped = re.sub(r"^(\s|&nbsp;)+", "", strip_tags(text))
        words = text_stripped.split()
        if len(words) > word_limit:
            truncated = " ".join(words[:word_limit]) + "..."
            return mark_safe(truncated)
        return mark_safe(text_stripped)

    def __str__(self):
        """Readable representation in admin or shell."""
        return self.title

    def approved_comments_count(self):
        return self.comments.filter(approved_comment=True).count()


# ------------------------------
# COMMENT MODEL
# ------------------------------


class Comment(models.Model):
    # Each comment belongs to a specific Post
    post = models.ForeignKey(
        "blog.Post", on_delete=models.CASCADE, related_name="comments"
    )

    # Replies: parent comment (null for top-level)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )

    # Basic comment info
    author = models.CharField(max_length=200)
    text = models.TextField()

    # Timestamp for when the comment was created
    created_date = models.DateTimeField(default=timezone.now)

    # Whether the comment has been approved by the blog author
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        """Readable representation: shows part of the comment text."""
        return self.text[:50]

    class Meta:
        ordering = ["-created_date"]  # newest first

