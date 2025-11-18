from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_path = settings.BASE_DIR / 'requests.log'

    def __call__(self, request):
        user = getattr(request, 'user', None)
        user_label = user.username if getattr(user, 'is_authenticated', False) else 'Anonymous'
        try:
            with open(self.log_path, 'a', encoding='utf-8') as fh:
                fh.write(f"{datetime.now()} - User: {user_label} - Path: {request.path}\n")
        except Exception:
            pass
        return self.get_response(request)

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Allowed window: 18:00 (6PM) <= time < 21:00 (9PM)
        self.start_hour = 18
        self.end_hour = 21

    def __call__(self, request):
        now = timezone.localtime()
        hour = now.hour
        if hour < self.start_hour or hour >= self.end_hour:
            return HttpResponseForbidden("Access restricted outside 6PM–9PM.")
        return self.get_response(request)