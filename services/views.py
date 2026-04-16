from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Service, StaffMember, Resource
from .forms import ServiceForm, StaffMemberForm, ResourceForm
from members.views import staff_required


@staff_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'services/service_list.html', {'services': services, 'page_title': 'Services'})


@staff_required
def service_create(request):
    form = ServiceForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Service created.')
        return redirect('services:service_list')
    return render(request, 'services/service_form.html', {'form': form, 'page_title': 'New Service', 'action': 'Create'})


@staff_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, instance=service)
    if form.is_valid():
        form.save()
        messages.success(request, 'Service updated.')
        return redirect('services:service_list')
    return render(request, 'services/service_form.html', {
        'form': form, 'service': service,
        'page_title': f'Edit — {service.name}', 'action': 'Save Changes',
    })


@staff_required
def staff_list(request):
    staff = StaffMember.objects.select_related('user').prefetch_related('services')
    return render(request, 'services/staff_list.html', {'staff': staff, 'page_title': 'Staff Members'})


@staff_required
def staff_detail(request, pk):
    staff_member = get_object_or_404(StaffMember, pk=pk)
    form = StaffMemberForm(request.POST or None, instance=staff_member)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Staff profile updated.')
        return redirect('services:staff_list')
    return render(request, 'services/staff_detail.html', {
        'staff_member': staff_member, 'form': form, 'page_title': staff_member.get_full_name(),
    })
