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

class OffensiveLanguageMiddleware:
    """
    Rate limits chat message POST requests by client IP.
    Limit: 5 messages per rolling 60-second window.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 5
        self.window_seconds = 60
        # ip -> list[datetime]
        self.ip_hits = {}

    def __call__(self, request):
        if request.method == 'POST':
            # Extract IP (support proxies)
            xff = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', 'unknown'))
            now = timezone.now()
            timestamps = self.ip_hits.get(ip, [])
            # Keep only those within window
            cutoff = now - timezone.timedelta(seconds=self.window_seconds)
            timestamps = [ts for ts in timestamps if ts > cutoff]
            if len(timestamps) >= self.limit:
                return HttpResponseForbidden("Rate limit exceeded: max 5 messages per minute.")
            timestamps.append(now)
            self.ip_hits[ip] = timestamps
        return self.get_response(request)
