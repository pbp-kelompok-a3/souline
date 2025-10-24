from django import forms
from .models import SportswearBrand

TAILWIND_INPUT_CLASS = 'w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-400'

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