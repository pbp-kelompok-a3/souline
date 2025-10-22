from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['poster', 'name', 'date', 'description']

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter event name',
                'class': 'w-full rounded-md border border-gray-300 px-3 py-2 mt-1 text-gray-700 focus:ring-2 focus:ring-[#F48C06] focus:outline-none'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full rounded-md border border-gray-300 px-3 py-2 mt-1 text-gray-700 focus:ring-2 focus:ring-[#F48C06] focus:outline-none'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Write a short description about the event...',
                'class': 'w-full rounded-md border border-gray-300 px-3 py-2 mt-1 text-gray-700 focus:ring-2 focus:ring-[#F48C06] focus:outline-none',
                'rows': 4
            }),
            'poster': forms.ClearableFileInput(attrs={
                'class': 'hidden',  # biar ngikut style upload kotak plus tadi
                'accept': 'image/*'
            }),
        }
