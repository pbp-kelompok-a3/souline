from datetime import date, timedelta
import json
from django.utils import timezone
from django.http import (HttpResponseBadRequest,HttpResponseForbidden,HttpResponseNotAllowed,JsonResponse,)
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Event
from .forms import EventForm


def show_events(request):
    filter_type = request.GET.get("filter")  # 'soon' or 'later'
    today = date.today()
    soon_limit = today + timedelta(days=7)

    if filter_type == "soon":
        events = Event.objects.filter(date__gte=today, date__lte=soon_limit)
    elif filter_type == "later":
        events = Event.objects.filter(date__gt=soon_limit)
    else:
        events = Event.objects.filter(date__gte=today)

    return render(
        request,
        "events/show_events.html",
        {"events": events, "filter_type": filter_type},
    )


def event_detail(request, id):
    event = get_object_or_404(Event, pk=id)
    return render(request, "events/event_detail.html", {"event": event})


@login_required(login_url="/login/")
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.owner = request.user
            event.save()
            return redirect("events:event_list")
    else:
        form = EventForm()
    return render(request, "events/add_event.html", {"form": form})


def _absolute_poster_url(request, event):
    if getattr(event, "poster", None):
        try:
            return request.build_absolute_uri(event.poster.url)
        except Exception:
            return ""
    return ""


def show_json(request):
    #JSON 
    events = Event.objects.all().order_by("date")
    data = []
    for e in events:
        data.append(
            {
                "id": e.id,
                "name": e.name,
                "date": e.date.isoformat(),
                "description": e.description,
                "poster": _absolute_poster_url(request, e),
                "location": e.location or "",
                "owner": e.owner.username if getattr(e, "owner", None) else "",
            }
        )
    return JsonResponse(data, safe=False)


def show_json_filtered(request, filter_type):
    today = timezone.now().date()

    if filter_type == "soon":
        events = Event.objects.filter(
            date__gte=today, date__lte=today + timedelta(days=7)
        ).order_by("date")
    elif filter_type == "later":
        events = Event.objects.filter(date__gt=today + timedelta(days=7)).order_by(
            "date"
        )
    else:
        events = Event.objects.all().order_by("date")

    data = []
    for e in events:
        data.append(
            {
                "id": e.id,
                "name": e.name,
                "date": e.date.isoformat(),
                "description": e.description,
                "poster": _absolute_poster_url(request, e),
                "location": e.location or "",
                "owner": e.owner.username if getattr(e, "owner", None) else "",
            }
        )
    return JsonResponse(data, safe=False)


@login_required(login_url="/login/")
def edit_event(request, id):
    event = get_object_or_404(Event, id=id)

    # permission check
    if not (request.user.is_staff or (event.owner and event.owner == request.user)):
        return HttpResponseForbidden("You don't have permission to edit this event.")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect("events:event_list")
    else:
        form = EventForm(instance=event)
    return render(request, "events/edit_event.html", {"form": form, "event": event})


@login_required(login_url="/login/")
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not (request.user.is_staff or (event.owner and event.owner == request.user)):
        return HttpResponseForbidden("You don't have permission to delete this event.")

    event.delete()
    return redirect("events:event_list")