"""Website Views."""
# Standard Python Libraries
import os

# Third-Party Libraries
import boto3
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import UserManager
from api.schemas.user_shema import UserSchema
from settings import logger
from utils.validator import validate_data

route53 = boto3.client("route53")
client_id = os.environ.get("AWS_COGNITO_USER_POOL_CLIENT_ID", 0)
user_pool_id = os.environ.get("AWS_COGNITO_USER_POOL_ID", 0)
adminGroup = os.environ.get("AWS_COGNITO_ADMIN_GROUP_NAME", 0)
cognito = boto3.client("cognito-idp")
user_manager = UserManager()


class UsersView(MethodView):
    """UsersView."""

    def get(self):
        """Get all users."""
        response = cognito.list_users(UserPoolId=user_pool_id)
        aws_users = response["Users"]
        dm_users = user_manager.all(params=request.args)
        self.merge_user_lists(aws_users, dm_users)

        return jsonify(aws_users)

    def merge_user_lists(self, aws_users, dm_users):
        """Merge AWS Users from Cognito with Database."""
        for aws_user in aws_users:
            if len(dm_users) <= 0:
                data = validate_data(aws_user, UserSchema)
                user_manager.save(data)
            for dm_user in dm_users:
                if aws_user["Username"] == dm_user["Username"]:
                    self.merge_user(aws_user, dm_user)
                    break
                if dm_user == dm_users[-1] or len(dm_users) <= 0:
                    # Last dm user reached and aws user not found, add to db
                    data["Groups"] = []
                    data = validate_data(aws_user, UserSchema)
                    user_manager.save(data)

    def merge_user(self, aws_user, dm_user):
        """Merge AWS User with Domain Manager User."""
        for key in dm_user:
            if key not in aws_user:
                aws_user[key] = dm_user[key]


class UserView(MethodView):
    """UserView."""

    def get(self, username):
        """Get User details."""
        dm_user = user_manager.get(filter_data={"Username": username})
        groups = cognito.admin_list_groups_for_user(
            Username=dm_user["Username"], UserPoolId=user_pool_id, Limit=50
        )
        aws_user = cognito.admin_get_user(
            UserPoolId=user_pool_id, Username=dm_user["Username"]
        )
        response = UserHelpers.merge_additional_keys(aws_user, dm_user)
        if "Groups" not in response:
            response["Groups"] = []
        if groups["Groups"]:
            for item in groups["Groups"]:
                response["Groups"].append(item)
        return jsonify(response)


class UserConfirmView(MethodView):
    """User Confirm View."""

    def get(self, username):
        """Confirm the selected user."""
        try:
            response = cognito.admin_confirm_sign_up(
                UserPoolId=user_pool_id, Username=username
            )
            user = user_manager.get(filter_data={"Username": username})
            user["UserStatus"] = "CONFIRMED"
            user_manager.update(document_id=user["_id"], data=user)
            return jsonify(response)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Failed to confirm user"}), 400


class UserAdminStatusView(MethodView):
    """Set Users admin status."""

    def get(self, username):
        """Set the user as an admin."""
        try:
            response = cognito.admin_add_user_to_group(
                UserPoolId=user_pool_id, Username=username, GroupName=adminGroup
            )
            return jsonify(response)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Failed to add user to admin group"}), 400

    def delete(self, username):
        """Remove user admin privlieges."""
        try:
            response = cognito.admin_remove_user_from_group(
                UserPoolId=user_pool_id, Username=username, GroupName=adminGroup
            )
            return jsonify(response)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Failed to remove user from admin group"}), 400


class UserGroupsView(MethodView):
    """Manage users groups."""

    def put(self, username):
        """Set users groups."""
        try:
            user = user_manager.get(filter_data={"Username": username})
            if "Groups" not in user:
                user["Groups"] = []
            if user["Groups"] == request.json:
                return jsonify({"error": "No changes made"}), 200
            user["Groups"] = request.json

            response = user_manager.update(document_id=user["_id"], data=user)
            return jsonify(response)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Failed to update user groups"}), 400


class UserHelpers:
    """Helper Class for user management."""

    def merge_additional_keys(base_dict, dict_to_add):
        """Merge Dicts."""
        for key in dict_to_add:
            if key not in base_dict:
                base_dict[key] = dict_to_add[key]
        return base_dict
