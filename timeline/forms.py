from django import forms
from .models import Post, Comment
from resources.models import Resource
from sportswear.models import SportswearBrand

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'image', 'resource', 'sportswear']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': "What's happening?"}),
            'resource': forms.ModelChoiceField(queryset=Resource.objects.all(), empty_label="Select Resource", required=False),
            'sportswear': forms.ModelChoiceField(queryset=SportswearBrand.objects.all(), empty_label="Select Sportswear Brand", required=False),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Write a comment...'}),
        }
