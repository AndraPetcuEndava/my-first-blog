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
    text = models.TextField()

    # Timestamps
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        """Mark post as published by setting the published_date to now."""
        self.published_date = timezone.now()
        self.save()

    def preview_sentence(self, count=3):
        # Split text into sentences ending with a dot
        sentences = re.findall(r'[^.]*\.', self.text)
        preview = ''.join(sentences[:count]).strip()
        if preview:
            return preview
        return self.text[:300]  # fallback

    def __str__(self):
        """Readable representation in admin or shell."""
        return self.title
    

# ------------------------------
# COMMENT MODEL
# ------------------------------
class Comment(models.Model):
    # Each comment belongs to a specific Post
    # 'related_name' allows us to access all comments of a post via post.comments
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')

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
    
def approved_comments(self):
    return self.comments.filter(approved_comment=True)