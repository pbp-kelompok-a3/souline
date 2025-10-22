from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from main.models import Studio

class StudioForm(ModelForm):
    class Meta:
        model = Studio
        fields = ['nama_studio', 'thumbnail', 'kota', 'area', 'alamat', 'gmaps_link', 'nomor_telepon']