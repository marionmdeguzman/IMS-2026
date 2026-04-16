from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Payment
from .forms import PaymentForm, MembershipPlanForm
from members.models import MembershipPlan, MemberMembership
from members.views import staff_required


@staff_required
def payment_list(request):
    payments = Payment.objects.select_related('member', 'appointment__service', 'recorded_by').order_by('-paid_at')
    method_filter = request.GET.get('method', '')
    status_filter = request.GET.get('status', '')
    if method_filter:
        payments = payments.filter(method=method_filter)
    if status_filter:
        payments = payments.filter(status=status_filter)

    total = payments.filter(status='paid').aggregate(t=Sum('amount'))['t'] or 0

    context = {
        'payments': payments[:200],
        'total': total,
        'method_filter': method_filter,
        'status_filter': status_filter,
        'method_choices': Payment.METHOD_CHOICES,
        'status_choices': Payment.STATUS_CHOICES,
        'page_title': 'Payments',
    }
    return render(request, 'billing/payment_list.html', context)


@staff_required
def payment_create(request):
    form = PaymentForm(request.POST or None)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.recorded_by = request.user
        payment.save()
        messages.success(request, f'Payment of ₱{payment.amount} recorded successfully.')
        return redirect('billing:payment_list')
    return render(request, 'billing/payment_form.html', {
        'form': form, 'page_title': 'Log Payment', 'action': 'Record Payment',
    })


@staff_required
def membership_list(request):
    memberships = MemberMembership.objects.select_related('member', 'plan').order_by('-start_date')
    status_filter = request.GET.get('status', '')
    if status_filter:
        memberships = memberships.filter(status=status_filter)

    context = {
        'memberships': memberships[:200],
        'status_filter': status_filter,
        'page_title': 'Memberships',
    }
    return render(request, 'billing/membership_list.html', context)


@staff_required
def plan_list(request):
    plans = MembershipPlan.objects.all()
    return render(request, 'billing/plan_list.html', {'plans': plans, 'page_title': 'Membership Plans'})


@staff_required
def plan_create(request):
    form = MembershipPlanForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Plan created.')
        return redirect('billing:plan_list')
    return render(request, 'billing/plan_form.html', {'form': form, 'page_title': 'New Plan', 'action': 'Create'})


@staff_required
def plan_edit(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    form = MembershipPlanForm(request.POST or None, instance=plan)
    if form.is_valid():
        form.save()
        messages.success(request, 'Plan updated.')
        return redirect('billing:plan_list')
    return render(request, 'billing/plan_form.html', {
        'form': form, 'plan': plan,
        'page_title': f'Edit Plan — {plan.name}', 'action': 'Save Changes',
    })


@staff_required
def revenue_report(request):
    today = timezone.now().date()
    this_month = today.replace(day=1)
    payments = Payment.objects.filter(status='paid', paid_at__date__gte=this_month)
    by_method = (
        payments.values('method')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    monthly_total = payments.aggregate(t=Sum('amount'))['t'] or 0

    context = {
        'by_method': by_method,
        'monthly_total': monthly_total,
        'this_month': this_month,
        'page_title': 'Revenue Report',
    }
    return render(request, 'billing/revenue_report.html', context)
