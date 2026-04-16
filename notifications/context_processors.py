from .models import Notification


def unread_notifications(request):
    if request.user.is_authenticated and request.user.is_admin_user:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        recent = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return {'unread_notification_count': count, 'recent_notifications': recent}
    return {'unread_notification_count': 0, 'recent_notifications': []}
