# fashion_store/middleware/visit_logging.py
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger("visits")

class VisitLoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        try:
            user = getattr(request, "user", None)
            username = user.username if getattr(user, "is_authenticated", False) else "anon"
        except Exception:
            username = "anon"

        path = request.get_full_path() if hasattr(request, "get_full_path") else getattr(request, "path", "-")
        method = getattr(request, "method", "-")
        status = getattr(response, "status_code", 0)
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = (xff.split(",").strip() if xff else request.META.get("REMOTE_ADDR", "")) or "-"

        logger.info(f"user={username} ip={ip} method={method} path={path} status={status}")
        return response
