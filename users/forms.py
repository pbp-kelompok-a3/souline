from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kota'] = UserProfile._meta.get_field('kota').formfield()
