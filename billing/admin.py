from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'method', 'status', 'paid_at', 'recorded_by']
    list_filter = ['method', 'status']
    search_fields = ['member__first_name', 'member__last_name', 'reference_number']
    date_hierarchy = 'paid_at'
