"""Auth Views."""
# Standard Python Libraries
from datetime import datetime, timedelta

# Third-Party Libraries
import boto3
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import LogManager, UserManager
from settings import COGNITO_CLIENT_ID, COGNTIO_USER_POOL_ID, logger
from utils.logs import cleanup_logs

cognito = boto3.client("cognito-idp")
user_manager = UserManager()
log_manager = LogManager()


class RegisterView(MethodView):
    """RegisterView."""

    def post(self):
        """Register a user."""
        try:
            data = request.json
            username = data["Username"]
            password = data["Password"]
            email = data["Email"]

            cognito.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}],
            )

            return jsonify(success=True)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Error registering user."}), 400


class SignInView(MethodView):
    """SignInView."""

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

        expires = datetime.utcnow() + timedelta(
            seconds=response["AuthenticationResult"]["ExpiresIn"]
        )
        
        logs_cleaned = cleanup_logs(username)
        logger.info(f"Cleanup up logs for {username} - {logs_cleaned}")
        return jsonify(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"],
                "expires_at": expires,
                "username": username,
            }
        )

class RefreshTokenView(MethodView):
    """Refresh User Token."""

    def post(self):
        """Refresh user token."""
        data = request.json
        logger.info(data)
        username = data['username']
        refreshToken = data["refeshToken"]

        response = cognito.admin_initiate_auth(
            UserPoolId=COGNTIO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refreshToken
            }
        )

        expires = datetime.utcnow() + timedelta(
            seconds=response["AuthenticationResult"]["ExpiresIn"]
        )
        
        logs_cleaned = cleanup_logs(username)
        logger.info(f"Cleanup up logs for {username} - {logs_cleaned}")
        return jsonify(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": refreshToken,
                "expires_at": expires,
                "username": username,
            }
        )     