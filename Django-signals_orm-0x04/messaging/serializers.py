from rest_framework import serializers
from .models import Message, EditHistory

class EditHistorySerializer(serializers.ModelSerializer):
    editor = serializers.StringRelatedField()

    class Meta:
        model = EditHistory
        fields = ['id', 'editor', 'previous_content', 'new_content', 'edited_at']


class MessageSerializer(serializers.ModelSerializer):
    history = EditHistorySerializer(source='edit_history', many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'created_at', 'timestamp', 'history']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            instance.editor_override = request.user
        return super().update(instance, validated_data)