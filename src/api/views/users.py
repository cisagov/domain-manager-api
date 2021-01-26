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
from api.manager import (
    UserManager,
)
from api.schemas.user_shema import UserSchema
from settings import logger
from utils.validator import validate_data


route53 = boto3.client("route53")
client_id = os.environ.get("AWS_COGNITO_USER_POOL_CLIENT_ID", 0)
user_pool_id = os.environ.get("AWS_COGNITO_USER_POOL_ID", 0)
adminGroup = os.environ.get("AWS_COGNITO_ADMIN_GROUP_NAME", 0)
cognito = boto3.client(
    'cognito-idp'
    )
user_manager = UserManager()

class UsersView(MethodView):
    """UsersView."""

    def get(self):
        """Get all users."""
        response = cognito.list_users(
            UserPoolId=user_pool_id
        )
        aws_users = response["Users"]
        dm_users = user_manager.all(params=request.args)
        self.mergeUserLists(aws_users,dm_users)

        return jsonify(aws_users)
    
    def mergeUserLists(self, awsUsers, dmUsers):
        for awsUser in awsUsers:
            if len(dmUsers) <= 0:
                data = validate_data(awsUser, UserSchema)
                user_manager.save(data)
            for dmUser in dmUsers:
                if awsUser["Username"] == dmUser["Username"]:
                    self.mergeUser(awsUser,dmUser)
                    break
                if dmUser == dmUsers[-1] or len(dmUsers) <= 0:
                    # Last dm user reached and aws user not found, add to db
                    data = validate_data(awsUser, UserSchema)
                    user_manager.save(data)
    
    def mergeUser(self, awsUser, dmUser):
        for key in dmUser:
            if key not in awsUser:
                awsUser[key] = dmUser[key]


class UserView(MethodView):
    """UserView."""

    def get(self, username):
        """Get User details."""
        dm_user = user_manager.get(
                filter_data={"Username": username}
            )
        groups = cognito.admin_list_groups_for_user(
            Username=dm_user["Username"],
            UserPoolId=user_pool_id,
            Limit=50
        )
        aws_user = cognito.admin_get_user(
            UserPoolId=user_pool_id,
            Username=dm_user["Username"]
        )
        response = UserHelpers.mergeAdditionalKeys(aws_user,dm_user)
        response["Groups"] = groups["Groups"]
        return jsonify(response)

class UserConfirmView(MethodView):
    """User Confirm View"""

    def get(self, username):
        """Confirm the selected user"""
        try:
            response = cognito.admin_confirm_sign_up(
                UserPoolId=user_pool_id,
                Username=username
            )
            user = user_manager.get(
                filter_data={"Username": username}
            )
            user["UserStatus"] = "CONFIRMED"
            user_manager.update(
                document_id = user["_id"], 
                data = user
            )
            return jsonify(response)
        except:
            return jsonify({"error": "Failed to confirm user"}), 400

class UserAdminStatus(MethodView):
    """Set Users admin status"""
    
    def get(self,username):
        """Set the user as an admin"""
        try:
            response = cognito.admin_add_user_to_group(
                UserPoolId=user_pool_id,
                Username=username,
                GroupName=adminGroup
            )
            return jsonify(response)
        except:
            return jsonify({"error": "Failed to add user to admin group"}), 400

    def delete(self,username):
        """Remove user admin privlieges"""
        try:
            response = cognito.admin_remove_user_from_group(
                UserPoolId=user_pool_id,
                Username=username,
                GroupName=adminGroup
            )
            return jsonify(response)
        except:
            return jsonify({"error": "Failed to remove user from admin group"}), 400

class UserHelpers():
    """Helper Class for user management"""

    def mergeAdditionalKeys(baseDict, dictToAdd):
        """Merge a """
        for key in dictToAdd:
            if key not in baseDict:
                baseDict[key] = dictToAdd[key]
        return baseDict
            
