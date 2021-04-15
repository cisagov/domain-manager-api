"""Auth Views."""
# Standard Python Libraries
from datetime import datetime, timedelta

# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import LogManager, UserManager
from settings import logger
from utils.aws import cognito
from utils.logs import cleanup_logs

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

            cognito.sign_up(username, password, email)

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

        response = cognito.authenticate(username, password)

        expires = datetime.utcnow() + timedelta(
            seconds=response["AuthenticationResult"]["ExpiresIn"]
        )

        cleanup_logs(username)
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
        username = data["username"]
        refresh_token = data["refeshToken"]
        response = cognito.refresh(refresh_token)

        expires = datetime.utcnow() + timedelta(
            seconds=response["AuthenticationResult"]["ExpiresIn"]
        )

        cleanup_logs(username)
        return jsonify(
            {
                "id_token": response["AuthenticationResult"]["IdToken"],
                "refresh_token": refresh_token,
                "expires_at": expires,
                "username": username,
            }
        )
