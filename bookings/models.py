import secrets
from django.db import models
from django.utils import timezone
from members.models import Member
from services.models import Service, StaffMember, Resource


class AvailabilitySlot(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, null=True, blank=True, related_name='availability')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True, related_name='availability')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        entity = str(self.staff) if self.staff else str(self.resource)
        return f"{entity} — {self.get_day_of_week_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    BOOKING_SOURCE_CHOICES = [
        ('staff', 'Staff'),
        ('public', 'Public'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    staff = models.ForeignKey(StaffMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    resource = models.ForeignKey(Resource, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    booking_source = models.CharField(max_length=20, choices=BOOKING_SOURCE_CHOICES, default='staff')
    public_booking_token = models.CharField(max_length=64, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['public_booking_token']),
        ]

    def __str__(self):
        return f"{self.member} — {self.service.name} on {self.date}"

    def save(self, *args, **kwargs):
        if not self.public_booking_token:
            self.public_booking_token = secrets.token_hex(32)
        if self.status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        elif self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_cancellable(self):
        return self.status in ('pending', 'confirmed') and self.date >= timezone.now().date()

    @property
    def duration_display(self):
        from datetime import datetime, timedelta
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        diff = end - start
        mins = int(diff.total_seconds() / 60)
        if mins >= 60:
            h = mins // 60
            m = mins % 60
            return f"{h}h {m}m" if m else f"{h}h"
        return f"{mins}m"


class Waitlist(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='waitlist_entries')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    preferred_date = models.DateField()
    preferred_staff = models.ForeignKey(StaffMember, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    is_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['preferred_date', 'created_at']

    def __str__(self):
        return f"{self.member} waiting for {self.service.name} on {self.preferred_date}"
