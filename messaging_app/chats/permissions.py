from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allows access only to participants of a conversation.
    """

    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # For Message objects
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False

    def has_permission(self, request, view):
        # Only allow authenticated users
        return request.user and request.user.is_authenticated
