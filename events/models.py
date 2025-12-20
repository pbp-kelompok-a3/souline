from django.conf import settings 
from django.db import models
from studio.models import Studio

class Event(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    date = models.DateField()
    poster = models.ImageField(upload_to='event_posters/', blank=True, null=True)
    location = models.ForeignKey(
        Studio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_events'
    )

    def __str__(self):
        return self.name
