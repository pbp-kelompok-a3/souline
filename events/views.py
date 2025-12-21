from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
import json
from django.utils import timezone
from django.http import (HttpResponseBadRequest,HttpResponseForbidden,HttpResponseNotAllowed,JsonResponse,)
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Event
from .forms import EventForm
from studio.models import Studio


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

def events_json(request):
    """
    GET params:
      - filter: '', 'soon', 'later'
      - kota: optional, e.g. 'Jakarta'
      - ref_date: optional, YYYY-MM-DD (user-selected date)
    """
    filter_type = request.GET.get('filter', '').strip()
    kota = request.GET.get('kota', '').strip()
    ref_date_str = request.GET.get('ref_date', '').strip()

    # parse date
    try:
        ref_date = date.fromisoformat(ref_date_str) if ref_date_str else timezone.now().date()
    except Exception:
        ref_date = timezone.now().date()

    soon_limit = ref_date + timedelta(days=7)

    qs = Event.objects.select_related('location').all().order_by('date')

    # filter berdasarkan tanggal
    if filter_type == 'soon':
        qs = qs.filter(date__gte=ref_date, date__lte=soon_limit)
    elif filter_type == 'later':
        qs = qs.filter(date__gt=soon_limit)
    else:
        qs = qs.filter(date__gte=ref_date)

    # filter berdasarkan kota
    if kota:
        qs = qs.filter(location__kota__iexact=kota)

    # serialize data ke JSON
    data = []
    for e in qs:
        data.append({
            "id": str(e.id),
            "name": e.name,
            "date": e.date.isoformat(),
            "description": e.description,
            "poster": request.build_absolute_uri(e.poster.url) if e.poster else "",
            "location": e.location.nama_studio if e.location else "",
            "location_id": str(e.location.id) if e.location else "",
            "location_kota": e.location.kota if e.location else "",
            "owner": e.owner.username if e.owner else "",
        })

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

@csrf_exempt
def add_event_api(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    form = EventForm(request.POST, request.FILES)
    if form.is_valid():
        event = form.save()
        return JsonResponse({"id": event.id, "status": "success"})
    return JsonResponse({"status": "failed", "errors": form.errors}, status=400)

@csrf_exempt
def edit_event_api(request, id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return JsonResponse({"status": "failed", "error": "Not found"}, status=404)
    form = EventForm(request.POST, request.FILES, instance=event)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed", "errors": form.errors}, status=400)

@csrf_exempt
def delete_event_api(request, id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    try:
        event = Event.objects.get(id=id)
        event.delete()
        return JsonResponse({"status": "success"})
    except Event.DoesNotExist:
        return JsonResponse({"status": "failed", "error": "Not found"}, status=404)