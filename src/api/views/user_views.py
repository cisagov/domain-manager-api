"""User Views."""
# Standard Python Libraries
import hashlib
from http import HTTPStatus
import secrets

# Third-Party Libraries
import boto3
from flask import abort, g, jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import LogManager, UserManager
from api.schemas.user_shema import UserSchema
from settings import COGNITO_ADMIN_GROUP, COGNTIO_USER_POOL_ID, logger
from utils.decorators.auth import can_access_user
from utils.validator import validate_data

cognito = boto3.client("cognito-idp")
user_manager = UserManager()
log_manager = LogManager()


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

    decorators = [can_access_user]

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

        response["History"] = log_manager.all(params={"username": dm_user["Username"]})
        return jsonify(response)

    def delete(self, username):
        """Delete the user."""
        if not g.is_admin:
            abort(HTTPStatus.FORBIDDEN.value)
        try:
            cognito.admin_delete_user(
                UserPoolId=COGNTIO_USER_POOL_ID, Username=username
            )
            dm_user = user_manager.get(filter_data={"Username": username})
            user_manager.update(
                document_id=dm_user["_id"], data={"UserStatus": "DELETED"}
            )
            return jsonify({"success": f"{username} was deleted"})

        except Exception as e:
            logger.exception(e)
            return (
                jsonify({"error": f"Failed to delete user - {username}"}),
                HTTPStatus.BAD_REQUEST.value,
            )

    def put(self, username):
        """Disable or re-enable the user."""
        if not g.is_admin:
            abort(HTTPStatus.FORBIDDEN.value)
        try:
            dm_user = user_manager.get(filter_data={"Username": username})
            if dm_user["Enabled"]:
                new_status = False
                cognito.admin_disable_user(
                    UserPoolId=COGNTIO_USER_POOL_ID, Username=username
                )
            else:
                new_status = True
                cognito.admin_enable_user(
                    UserPoolId=COGNTIO_USER_POOL_ID, Username=username
                )

            dm_user["Enabled"] = new_status
            user_manager.update(document_id=dm_user["_id"], data=dm_user)
            return jsonify(
                {
                    "success": f"{username} enabled status - {new_status}",
                    "status": new_status,
                }
            )

        except Exception as e:
            logger.exception(e)
            return (
                jsonify({"error": f"Failed to disable/enable user - {username}"}),
                HTTPStatus.BAD_REQUEST.value,
            )


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
            return (
                jsonify({"error": "Failed to confirm user"}),
                HTTPStatus.BAD_REQUEST.value,
            )


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
            return (
                jsonify({"error": "Failed to add user to admin group"}),
                HTTPStatus.BAD_REQUEST.value,
            )

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
            return (
                jsonify({"error": "Failed to remove user from admin group"}),
                HTTPStatus.BAD_REQUEST.value,
            )


class UserGroupsView(MethodView):
    """Manage users groups."""

    def put(self, username):
        """Set users groups."""
        try:
            user = user_manager.get(filter_data={"Username": username})
            if "Groups" not in user:
                user["Groups"] = []
            if user["Groups"] == request.json:
                return jsonify({"error": "No changes made"}), HTTPStatus.ACCEPTED
            user["Groups"] = request.json

            response = user_manager.update(document_id=user["_id"], data=user)
            return jsonify(response)
        except Exception as e:
            logger.exception(e)
            return (
                jsonify({"error": "Failed to update user groups"}),
                HTTPStatus.BAD_REQUEST.value,
            )


class UserAPIKeyView(MethodView):
    """Manage a user's api key."""

    def get(self, username):
        """Get a new api key for the user."""
        try:
            api_key = secrets.token_urlsafe(40)
            hash_val = hashlib.sha256(str.encode(api_key)).hexdigest()
            user = user_manager.get(filter_data={"Username": username})
            user_manager.update(document_id=user["_id"], data={"HashedAPI": hash_val})
            return jsonify({"api_key": api_key})
        except Exception as e:
            logger.exception(e)
            return (
                jsonify({"error": f"Failed to create API key for {username}"}),
                HTTPStatus.BAD_REQUEST.value,
            )


class UserHelpers:
    """Helper Class for user management."""

    def merge_additional_keys(base_dict, dict_to_add):
        """Merge Dicts."""
        for key in dict_to_add:
            if key not in base_dict:
                base_dict[key] = dict_to_add[key]
        return base_dict
