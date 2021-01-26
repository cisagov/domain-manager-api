"""Website Views."""
# Third-Party Libraries
import boto3
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import UserManager
from api.schemas.user_shema import UserSchema
from settings import COGNITO_CLIENT_ID, COGNTIO_USER_POOL_ID
from utils.validator import validate_data

route53 = boto3.client("route53")
cognito = boto3.client("cognito-idp")
user_manager = UserManager()


class UsersView(MethodView):
    """UsersView."""

    def get(self):
        """Get all users."""
        response = cognito.list_users(UserPoolId=COGNTIO_USER_POOL_ID)
        aws_users = response["Users"]
        dm_users = user_manager.all(params=request.args)
        self.merge_user_list(aws_users, dm_users)

        return jsonify(aws_users)

    def merge_user_list(self, aws_users, db_users):
        """Merge current database list of users with list in cognito."""
        for aws_user in aws_users:
            if len(db_users) <= 0:
                data = validate_data(aws_user, UserSchema)
                user_manager.save(data)
            for db_user in db_users:
                if aws_user["Username"] == db_user["Username"]:
                    self.merge_user(aws_user, db_user)
                    break
                if db_user == db_users[-1] or len(db_users) <= 0:
                    # Last dm user reached and aws user not found, add to db
                    data = validate_data(aws_user, UserSchema)
                    user_manager.save(data)

    def merge_user(self, aws_user, db_user):
        """Merge database user with cognito user."""
        for key in db_user:
            if key not in aws_user:
                aws_user[key] = db_user[key]


class UserView(MethodView):
    """UserView."""

    def get(self, username):
        """Get User details."""
        user = user_manager.get(filter_data={"Username": username})
        cognito.admin_list_groups_for_user(
            Username=user["Username"], UserPoolId=COGNTIO_USER_POOL_ID, Limit=1
        )
        return jsonify(user)


class UserConfirmView(MethodView):
    """UserConfirmView."""

    def get(self, username):
        """Confirm the selected user."""
        try:
            cognito.admin_confirm_sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
            )
        except Exception:
            return jsonify({"error": "Failed to confirm user"}), 400
