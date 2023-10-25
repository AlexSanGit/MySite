# context_processors.py
# В этом файле регистрируются тэги , чтобы они были доступны во всех шаблонах.

from .models import Profile


def unread_notifications(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        notifications = profile.notifications.split('\n') if profile.notifications else []
        has_unread_notifications = any("Пост" in notification for notification in notifications)
    else:
        has_unread_notifications = False

    return {'has_unread_notifications': has_unread_notifications}
