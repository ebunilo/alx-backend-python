from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, EditHistory

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if not created:
        return
    Notification.objects.create(user=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def track_message_edit(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return
    if previous.content != instance.content:
        editor = getattr(instance, 'editor_override', instance.sender)
        EditHistory.objects.create(
            message=instance,
            editor=editor,
            previous_content=previous.content,
            new_content=instance.content,
        )