from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    date = models.DateField()
    poster = models.ImageField(upload_to='event_posters/', blank=True, null=True)
    

    def __str__(self):
        return self.name
