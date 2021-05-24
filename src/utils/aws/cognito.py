"""AWS Cognito."""
# Third-Party Libraries
import boto3

# cisagov Libraries
from settings import COGNITO_ADMIN_GROUP, COGNITO_CLIENT_ID, COGNTIO_USER_POOL_ID
from utils.users import get_email_from_user, get_emails_from_users

cognito = boto3.client("cognito-idp")


def get_user_groups(username: str):
    """Get groups for user."""
    return cognito.admin_list_groups_for_user(
        Username=username, UserPoolId=COGNTIO_USER_POOL_ID, Limit=50
    )


def get_user(username: str, return_email: bool = False):
    """Get user from cognito."""
    user = cognito.admin_get_user(UserPoolId=COGNTIO_USER_POOL_ID, Username=username)
    if return_email:
        return get_email_from_user(user)
    return user


def get_admin_users(return_emails: bool = False):
    """Get admin users from cognito."""
    users = cognito.list_users_in_group(
        UserPoolId=COGNTIO_USER_POOL_ID, GroupName=COGNITO_ADMIN_GROUP
    )["Users"]

    if return_emails:
        return get_emails_from_users(users)
    return users


def list_users(return_emails: bool = False):
    """List users in cognito."""
    users = cognito.list_users(UserPoolId=COGNTIO_USER_POOL_ID)["Users"]
    if return_emails:
        return get_emails_from_users(users)
    return users


def delete_user(username):
    """Delete user from cognito."""
    cognito.admin_disable_user(UserPoolId=COGNTIO_USER_POOL_ID, Username=username)
    return cognito.admin_delete_user(UserPoolId=COGNTIO_USER_POOL_ID, Username=username)


def disable_user(username):
    """Disable user in cognito."""
    return cognito.admin_disable_user(
        UserPoolId=COGNTIO_USER_POOL_ID, Username=username
    )


def enable_user(username):
    """Enable user in cognito."""
    return cognito.admin_enable_user(UserPoolId=COGNTIO_USER_POOL_ID, Username=username)


def confirm_user(username):
    """Confirm user in cognito."""
    return cognito.admin_confirm_sign_up(
        UserPoolId=COGNTIO_USER_POOL_ID, Username=username
    )


def add_admin_user(username):
    """Add user to admin group."""
    return cognito.admin_add_user_to_group(
        UserPoolId=COGNTIO_USER_POOL_ID,
        Username=username,
        GroupName=COGNITO_ADMIN_GROUP,
    )


def remove_admin_user(username):
    """Remove user from admin group."""
    return cognito.admin_remove_user_from_group(
        UserPoolId=COGNTIO_USER_POOL_ID,
        Username=username,
        GroupName=COGNITO_ADMIN_GROUP,
    )


def sign_up(username, password, email):
    """Sign up user in domain manager."""
    return cognito.sign_up(
        ClientId=COGNITO_CLIENT_ID,
        Username=username,
        Password=password,
        UserAttributes=[{"Name": "email", "Value": email}],
    )


def authenticate(username, password):
    """Authenticate user."""
    return cognito.admin_initiate_auth(
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


def refresh(token):
    """Refresh auth token."""
    return cognito.admin_initiate_auth(
        UserPoolId=COGNTIO_USER_POOL_ID,
        ClientId=COGNITO_CLIENT_ID,
        AuthFlow="REFRESH_TOKEN_AUTH",
        AuthParameters={"REFRESH_TOKEN": token},
    )


def getUser(username):
    """Get the users info by username."""
    return cognito.admin_get_user(UserPoolId=COGNTIO_USER_POOL_ID, Username=username)
