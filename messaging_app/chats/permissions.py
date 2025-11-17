from rest_framework import permissions

class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to allow users to access only their own messages/conversations.
    Assumes the view has a 'get_object()' method returning the object.
    """

    def has_object_permission(self, request, view, obj):
        # For a conversation, check if user is a participant
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # For a message, check if user is sender or recipient
        if hasattr(obj, 'sender') and hasattr(obj, 'recipient'):
            return request.user == obj.sender or request.user == obj.recipient
        return False
