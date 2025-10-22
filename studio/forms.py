from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from main.models import UserProfile, Studio

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kota'] = UserProfile._meta.get_field('kota').formfield()

class StudioForm(ModelForm):
    class Meta:
        model = Studio
        fields = ['nama_studio', 'thumbnail', 'kota', 'area', 'alamat', 'gmaps_link', 'nomor_telepon']