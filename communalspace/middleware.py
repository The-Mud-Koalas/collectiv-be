from .settings import CORS_ALLOWED_ORIGINS
from .exceptions import ImproperNetworkAccessException


class CorsOriginPresenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('HTTP_ORIGIN') not in CORS_ALLOWED_ORIGINS:
            raise ImproperNetworkAccessException('Origin not allowed')

        response = self.get_response(request)
        return response
