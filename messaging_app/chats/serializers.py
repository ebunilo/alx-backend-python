from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'role', 'created_at', 'password'
        ]
        read_only_fields = ['id', 'created_at', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.password_hash = user.password  # mirrors hashed password
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
            instance.password_hash = instance.password
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'sender', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['id', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        convo = Conversation.objects.create(**validated_data)
        if participants:
            convo.participants.set(participants)
        return convo

    def update(self, instance, validated_data):
        participants = validated_data.pop('participants', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if participants is not None:
            instance.participants.set(participants)
        return instance