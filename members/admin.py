from django.contrib import admin
from .models import Member, Tag, MembershipPlan, MemberMembership


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'status', 'created_at']
    list_filter = ['status', 'tags']
    search_fields = ['first_name', 'last_name', 'email']
    filter_horizontal = ['tags']


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_days', 'price', 'is_active']


@admin.register(MemberMembership)
class MemberMembershipAdmin(admin.ModelAdmin):
    list_display = ['member', 'plan', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'plan']
