from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.

KOTA_CHOICES = [
    ('Jakarta', 'Jakarta'),
    ('Bogor', 'Bogor'),
    ('Depok', 'Depok'),
    ('Tangerang', 'Tangerang'),
    ('Bekasi', 'Bekasi'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    kota = models.CharField(max_length=20, choices=KOTA_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return self.user.username