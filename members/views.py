from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Member, Tag, MemberMembership, MembershipPlan
from .forms import MemberForm, MemberMembershipForm, CSVImportForm
from accounts.models import User


def staff_required(view_func):
    """Decorator: requires authenticated staff/admin/owner."""
    from functools import wraps

    @wraps(view_func)
    @login_required(login_url='/admin-portal/login/')
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_admin_user:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('accounts:staff_login')
        return view_func(request, *args, **kwargs)

    return _wrapped


@staff_required
def member_list(request):
    members = Member.objects.prefetch_related('tags', 'memberships__plan').exclude(status='archived')
    status_filter = request.GET.get('status', '')
    tag_filter = request.GET.get('tag', '')
    search = request.GET.get('q', '')

    if status_filter:
        members = members.filter(status=status_filter)
    if tag_filter:
        members = members.filter(tags__id=tag_filter)
    if search:
        members = members.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search)
        )

    tags = Tag.objects.all()
    context = {
        'members': members,
        'tags': tags,
        'status_filter': status_filter,
        'tag_filter': tag_filter,
        'search': search,
        'page_title': 'Members',
    }
    return render(request, 'members/member_list.html', context)


@staff_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    memberships = member.memberships.select_related('plan').order_by('-start_date')
    appointments = member.appointments.select_related('service', 'staff__user').order_by('-date', '-start_time')[:20]
    payments = member.payments.order_by('-paid_at')[:10]
    membership_form = MemberMembershipForm()

    if request.method == 'POST' and 'add_membership' in request.POST:
        membership_form = MemberMembershipForm(request.POST)
        if membership_form.is_valid():
            mem = membership_form.save(commit=False)
            mem.member = member
            mem.save()
            messages.success(request, 'Membership assigned successfully.')
            return redirect('members:member_detail', pk=pk)

    context = {
        'member': member,
        'memberships': memberships,
        'appointments': appointments,
        'payments': payments,
        'membership_form': membership_form,
        'page_title': member.get_full_name(),
    }
    return render(request, 'members/member_detail.html', context)


@staff_required
def member_create(request):
    form = MemberForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        member = form.save()
        messages.success(request, f'Member {member.get_full_name()} created successfully.')
        return redirect('members:member_detail', pk=member.pk)
    return render(request, 'members/member_form.html', {'form': form, 'page_title': 'Add Member', 'action': 'Create'})


@staff_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    form = MemberForm(request.POST or None, request.FILES or None, instance=member)
    if form.is_valid():
        form.save()
        messages.success(request, 'Member updated successfully.')
        return redirect('members:member_detail', pk=pk)
    return render(request, 'members/member_form.html', {
        'form': form,
        'member': member,
        'page_title': f'Edit — {member.get_full_name()}',
        'action': 'Save Changes',
    })


@staff_required
def member_archive(request, pk):
    if request.method == 'POST':
        member = get_object_or_404(Member, pk=pk)
        member.status = 'archived'
        member.save()
        messages.success(request, f'{member.get_full_name()} has been archived.')
    return redirect('members:member_list')


@staff_required
def member_import_csv(request):
    form = CSVImportForm(request.POST or None, request.FILES or None)
    created = 0
    skipped = 0
    errors = []

    if request.method == 'POST' and form.is_valid():
        df = form.cleaned_data['csv_file']
        df.columns = df.columns.str.strip().str.lower()
        for _, row in df.iterrows():
            email = str(row.get('email', '')).strip()
            if not email or Member.objects.filter(email=email).exists():
                skipped += 1
                continue
            try:
                Member.objects.create(
                    first_name=str(row.get('first_name', '')).strip(),
                    last_name=str(row.get('last_name', '')).strip(),
                    email=email,
                    phone=str(row.get('phone', '')).strip(),
                    notes=str(row.get('notes', '')).strip(),
                )
                created += 1
            except Exception as e:
                errors.append(f"Row error ({email}): {e}")

        messages.success(request, f'Import complete: {created} created, {skipped} skipped.')
        if errors:
            for err in errors[:5]:
                messages.warning(request, err)
        return redirect('members:member_list')

    return render(request, 'members/member_import.html', {'form': form, 'page_title': 'Import Members CSV'})


@staff_required
def plan_list(request):
    plans = MembershipPlan.objects.all()
    return render(request, 'billing/plan_list.html', {'plans': plans, 'page_title': 'Membership Plans'})


@staff_required
def plan_create(request):
    from billing.forms import MembershipPlanForm
    form = MembershipPlanForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Plan created.')
        return redirect('billing:plan_list')
    return render(request, 'billing/plan_form.html', {'form': form, 'page_title': 'New Plan', 'action': 'Create'})


@staff_required
def plan_edit(request, pk):
    from billing.forms import MembershipPlanForm
    plan = get_object_or_404(MembershipPlan, pk=pk)
    form = MembershipPlanForm(request.POST or None, instance=plan)
    if form.is_valid():
        form.save()
        messages.success(request, 'Plan updated.')
        return redirect('billing:plan_list')
    return render(request, 'billing/plan_form.html', {
        'form': form, 'plan': plan, 'page_title': f'Edit Plan — {plan.name}', 'action': 'Save Changes',
    })
