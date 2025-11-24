from rest_framework import serializers
from .models import Message, MessageHistory

class MessageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageHistory
        fields = ['id', 'previous_content', 'logged_at']


class MessageSerializer(serializers.ModelSerializer):
    history = MessageHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'created_at', 'timestamp', 'history']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            instance.editor_override = request.user
        return super().update(instance, validated_data)