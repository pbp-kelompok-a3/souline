from django import forms
from .models import Event
from studio.models import Studio

class EventForm(forms.ModelForm):
    location = forms.ModelChoiceField(
        queryset=Studio.objects.none(),  # set in __init__
        empty_label="Select Location",
        widget=forms.Select(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Studio.objects.all()
        if self.instance and self.instance.location:
            self.fields['location'].initial = self.instance.location

    class Meta:
        model = Event
        fields = ['poster', 'name', 'date', 'description', 'location']

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
            'poster': forms.URLInput(attrs={
                'placeholder': 'Input your URL poster here',
                'class': 'w-full rounded-md border border-gray-300 px-3 py-2 mt-1 text-gray-700 focus:ring-2 focus:ring-[#F48C06] focus:outline-none'
            }),
        }
