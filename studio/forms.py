from django.forms import ModelForm
from studio.models import Studio

class StudioForm(ModelForm):
    class Meta:
        model = Studio
        fields = ['nama_studio', 'thumbnail', 'kota', 'area', 'alamat', 'gmaps_link', 'nomor_telepon']