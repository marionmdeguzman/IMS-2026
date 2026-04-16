from django.contrib import admin
from .models import Notification, EmailBlast


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'user', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']


@admin.register(EmailBlast)
class EmailBlastAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sent_by', 'sent_at']
    filter_horizontal = ['sent_to']
