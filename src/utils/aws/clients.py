"""AWS clients."""
# Standard Python Libraries
from uuid import uuid4

# Third-Party Libraries
import boto3
from botocore.exceptions import ClientError

# cisagov Libraries
from api.config import (
    COGNITO_ADMIN_GROUP,
    COGNITO_CLIENT_ID,
    COGNTIO_USER_POOL_ID,
    SES_ASSUME_ROLE_ARN,
    logger,
)
from utils.users import get_email_from_user, get_emails_from_users


class AWS:
    """Base AWS Class."""

    def get_client(self, service):
        """Get client."""
        return boto3.client(service_name=service)


class Cognito(AWS):
    """Cognito."""

    def __init__(self):
        """Init."""
        self.client = self.get_client("cognito-idp")

    def get_user_groups(self, username: str):
        """Get groups for user."""
        return self.client.admin_list_groups_for_user(
            Username=username, UserPoolId=COGNTIO_USER_POOL_ID, Limit=50
        )

    def get_user(self, username, return_email: bool = False):
        """Get user from cognito."""
        user = self.client.admin_get_user(
            UserPoolId=COGNTIO_USER_POOL_ID, Username=username
        )
        if return_email:
            return get_email_from_user(user)
        return user

    def get_admin_users(self, return_emails: bool = False):
        """Get admin users from cognito."""
        users = self.client.list_users_in_group(
            UserPoolId=COGNTIO_USER_POOL_ID, GroupName=COGNITO_ADMIN_GROUP
        )["Users"]

        if return_emails:
            return get_emails_from_users(users)
        return users

    def list_users(self, return_emails: bool = False):
        """List users in cognito."""
        users = self.client.list_users(UserPoolId=COGNTIO_USER_POOL_ID)["Users"]
        if return_emails:
            return get_emails_from_users(users)
        return users

    def disable_user(self, username):
        """Disable user in cognito."""
        return self.client.admin_disable_user(
            UserPoolId=COGNTIO_USER_POOL_ID, Username=username
        )

    def delete_user(self, username):
        """Delete user from cognito."""
        self.disable_user(username)
        return self.client.admin_delete_user(
            UserPoolId=COGNTIO_USER_POOL_ID, Username=username
        )

    def enable_user(self, username):
        """Enable user in cognito."""
        return self.client.admin_enable_user(
            UserPoolId=COGNTIO_USER_POOL_ID, Username=username
        )

    def confirm_user(self, username):
        """Confirm user in cognito."""
        return self.client.admin_confirm_sign_up(
            UserPoolId=COGNTIO_USER_POOL_ID, Username=username
        )

    def add_admin_user(self, username):
        """Add user to admin group."""
        return self.client.admin_add_user_to_group(
            UserPoolId=COGNTIO_USER_POOL_ID,
            Username=username,
            GroupName=COGNITO_ADMIN_GROUP,
        )

    def remove_admin_user(self, username):
        """Remove user from admin group."""
        return self.client.admin_remove_user_from_group(
            UserPoolId=COGNTIO_USER_POOL_ID,
            Username=username,
            GroupName=COGNITO_ADMIN_GROUP,
        )

    def sign_up(self, username, password, email):
        """Sign up user in domain manager."""
        return self.client.sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[{"Name": "email", "Value": email}],
        )

    def authenticate(self, username, password):
        """Authenticate user."""
        return self.client.admin_initiate_auth(
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

    def refresh(self, token):
        """Refresh auth token."""
        return self.client.admin_initiate_auth(
            UserPoolId=COGNTIO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": token},
        )


class STS(AWS):
    """STS."""

    def __init__(self):
        """Init."""
        self.client = self.get_client("sts")

    def assume_role_client(self, service, role_arn):
        """Assume Role via STS."""
        resp = self.client.assume_role(
            RoleArn=role_arn, RoleSessionName=f"{service}_session"
        )

        return boto3.client(
            service,
            aws_access_key_id=resp["Credentials"]["AccessKeyId"],
            aws_secret_access_key=resp["Credentials"]["SecretAccessKey"],
            aws_session_token=resp["Credentials"]["SessionToken"],
        )


class Route53(AWS):
    """Route53."""

    def __init__(self):
        """Init."""
        self.client = self.get_client("route53")

    def create_hosted_zone(self, name):
        """Create hosted zone."""
        return self.client.create_hosted_zone(Name=name, CallerReference=str(uuid4()))

    def delete_hosted_zone(self, hosted_zone_id):
        """Delete hosted zone."""
        return self.client.delete_hosted_zone(Id=hosted_zone_id)

    def list_hosted_zones(self, names_only: bool = False):
        """
        List hosted zones.

        Set names_only to true if only hosted zone names are needed.
        """
        zones = self.client.list_hosted_zones()["HostedZones"]
        if names_only:
            return [hosted_zone.get("Name") for hosted_zone in zones]
        return zones

    def list_resource_record_sets(self, hosted_zone_id):
        """List records."""
        return self.client.list_resource_record_sets(HostedZoneId=hosted_zone_id)


class SES(AWS):
    """SES."""

    def __init__(self):
        """Init."""
        if SES_ASSUME_ROLE_ARN:
            sts = STS()
            self.client = sts.assume_role_client("ses", SES_ASSUME_ROLE_ARN)
        else:
            self.client = self.get_client("ses")

    def send_email(self, source: str, to: list, subject: str, text: str, html: str):
        """Send email via SES."""
        try:
            return self.client.send_email(
                Source=source,
                Destination={
                    "BccAddresses": to,
                },
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": text, "Charset": "UTF-8"},
                        "Html": {"Data": html, "Charset": "UTF-8"},
                    },
                },
            )
        except ClientError as e:
            logger.exception(e)
            return e.response["Error"]


class Cloudfront(AWS):
    """Cloudfront."""

    def __init__(self):
        """Init."""
        self.client = self.get_client("cloudfront")

    def get_distribution(self, distribution_id):
        """Get distribution."""
        return self.client.get_distribution(Id=distribution_id)