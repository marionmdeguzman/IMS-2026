from django.contrib import admin
from .models import Appointment, AvailabilitySlot, Waitlist


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['member', 'service', 'date', 'start_time', 'status', 'booking_source']
    list_filter = ['status', 'booking_source', 'date']
    search_fields = ['member__first_name', 'member__last_name', 'member__email']
    date_hierarchy = 'date'


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['staff', 'resource', 'day_of_week', 'start_time', 'end_time', 'is_active']


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ['member', 'service', 'preferred_date', 'is_notified']
