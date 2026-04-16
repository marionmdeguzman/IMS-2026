from django.db import models
from accounts.models import User
from members.models import Member, MemberMembership
from bookings.models import Appointment


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('gcash', 'GCash'),
        ('maya', 'Maya'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment')
    membership = models.ForeignKey(MemberMembership, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')
    paid_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_payments')

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f"Payment #{self.pk} — {self.member} — ₱{self.amount} ({self.method})"
