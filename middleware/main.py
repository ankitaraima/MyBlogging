# filepath: /D:/Internship/NewBlog/blog/middleware/main.py
import time
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse

class ActivityLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Log user activities
        user = request.user if request.user.is_authenticated else 'Anonymous'
        path = request.path
        method = request.method
        print(f"User: {user}, Path: {path}, Method: {method}")

    def process_response(self, request, response):
        # Additional logging if needed
        return response

class RateLimitingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Rate limiting logic
        user_ip = request.META.get('REMOTE_ADDR')
        path = request.path
        key = f"rate_limit:{user_ip}:{path}"
        rate_limit = cache.get(key, 0)

        if rate_limit >= 5:  # Allow 5 requests per minute
            return JsonResponse({'error': 'Rate limit exceeded'}, status=429)

        cache.set(key, rate_limit + 1, timeout=60)  # Increment request count and set timeout

    def process_response(self, request, response):
        return response