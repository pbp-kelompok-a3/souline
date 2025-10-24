from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import UserProfile
from django.forms import ModelForm
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kota'] = UserProfile._meta.get_field('kota').formfield()
        
        # override def
        self.fields['username'].help_text = 'Required. 20 characters or fewer. Letters and numbers only.'
        self.fields['username'].max_length = 20
        self.fields['username'].validators = []  # clear validators DO NOT REMOVE FOR THE LOVE OF GOD
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter username (letters and numbers only)',
            'maxlength': '20'  # HTML validation
        })
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalnum():
            raise ValidationError("Username must contain only letters and numbers.")
        if len(username) > 20:
            raise ValidationError("Username must be 20 characters or less.")
            
        # Check if username is already taken
        if User.objects.filter(username=username).exists() and not self.instance.pk:
            raise ValidationError("This username is already taken.")
            
        return username

class UserProfileModelForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['kota']
