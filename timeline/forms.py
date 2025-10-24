from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'image', 'video_url']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': "What's happening?"}),
            'video_url': forms.URLInput(attrs={'placeholder': 'Optional video link'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Write a comment...'}),
        }
