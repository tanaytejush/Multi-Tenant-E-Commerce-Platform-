from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to extract tenant information from JWT token and attach it to the request.
    This ensures all requests are tenant-aware.
    """

    def process_request(self, request):
        # Skip tenant extraction for certain paths
        exempt_paths = ['/admin/', '/api/auth/register/', '/api/auth/login/']
        if any(request.path.startswith(path) for path in exempt_paths):
            request.tenant_id = None
            request.user_role = None
            return None

        # Try to extract tenant from JWT token
        jwt_auth = JWTAuthentication()
        try:
            # Get the token from the request
            header = jwt_auth.get_header(request)
            if header is None:
                request.tenant_id = None
                request.user_role = None
                return None

            raw_token = jwt_auth.get_raw_token(header)
            if raw_token is None:
                request.tenant_id = None
                request.user_role = None
                return None

            # Validate and decode the token
            validated_token = jwt_auth.get_validated_token(raw_token)

            # Extract custom claims
            request.tenant_id = validated_token.get('tenant_id')
            request.user_role = validated_token.get('role')

        except (InvalidToken, TokenError):
            request.tenant_id = None
            request.user_role = None

        return None
