from django.urls import path, include
from rest_framework import routers  # changed import
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()  # updated instantiation
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
