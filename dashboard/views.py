from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count

from members.views import staff_required
from members.models import Member, MemberMembership
from bookings.models import Appointment
from billing.models import Payment


def get_dashboard_stats():
    today = timezone.now().date()
    this_month_start = today.replace(day=1)

    todays_appointments = (
        Appointment.objects
        .filter(date=today)
        .exclude(status='cancelled')
        .count()
    )
    active_members = Member.objects.filter(status='active').count()
    revenue_this_month = (
        Payment.objects
        .filter(paid_at__date__gte=this_month_start, status='paid')
        .aggregate(total=Sum('amount'))['total'] or 0
    )
    expiring_memberships = MemberMembership.objects.filter(
        end_date__range=[today, today + timedelta(days=7)],
        status='active',
    ).count()
    no_shows_this_month = Appointment.objects.filter(
        date__gte=this_month_start,
        status='no_show',
    ).count()

    return {
        'todays_appointments': todays_appointments,
        'active_members': active_members,
        'revenue_this_month': revenue_this_month,
        'expiring_memberships': expiring_memberships,
        'no_shows_this_month': no_shows_this_month,
    }


@staff_required
def overview(request):
    stats = get_dashboard_stats()
    today = timezone.now().date()

    todays_appts = (
        Appointment.objects
        .filter(date=today)
        .select_related('member', 'service', 'staff__user')
        .exclude(status='cancelled')
        .order_by('start_time')
    )
    expiring = (
        MemberMembership.objects
        .filter(
            end_date__range=[today, today + timedelta(days=7)],
            status='active',
        )
        .select_related('member', 'plan')
        .order_by('end_date')
    )
    recent_payments = (
        Payment.objects
        .select_related('member')
        .filter(status='paid')
        .order_by('-paid_at')[:8]
    )

    context = {
        **stats,
        'todays_appts': todays_appts,
        'expiring': expiring,
        'recent_payments': recent_payments,
        'today': today,
        'page_title': 'Dashboard',
    }
    return render(request, 'dashboard/overview.html', context)


@staff_required
def no_show_report(request):
    today = timezone.now().date()
    this_month_start = today.replace(day=1)

    no_shows = (
        Appointment.objects
        .filter(status='no_show', date__gte=this_month_start)
        .select_related('member', 'service', 'staff__user')
        .order_by('-date')
    )
    total = no_shows.count()

    context = {
        'no_shows': no_shows,
        'total': total,
        'this_month_start': this_month_start,
        'page_title': 'No-Show Report',
    }
    return render(request, 'dashboard/no_show_report.html', context)
