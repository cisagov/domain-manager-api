"""Decorator utils."""
# Standard Python Libraries
from functools import wraps
import hashlib

# Third-Party Libraries
import boto3
import cognitojwt
from flask import abort, g, request

# cisagov Libraries
from api.manager import DomainManager, UserManager
from settings import (
    AWS_REGION,
    COGNITO_ADMIN_GROUP,
    COGNITO_CLIENT_ID,
    COGNITO_DEFAULT_ADMIN,
    COGNTIO_ENABLED,
    COGNTIO_USER_POOL_ID,
    logger,
)
from utils.user_profile import user_can_access_domain

domain_manager = DomainManager()
user_manager = UserManager()


class RequestAuth:
    """Authorization class for requests."""

    def __init__(self, request):
        """Initialize class with cognito settings and associated request."""
        self.request = request
        self.cognito = boto3.client("cognito-idp")
        self.username = ""

    def validate(self):
        """Validate request."""
        if self.check_api_key(request):
            g.is_admin = True
            return True
        if not COGNTIO_ENABLED:
            g.is_admin = True
            return True
        if self.check_cognito_jwt(request):
            return True

        return False

    def check_api_key(self, request):
        """Check if API Key is valid."""
        if "api_key" in request.headers:
            hash_val = hashlib.sha256(
                str.encode(request.headers.get("api_key"))
            ).hexdigest()
            user = user_manager.all(params={"HashedAPI": hash_val})
            if not user:
                return False
            if len(user) > 1:
                logger.info(f"Hash Key collision - {hash_val}")
                return False

            matched_user = user[0]
            self.username = matched_user["Username"]
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
            logger.info(jwt)
            resp = cognitojwt.decode(
                jwt,
                AWS_REGION,
                COGNTIO_USER_POOL_ID,
                app_client_id=COGNITO_CLIENT_ID,
            )
            logger.info(resp)
            self.username = resp["cognito:username"]
            return self.username
        except Exception as e:
            logger.exception(e)
            return False

    def check_admin_status(self):
        """Check if user is in the admin cognito group."""
        if not COGNTIO_ENABLED:
            return True
        if COGNITO_DEFAULT_ADMIN:
            return True

        resp = self.cognito.admin_list_groups_for_user(
            Username=self.username, UserPoolId=COGNTIO_USER_POOL_ID, Limit=60
        )
        for group in resp["Groups"]:
            if group["GroupName"] == COGNITO_ADMIN_GROUP:
                return True
        return False


def auth_required(view):
    """Authorize requests."""

    @wraps(view)
    def decorated(*args, **kwargs):
        """Decorate."""
        auth = RequestAuth(request)
        if auth.validate():
            g.username = auth.username
            if auth.check_admin_status():
                g.is_admin = True
            else:
                g.is_admin = False
            return view(*args, **kwargs)
        else:
            abort(401)

    return decorated


def auth_admin_required(view):
    """Authorize requests."""

    @wraps(view)
    def decorated(*args, **kwargs):
        """Decorate."""
        auth = RequestAuth(request)
        if auth.validate():
            if auth.check_admin_status():
                g.username = auth.username
                g.is_admin = True
                return view(*args, **kwargs)
            else:
                abort(401)
        else:
            abort(401)

    return decorated


def can_access_domain(view):
    """Check if user can access domain."""

    @wraps(view)
    def decorated(*args, **kwargs):
        """Decorate."""
        if kwargs.get("domain_id"):
            domain = domain_manager.get(
                document_id=kwargs.get("domain_id"), fields=["application_id"]
            )
            if user_can_access_domain(domain):
                return view(*args, **kwargs)
            else:
                return "User does not have permission to domain.", 400
        else:
            return "URL Path configured improperly.", 500

    return decorated
