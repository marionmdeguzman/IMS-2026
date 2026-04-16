import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Appointment, Waitlist
from .forms import AppointmentForm, AppointmentStatusForm
from members.views import staff_required
from services.models import Service, StaffMember


def check_conflict(staff, resource, date, start_time, end_time, exclude_id=None):
    """Returns (True, message) if there is a booking conflict, else (False, None)."""
    qs = Appointment.objects.filter(
        date=date,
        status__in=['pending', 'confirmed'],
    ).exclude(pk=exclude_id or 0)

    if staff:
        staff_conflict = qs.filter(
            staff=staff,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()
        if staff_conflict:
            return True, 'That staff member is already booked at this time.'

    if resource:
        resource_conflict = qs.filter(
            resource=resource,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()
        if resource_conflict:
            return True, 'That resource is already booked at this time.'

    return False, None


@staff_required
def appointment_list(request):
    appointments = (
        Appointment.objects
        .select_related('member', 'service', 'staff__user', 'resource')
        .order_by('-date', '-start_time')
    )
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if date_filter:
        appointments = appointments.filter(date=date_filter)

    context = {
        'appointments': appointments[:200],
        'status_filter': status_filter,
        'date_filter': date_filter,
        'page_title': 'Bookings',
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'bookings/appointment_list.html', context)


@staff_required
def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if form.is_valid():
        appt = form.save(commit=False)
        conflict, msg = check_conflict(appt.staff, appt.resource, appt.date, appt.start_time, appt.end_time)
        if conflict:
            form.add_error(None, msg)
        else:
            with transaction.atomic():
                appt.booking_source = 'staff'
                appt.save()
            messages.success(request, 'Appointment created successfully.')
            return redirect('bookings:appointment_detail', pk=appt.pk)
    return render(request, 'bookings/appointment_form.html', {
        'form': form, 'page_title': 'New Appointment', 'action': 'Create Appointment',
    })


@staff_required
def appointment_detail(request, pk):
    appt = get_object_or_404(
        Appointment.objects.select_related('member', 'service', 'staff__user', 'resource'),
        pk=pk,
    )
    status_form = AppointmentStatusForm(instance=appt)
    context = {'appt': appt, 'status_form': status_form, 'page_title': f'Booking #{appt.pk}'}
    return render(request, 'bookings/appointment_detail.html', context)


@staff_required
@require_POST
def appointment_update_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    form = AppointmentStatusForm(request.POST, instance=appt)
    if form.is_valid():
        form.save()
        messages.success(request, f'Status updated to {appt.get_status_display()}.')
    else:
        messages.error(request, 'Could not update status.')
    return redirect('bookings:appointment_detail', pk=pk)


@staff_required
def calendar_view(request):
    return render(request, 'bookings/calendar.html', {'page_title': 'Booking Calendar'})


@staff_required
def calendar_events(request):
    appointments = Appointment.objects.select_related(
        'member', 'service', 'staff__user'
    ).exclude(status='cancelled')
    events = []
    for appt in appointments:
        events.append({
            'id': appt.pk,
            'title': f"{appt.member.get_full_name()} — {appt.service.name}",
            'start': f"{appt.date}T{appt.start_time}",
            'end': f"{appt.date}T{appt.end_time}",
            'color': appt.service.color,
            'url': f"/admin-portal/bookings/{appt.pk}/",
            'extendedProps': {
                'status': appt.status,
                'staff': appt.staff.get_full_name() if appt.staff else 'Unassigned',
            },
        })
    return JsonResponse(events, safe=False)


@staff_required
def get_slots(request):
    """Return available time slots for a given service + date + optional staff."""
    service_id = request.GET.get('service')
    date_str = request.GET.get('date')
    staff_id = request.GET.get('staff')

    if not service_id or not date_str:
        return JsonResponse({'slots': []})

    try:
        service = Service.objects.get(pk=service_id)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (Service.DoesNotExist, ValueError):
        return JsonResponse({'slots': []})

    booked_times = Appointment.objects.filter(
        date=date,
        status__in=['pending', 'confirmed'],
    )
    if staff_id:
        booked_times = booked_times.filter(staff_id=staff_id)

    booked_ranges = [(a.start_time, a.end_time) for a in booked_times]

    slots = []
    current = datetime.combine(date, datetime.strptime('07:00', '%H:%M').time())
    end_of_day = datetime.combine(date, datetime.strptime('20:00', '%H:%M').time())
    duration = timedelta(minutes=service.duration_minutes)

    while current + duration <= end_of_day:
        slot_start = current.time()
        slot_end = (current + duration).time()
        conflict = any(
            not (slot_end <= bs or slot_start >= be)
            for bs, be in booked_ranges
        )
        if not conflict:
            slots.append({
                'start': slot_start.strftime('%H:%M'),
                'end': slot_end.strftime('%H:%M'),
                'label': slot_start.strftime('%I:%M %p'),
            })
        current += timedelta(minutes=30)

    return JsonResponse({'slots': slots})
