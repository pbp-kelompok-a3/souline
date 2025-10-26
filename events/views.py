from datetime import date, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Event
from .forms import EventForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import serializers

def show_events(request):
    filter_type = request.GET.get('filter')  # 'soon' or 'later'
    today = date.today()
    soon_limit = today + timedelta(days=7)

    if filter_type == 'soon':
        events = Event.objects.filter(date__gte=today, date__lte=soon_limit)
    elif filter_type == 'later':
        events = Event.objects.filter(date__gt=soon_limit)
    else:
        events = Event.objects.filter(date__gte=today)

    return render(request, 'events/show_events.html', {
        'events': events,
        'filter_type': filter_type,
    })

def event_detail(request, id):
    event = get_object_or_404(Event, pk=id)
    return render(request, 'events/event_detail.html', {'event': event})

@login_required(login_url='/login/')
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('events:event_list')
    else:
        form = EventForm()
    return render(request, 'events/add_event.html', {'form': form})


def show_json(request):
    events = Event.objects.all().order_by('date')
    data = [{
        "id": e.id,
        "name": e.name,
        "date": e.date.strftime("%d %B %Y"),
        "description": e.description,
        "poster": e.poster.url if e.poster else "",
    } for e in events]
    return JsonResponse(data, safe=False)


def show_json_filtered(request, filter_type):
    today = timezone.now().date()

    if filter_type == "soon":
        events = Event.objects.filter(date__gte=today, date__lte=today + timedelta(days=7))
    elif filter_type == "later":
        events = Event.objects.filter(date__gt=today + timedelta(days=7))
    else:
        events = Event.objects.all()

    data = [{
        "id": e.id,
        "name": e.name,
        "date": e.date.strftime("%d %B %Y"),
        "description": e.description,
        "poster": e.poster.url if e.poster else "",
    } for e in events]
    return JsonResponse(data, safe=False)

@login_required(login_url='/login/')
def edit_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('events:event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})

@login_required(login_url='/login/')
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.user.is_staff and request.method == 'POST':
        event.delete()
    return redirect('events:event_list')

