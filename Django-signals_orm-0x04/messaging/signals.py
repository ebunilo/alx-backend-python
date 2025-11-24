from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if not created:
        return
    Notification.objects.create(user=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def log_message_history(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return
    if previous.content != instance.content:
        MessageHistory.objects.create(
            message=previous,
            previous_content=previous.content,
        )
        editor = getattr(instance, 'editor_override', None)
        instance.edited = True
        instance.edited_at = timezone.now()
        if editor and getattr(editor, 'is_authenticated', False):
            instance.edited_by = editor