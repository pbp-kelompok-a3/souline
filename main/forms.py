from django.forms import ModelForm
from main.models import UserProfile, Studio

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['kota']

class StudioForm(ModelForm):
    class Meta:
        model = Studio
        fields = ['nama_studio', 'thumbnail', 'kota', 'area', 'alamat', 'gmaps_link', 'nomor_telepon']