from django.db import models
from accounts.models import User
from members.models import Member


class Notification(models.Model):
    TYPE_CHOICES = [
        ('appointment', 'Appointment'),
        ('membership', 'Membership'),
        ('payment', 'Payment'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title}"


class EmailBlast(models.Model):
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_to = models.ManyToManyField(Member, blank=True, related_name='email_blasts')
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_blasts')

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Blast: {self.subject} ({self.sent_at:%Y-%m-%d})"
