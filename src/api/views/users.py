
"""Website Views."""
#python libraries
import hashlib
import random
import string

# Third-Party Libraries
import boto3
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import UserManager
from api.schemas.user_shema import UserSchema
from settings import COGNITO_ADMIN_GROUP, COGNTIO_USER_POOL_ID, logger
from utils.validator import validate_data

cognito = boto3.client("cognito-idp")
user_manager = UserManager()


class UsersView(MethodView):
    """UsersView."""

    def get(self):
        """Get all users."""
        response = cognito.list_users(UserPoolId=COGNTIO_USER_POOL_ID)
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
                    data = validate_data(aws_user, UserSchema)
                    data["Groups"] = []
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
            Username=dm_user["Username"], UserPoolId=COGNTIO_USER_POOL_ID, Limit=50
        )
        aws_user = cognito.admin_get_user(
            UserPoolId=COGNTIO_USER_POOL_ID, Username=dm_user["Username"]
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
                UserPoolId=COGNTIO_USER_POOL_ID, Username=username
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
                UserPoolId=COGNTIO_USER_POOL_ID,
                Username=username,
                GroupName=COGNITO_ADMIN_GROUP,
            )
            return jsonify(response)
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Failed to add user to admin group"}), 400

    def delete(self, username):
        """Remove user admin privlieges."""
        try:
            response = cognito.admin_remove_user_from_group(
                UserPoolId=COGNTIO_USER_POOL_ID,
                Username=username,
                GroupName=COGNITO_ADMIN_GROUP,
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

class UserAPIKeyView(MethodView):
    """Manage a users api key/s"""
    def get(self, username):
        """ Get a new api key for hte given user"""
        try:
            api_key_length = 16
            characters = string.ascii_letters + string.digits
            api_key = ''.join(random.SystemRandom().choice(characters) for i in range(api_key_length))
            hash_val = hashlib.sha256(str.encode(api_key)).hexdigest()
            user = user_manager.get(filter_data={"Username": username})
            user["HashedAPI"] = hash_val
            user_manager.update(document_id=user["_id"], data=user)
            return jsonify({"api_key": api_key})
        except:
            logger.exception(e)
            return jsonify({f"error": "Failed to create API key for {username}"}), 400

class UserHelpers:
    """Helper Class for user management."""

    def merge_additional_keys(base_dict, dict_to_add):
        """Merge Dicts."""
        for key in dict_to_add:
            if key not in base_dict:
                base_dict[key] = dict_to_add[key]
        return base_dict
