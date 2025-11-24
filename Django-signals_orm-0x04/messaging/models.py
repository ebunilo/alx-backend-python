from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone

User = get_user_model()

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='message_edits',
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['receiver', 'timestamp']),
        ]

    def __str__(self):
        return f'Msg {self.id} from {self.sender} to {self.receiver}'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'read', 'timestamp']),
        ]

    def __str__(self):
        return f'Notification {self.id} to {self.user} (read={self.read})'


class MessageHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    previous_content = models.TextField()
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']
        indexes = [
            models.Index(fields=['message', 'logged_at']),
        ]

    def __str__(self):
        return f'History {self.id} for Message {self.message_id}'


from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Message)
def create_message_history(sender, instance, **kwargs):
    if instance.pk:  # Message instance is being updated
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            old_instance = None

        if old_instance and old_instance.content != instance.content:
            # Content has changed, create a MessageHistory entry
            MessageHistory.objects.create(
                message=instance,
                previous_content=old_instance.content
            )
            # Update edited metadata
            instance.edited = True
            instance.edited_at = timezone.now()
            instance.edited_by = instance.sender  # Assuming the sender is the one editing
