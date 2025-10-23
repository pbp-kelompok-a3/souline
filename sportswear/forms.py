from django import forms
from .models import SportswearBrand

class SportswearBrandForm(forms.ModelForm):
    class Meta:
        model = SportswearBrand
        fields = [
            'brand_name', 
            'description', 
            'link', 
            'thumbnail_url'
        ]
        
        widgets = {
            'brand_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'thumbnail_url': forms.URLInput(attrs={'class': 'form-control'}),
        }