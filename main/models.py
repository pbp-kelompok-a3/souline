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

# Model user belum kelar, lanjutin dari ini bagi yang pegang modul auth
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    kota = models.CharField(max_length=20, choices=KOTA_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Studio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_studio = models.CharField(max_length=100)
    thumbnail = models.URLField(blank=True, null=True)
    kota = models.CharField(max_length=20, choices=KOTA_CHOICES)
    area = models.CharField(max_length=100)
    alamat = models.TextField()
    gmaps_link = models.URLField(blank=True, null=True)
    nomor_telepon = models.CharField(max_length=15)

    def __str__(self):
        return self.nama_studio