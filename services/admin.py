from django.contrib import admin
from .models import Service, StaffMember, Resource


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'duration_minutes', 'price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'category']


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'is_available']
    filter_horizontal = ['services']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'resource_type', 'capacity', 'is_available']
    list_filter = ['resource_type', 'is_available']
