from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .forms import StaffLoginForm, ClientLoginForm, ClientRegisterForm


def client_login(request):
    if request.user.is_authenticated:
        if request.user.is_admin_user:
            return redirect('dashboard:overview')
        return redirect('accounts:client_profile')
    form = ClientLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        login(request, user)
        if user.is_admin_user:
            return redirect(request.GET.get('next', '/admin-portal/dashboard/'))
        return redirect('accounts:client_profile')
    return render(request, 'accounts/login.html', {'form': form})


def client_register(request):
    if request.user.is_authenticated:
        if request.user.is_admin_user:
            return redirect('dashboard:overview')
        return redirect('accounts:client_profile')
    form = ClientRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
        return redirect('accounts:client_profile')
    return render(request, 'accounts/register.html', {'form': form})


@login_required(login_url='/login/')
def client_profile(request):
    user = request.user
    if user.is_admin_user:
        return redirect('dashboard:overview')
    try:
        member = user.member_profile
    except Exception:
        member = None
    today = timezone.now().date()
    upcoming = []
    past = []
    if member:
        upcoming = member.appointments.filter(
            date__gte=today, status__in=['pending', 'confirmed']
        ).select_related('service', 'staff__user').order_by('date', 'start_time')[:5]
        past = member.appointments.filter(
            status__in=['completed', 'cancelled', 'no_show']
        ).select_related('service', 'staff__user').order_by('-date', '-start_time')[:5]
    return render(request, 'accounts/profile.html', {
        'member': member,
        'upcoming': upcoming,
        'past': past,
        'today': today,
    })


def staff_login(request):
    if request.user.is_authenticated and request.user.is_admin_user:
        return redirect('dashboard:overview')
    form = StaffLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.cleaned_data['user'])
        next_url = request.GET.get('next', '/admin-portal/dashboard/')
        return redirect(next_url)
    return render(request, 'accounts/staff_login.html', {'form': form})


@require_POST
def staff_logout(request):
    was_admin = request.user.is_authenticated and request.user.is_admin_user
    logout(request)
    if was_admin:
        return redirect('accounts:staff_login')
    return redirect('accounts:login')
