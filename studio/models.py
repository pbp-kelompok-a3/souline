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