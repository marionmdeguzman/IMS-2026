from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, EmailBlast
from .forms import EmailBlastForm
from members.models import Member
from members.views import staff_required


@staff_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark all as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'page_title': 'Notifications',
    })


@staff_required
def email_blast(request):
    form = EmailBlastForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        subject = form.cleaned_data['subject']
        body = form.cleaned_data['body']
        recipients_qs = form.cleaned_data.get('recipients')
        if not recipients_qs or len(recipients_qs) == 0:
            recipients_qs = Member.objects.filter(status='active').exclude(email='')

        emails = [m.email for m in recipients_qs if m.email]
        if emails:
            for email in emails:
                try:
                    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
                except Exception:
                    pass

        blast = EmailBlast.objects.create(subject=subject, body=body, sent_by=request.user)
        blast.sent_to.set(recipients_qs)
        messages.success(request, f'Email blast sent to {len(emails)} recipients.')
        return redirect('notifications:email_blast')

    blasts = EmailBlast.objects.order_by('-sent_at')[:10]
    return render(request, 'notifications/email_blast.html', {
        'form': form,
        'blasts': blasts,
        'page_title': 'Email Blast',
    })
