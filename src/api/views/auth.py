"""Auth Views."""
# Standard Python Libraries
import base64
from datetime import datetime, timedelta
import hashlib
import hmac

# Third-Party Libraries
import boto3
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import LogManager, UserManager
from api.schemas.user_shema import UserSchema
from settings import (
    AWS_REGION,
    COGNITO_ADMIN_GROUP,
    COGNITO_CLIENT_ID,
    COGNITO_DEFAULT_ADMIN,
    COGNTIO_ENABLED,
    COGNTIO_USER_POOL_ID,
    logger,
)
from utils.validator import validate_data

cognito = boto3.client("cognito-idp")
user_manager = UserManager()
log_manager = LogManager()


class RegisterView(MethodView):
    """Register User View."""

    def get_secret_hash(username):
        msg = username + COGNITO_CLIENT_ID
        dig = hmac.new(
            str(CLIENT_SECRET).encode("utf-8"),
            msg=str(msg).encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        d2 = base64.b64encode(dig).decode()
        return d2

    def post(self):
        """register a user."""
        try:
            data = request.json
            username = data["Username"]
            password = data["Password"]
            email = data["Email"]

            resp = cognito.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}],
            )

            return jsonify(success=True)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Error registiring user."}), 400


class SignInView(MethodView):
    """Sign In User View."""

    def post(self):
        """Sign In User."""

        data = request.json
        username = data["username"]
        password = data["password"]

        response = cognito.admin_initiate_auth(
            UserPoolId=COGNTIO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="ADMIN_NO_SRP_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
            ClientMetadata={
                "username": username,
                "password": password,
            },
        )

        expireDate = datetime.utcnow() + timedelta(
            seconds=response["AuthenticationResult"]["ExpiresIn"]
        )
        return jsonify(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "expires_at": expireDate,
                "username": username,
            }
        )
