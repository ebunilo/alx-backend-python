from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer, MessageHistorySerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

# Create your views here.

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    request.user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()  # cascades Messages, Notifications, MessageHistory
        return Response(status=status.HTTP_204_NO_CONTENT)

class MessageViewSet(ModelViewSet):
    queryset = (
        Message.objects.all()
        .select_related('sender', 'receiver', 'parent_message')
        .prefetch_related('history', 'notifications', 'replies')
    )
    serializer_class = MessageSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        message = self.get_object()
        ser = MessageHistorySerializer(message.history.all(), many=True)
        return Response(ser.data)

    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """
        Returns the recursive threaded conversation for this message.
        """
        message = self.get_object()
        return Response(message.build_thread())
