from django.shortcuts import render, redirect
from .models import Event
from .forms import EventForm

def show_events(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'events/show_events.html', {'events': events})

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/add_event.html', {'form': form})