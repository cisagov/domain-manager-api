"""User Views."""
# Standard Python Libraries
import hashlib
from http import HTTPStatus
import secrets

# Third-Party Libraries
from flask import abort, g, jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import LogManager, UserManager
from settings import logger
from utils.aws.clients import Cognito
from utils.decorators.auth import can_access_user
from utils.notifications import Notification
from utils.users import get_email_from_user, get_users_in_group

user_manager = UserManager()
log_manager = LogManager()
cognito = Cognito()


class UsersView(MethodView):
    """UsersView."""

    def get(self):
        """Get all users."""
        application = request.args.get("application")
        if application:
            return jsonify(get_users_in_group(application))

        self.aws_users = cognito.list_users()
        self.dm_users = user_manager.all(params=request.args)
        self.merge_user_lists()

        return jsonify(self.aws_users)

    def merge_user_lists(self):
        """Merge AWS Users from Cognito with Database."""
        aws_usernames = {u["Username"] for u in self.aws_users}
        dm_usernames = {u["Username"] for u in self.dm_users}

        # Don't need to update everyone time,
        # uncomment when database is out of sync again.
        # common_users = aws_usernames.intersection(dm_usernames)
        # for user in common_users:
        #     self.update_user(user)

        # Add users not in database
        not_in_dm = aws_usernames.difference(dm_usernames)
        for user in not_in_dm:
            self.add_user(user)

        # Remove users that don't exist in AWS
        not_in_aws = dm_usernames.difference(aws_usernames)
        for user in not_in_aws:
            self.remove_user(user)

    def remove_user(self, username):
        """Remove user from database."""
        dm_user = self.get_user(self.dm_users, username)
        user_manager.delete(document_id=dm_user["_id"])

    def add_user(self, username):
        """Add user to database."""
        aws_user = self.get_user(self.aws_users, username)
        aws_user["Groups"] = []
        user_manager.save(aws_user)

    def update_user(self, username):
        """Update user in database."""
        aws_user = self.get_user(self.aws_users, username)
        dm_user = self.get_user(self.dm_users, username)
        user_manager.update(document_id=dm_user["_id"], data=aws_user)

    def get_user(self, users, username):
        """Get user from list by username."""
        return next(filter(lambda x: x["Username"] == username, users), None)


class UserView(MethodView):
    """UserView."""

    decorators = [can_access_user]

    def get(self, username):
        """Get User details."""
        dm_user = user_manager.get(filter_data={"Username": username})
        groups = cognito.get_user_groups(dm_user["Username"])
        aws_user = cognito.get_user(dm_user["Username"])
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
            cognito.delete_user(username)
            dm_user = user_manager.get(filter_data={"Username": username})
            user_manager.delete(document_id=dm_user["_id"])
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
                cognito.disable_user(username)
            else:
                new_status = True
                cognito.enable_user(username)

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
            response = cognito.confirm_user(username)
            user = user_manager.get(filter_data={"Username": username})
            user["UserStatus"] = "CONFIRMED"
            user_manager.update(document_id=user["_id"], data=user)
            cog_user = cognito.get_user(username)

            email = Notification(
                message_type="user_confirmed",
                context={
                    "Username": user["Username"],
                    "UserEmail": get_email_from_user(cog_user),
                },
            )
            email.send()
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
            response = cognito.add_admin_user(username)
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
            response = cognito.remove_admin_user(username)
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

    decorators = [can_access_user]

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
