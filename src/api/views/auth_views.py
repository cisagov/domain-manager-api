"""Auth Views."""
# Standard Python Libraries
from datetime import datetime, timedelta

# Third-Party Libraries
import botocore
from flask import g, jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.config import logger
from api.manager import LogManager, UserManager
from utils.aws.clients import Cognito
from utils.logs import cleanup_logs
from utils.notifications import Notification

user_manager = UserManager()
log_manager = LogManager()
cognito = Cognito()


class RegisterView(MethodView):
    """RegisterView."""

    def post(self):
        """Register a user."""
        try:
            data = request.json
            username = data["Username"]
            password = data["Password"]
            email = data["Email"]

            g.username = "Registration"
            cognito.sign_up(username, password, email)
            user = cognito.get_user(username)
            user["Groups"] = []
            user["Groups"].append(
                {
                    "GroupName": data["ApplicationName"],
                    "Application_Id": data["ApplicationId"],
                }
            )
            user_manager.save(user)

            email = Notification(
                message_type="user_registered",
                context={
                    "new_user": data["Username"],
                    "application": data["ApplicationName"],
                },
            )
            email.send()

            return jsonify(success=True)
        except botocore.exceptions.ClientError as e:
            logger.exception(e)
            return e.response["Error"]["Message"], 400


class SignInView(MethodView):
    """SignInView."""

    def post(self):
        """Sign In User."""
        data = request.json
        username = data["username"]
        password = data["password"]

        try:
            response = cognito.authenticate(username, password)
        except botocore.exceptions.ClientError as e:
            logger.exception(e)
            return e.response["Error"]["Message"], 400

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


class ConfirmSignUpView(MethodView):
    """Confirm Email Sign Up View."""

    def post(self, username):
        """Confirm registration email of a new user."""
        post_data = request.json
        try:
            cognito.confirm_signup(
                username=username,
                confirmation_code=post_data["confirmation_code"],
            )
        except botocore.exceptions.ClientError as e:
            logger.exception(e)
            return e.response["Error"]["Message"], 400
        return jsonify({"success": "User email has been confirmed."}), 200


class ResetPasswordView(MethodView):
    """Reset User Password."""

    def post(self, username):
        """Enter a New Password and Email Confirmation Code."""
        post_data = request.json
        try:
            cognito.confirm_forgot_password(
                username=username,
                confirmation_code=post_data["confirmation_code"],
                password=post_data["password"],
            )
        except botocore.exceptions.ClientError as e:
            logger.exception(e)
            return e.response["Error"]["Message"], 400
        return jsonify({"success": "User password has been reset."}), 200

    def get(self, username):
        """Trigger a Password Reset."""
        try:
            cognito.reset_password(username=username)
        except botocore.exceptions.ClientError as e:
            logger.exception(e)
            return e.response["Error"]["Message"], 400
        return jsonify({"success": "An email with a reset code has been sent."}), 200


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
