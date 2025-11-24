from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer, EditHistorySerializer

# Create your views here.

class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        message = self.get_object()
        qs = message.edit_history.all()
        ser = EditHistorySerializer(qs, many=True)
        return Response(ser.data)
