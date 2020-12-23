"""Decorator utils."""
# Standard Python Libraries
from functools import wraps
import logging
import os

# Third-Party Libraries
import cognitojwt
from flask import abort, request


class RequestAuth:
    """Authorization class for requests."""

    def __init__(self, request):
        """Initialize class with cognito settings and associated request."""
        self.request = request
        self.aws_default_region = os.environ.get("AWS_DEFAULT_REGION")
        self.aws_cognito_user_pool_id = os.environ.get("AWS_COGNITO_USER_POOL_ID")
        self.aws_cognito_user_pool_client_id = os.environ.get(
            "AWS_COGNITO_USER_POOL_CLIENT_ID"
        )
        self.aws_cognito_enabled = bool(int(os.environ.get("AWS_COGNITO_ENABLED", 0)))

    def validate(self):
        """Validate request."""
        if self.check_api_key(request):
            return True
        if not self.aws_cognito_enabled:
            return True
        if self.check_cognito_jwt(request):
            return True

        return False

    def check_api_key(self, request):
        """Check if API Key is valid."""
        if os.environ.get("API_KEY") == request.headers.get("api_key"):
            return True
        return False

    def get_authorization_header(self, request):
        """Get auth header."""
        auth_header = request.headers.get("Authorization", "")
        return auth_header

    def get_jwt_token(self, request):
        """Get JWT Token."""
        auth = self.get_authorization_header(request).split()
        if not auth or str(auth[0].lower()) != "bearer":
            return None
        if len(auth) != 2:
            return None
        return auth[1]

    def check_cognito_jwt(self, request):
        """Check if valid cognito jwt."""
        jwt = self.get_jwt_token(request)
        if not jwt:
            return False
        try:
            resp = cognitojwt.decode(
                jwt,
                self.aws_default_region,
                self.aws_cognito_user_pool_id,
                app_client_id=self.aws_cognito_user_pool_client_id,
            )
            return resp["username"]
        except Exception as e:
            logging.exception(e)
            return False


def auth_required(view):
    """Authorize requests."""

    @wraps(view)
    def decorated(*args, **kwargs):
        """Decorate."""
        auth = RequestAuth(request)
        if auth.validate():
            return view(*args, **kwargs)
        else:
            abort(401)

    return decorated
