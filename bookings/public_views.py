import secrets
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone

from .models import Appointment
from .forms import PublicBookingForm
from .views import check_conflict
from members.models import Member
from services.models import Service, StaffMember


def public_booking(request):
    services = Service.objects.filter(is_active=True)
    staff_members = StaffMember.objects.filter(is_available=True).select_related('user')

    # Pre-fill form with logged-in member's details
    initial = {}
    member_prefill = None
    if request.user.is_authenticated and not request.user.is_admin_user:
        try:
            member_prefill = request.user.member_profile
            initial = {
                'first_name': member_prefill.first_name,
                'last_name': member_prefill.last_name,
                'email': member_prefill.email,
                'phone': member_prefill.phone,
            }
        except Exception:
            initial = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }

    form = PublicBookingForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        service = data['service']
        staff = data.get('staff')
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        conflict, msg = check_conflict(staff, None, date, start_time, end_time)
        if conflict:
            form.add_error(None, msg)
        elif date < timezone.now().date():
            form.add_error('date', 'Please select a future date.')
        else:
            with transaction.atomic():
                member, _ = Member.objects.get_or_create(
                    email=data['email'],
                    defaults={
                        'first_name': data['first_name'],
                        'last_name': data['last_name'],
                        'phone': data['phone'],
                    },
                )
                token = secrets.token_hex(32)
                appt = Appointment.objects.create(
                    member=member,
                    service=service,
                    staff=staff,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    status='pending',
                    booking_source='public',
                    public_booking_token=token,
                    notes=data.get('notes', ''),
                )
            return redirect('bookings_public:confirm', token=token)

    context = {
        'form': form,
        'services': services,
        'staff_members': staff_members,
        'prefilled': bool(member_prefill),
    }
    return render(request, 'bookings/public_booking.html', context)


def booking_confirm(request, token):
    appt = get_object_or_404(Appointment, public_booking_token=token)
    return render(request, 'bookings/booking_confirm.html', {'appt': appt})


def public_slots(request):
    """Return available time slots for given service + date + optional staff (public endpoint)."""
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

    if date < timezone.now().date():
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
