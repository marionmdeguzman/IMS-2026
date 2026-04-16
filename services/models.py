from django.db import models
from accounts.models import User


class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default='#6366F1')

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class StaffMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    specialization = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    services = models.ManyToManyField(Service, blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.specialization or 'Staff'})"

    def get_full_name(self):
        return self.user.get_full_name()


class Resource(models.Model):
    name = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=100)
    capacity = models.IntegerField(default=1)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['resource_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.resource_type})"
