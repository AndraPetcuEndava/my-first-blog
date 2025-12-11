from django.db import models
from django.conf import settings
from django.utils import timezone
import re

# ==============================
# COMMENT REACTION MODEL
# ==============================


class CommentReaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(
        "Comment", on_delete=models.CASCADE, related_name="reactions"
    )
    reaction = models.CharField(
        max_length=7, choices=(("like", "Like"), ("dislike", "Dislike"))
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")


# ==============================
# BLOG POST MODEL
# ==============================


class Post(models.Model):
    # ForeignKey to User: each post has one author
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Main content fields
    title = models.CharField(max_length=200)  # Post title
    from ckeditor_uploader.fields import RichTextUploadingField

    text = (
        RichTextUploadingField()
    )  # Rich text content (with CKEditor: images, formatting, etc.)
    image = models.ImageField(
        upload_to="post_images/", blank=True, null=True
    )  # Optional image

    # Timestamps
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    # View counter
    views = models.PositiveIntegerField(default=0)

    def publish(self):
        # Mark post as published by setting the published_date to now.
        self.published_date = timezone.now()
        self.save()

    def increment_views(self):
        self.views += 1
        self.save(update_fields=["views"])

    def preview_html(self, word_limit=20):
        # Create a short preview version of the post text for displaying in post cards
        from django.utils.html import strip_tags
        from django.utils.safestring import mark_safe
        import re

        text = self.text
        # Remove HTML tags and unnecessary spaces or blank lines
        text_stripped = re.sub(r"^(\s|&nbsp;)+", "", strip_tags(text))
        words = text_stripped.split()
        if len(words) > word_limit:
            truncated = " ".join(words[:word_limit]) + "..."
            return mark_safe(truncated)
        return mark_safe(text_stripped)

    def __str__(self):
        # String representation for admin/shell: show the post title.
        return self.title

    def approved_comments_count(self):
        # Return the number of approved comments for this post.
        return self.comments.filter(approved_comment=True).count()


# ==============================
# COMMENT MODEL
# ==============================


class Comment(models.Model):
    # ForeignKey to Post: each comment belongs to a post
    post = models.ForeignKey(
        "blog.Post", on_delete=models.CASCADE, related_name="comments"
    )

    # Replies
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )

    # Comment content
    author = models.CharField(max_length=200)
    text = models.TextField()

    # Timestamp for when the comment was created
    created_date = models.DateTimeField(default=timezone.now)

    # Whether the comment has been approved by the blog author
    approved_comment = models.BooleanField(default=False)

    # Like/dislike counters
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def approve(self):
        # Mark this comment as approved.
        self.approved_comment = True
        self.save()

    def __str__(self):
        # String representation: show the first 50 chars of the comment text.
        return self.text[:50]

    class Meta:
        # Order comments by newest first
        ordering = ["-created_date"]
