"""Website Views."""
# Standard Python Libraries
from datetime import datetime
import io
import os
import shutil

# Third-Party Libraries
import boto3
from flask import current_app, jsonify, request, send_file
from flask.views import MethodView
import requests

# cisagov Libraries
from api.schemas.user_shema import UserSchema
from settings import logger
from utils.validator import validate_data


route53 = boto3.client("route53")
region =  os.environ.get("AWS_REGION", 0)
access_key = os.environ.get("AWS_ACCESS_KEY_ID", 0)
secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", 0)
client_id = os.environ.get("AWS_COGNITO_USER_POOL_CLIENT_ID", 0)
user_pool_id = os.environ.get("AWS_COGNITO_USER_POOL_ID", 0)
cognito = boto3.client(
    'cognito-idp',
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_access_key,   
    )

class UsersView(MethodView):
    """UsersView."""

    def get(self):
        """Get all users."""
        response = cognito.list_users(
            UserPoolId=user_pool_id
        )
        return jsonify(response["Users"])

class UserView(MethodView):
    """UserView."""

    def get(self, user_id):
        """Get User details."""
        return f"Test Val {user_id}"
