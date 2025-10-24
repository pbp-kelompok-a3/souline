from django.db import models

class Resource(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    youtube_url = models.URLField(
        default="https://youtu.be/jRFpuiIhKAQ?si=gQTLj0qkUP63bSE-"
    )
    level = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default='beginner'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate thumbnail otomatis dari link YouTube
        if self.youtube_url and not self.thumbnail_url:
            video_id = None

            if "embed/" in self.youtube_url:
                video_id = self.youtube_url.split("embed/")[1].split("?")[0]
            elif "v=" in self.youtube_url:
                video_id = self.youtube_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in self.youtube_url:
                video_id = self.youtube_url.split("youtu.be/")[1].split("?")[0]

            if video_id:
                self.thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title