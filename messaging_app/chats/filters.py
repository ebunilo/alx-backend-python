import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    user = django_filters.NumberFilter(method='filter_user')

    def filter_user(self, queryset, name, value):
        return queryset.filter(sender_id=value) | queryset.filter(recipient_id=value)

    class Meta:
        model = Message
        fields = [
            'conversation',
            'sender',
            'recipient',
            'created_after',
            'created_before',
            'user',
        ]
