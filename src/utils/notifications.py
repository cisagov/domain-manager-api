"""Email Notifications."""
# Third-Party Libraries
import boto3
from botocore.exceptions import ClientError
from flask import g, render_template, render_template_string

# cisagov Libraries
from api.manager import UserManager
from settings import APP_ENV, APP_NAME, SES_ASSUME_ROLE_ARN, SMTP_FROM, logger
from utils.aws import cognito, sts
from utils.users import get_users_in_group

if SES_ASSUME_ROLE_ARN:
    ses = sts.assume_role_client("ses", SES_ASSUME_ROLE_ARN)
else:
    ses = boto3.client("ses")

user_manager = UserManager()


class Notification:
    """Manage sending email notifications."""

    def __init__(self, message_type, context, application_id=None):
        """Initialize."""
        self.message_type = message_type
        self.context = context
        self.application_id = application_id

    def _set_context(self, message_type, context):
        """
        Set context.

        Required fields when creating context-
        [send_to] - User,Admins,All,Application
        [subject] - Subject of email
        [text_content] - Text content of email
        [html_content] - Html content of email
        """
        return {
            "test": {
                "send_to": "User",
                "subject": "[Domain Manager] Test Event",
                "text_content": render_template_string("emails/test.html", **context),
                "html_content": render_template("emails/test.html", **context),
            },
            "website_launched": {
                "send_to": "User",
                "subject": "[Domain Manager] Your Website has been Launched",
                "text_content": render_template_string(
                    "emails/website_launched.html", **context
                ),
                "html_content": render_template(
                    "emails/website_launched.html", **context
                ),
            },
        }.get(message_type)

    def get_to_addresses(self, content):
        """Get email addresses to send to."""
        addresses = []
        if self.application_id:
            addresses.extend(
                get_users_in_group(
                    application_id=self.application_id, return_emails=True
                )
            )
        elif content["send_to"] == "User":
            addresses.append(cognito.get_user(g.username, return_email=True))
        elif content["send_to"] == "Admins":
            addresses.extend(cognito.get_admin_users(return_emails=True))
        elif content["send_to"] == "All":
            addresses.extend(cognito.list_users(return_emails=True))
        return addresses

    def send(self):
        """Send Email."""
        # Set Context
        self.context["username"] = g.get("username")
        content = self._set_context(self.message_type, self.context)
        addresses = self.get_to_addresses(content)

        logger.info(f"Sending template {self.message_type} to {addresses}")

        return send_message(
            to=addresses,
            subject=content["subject"],
            text=content["text_content"],
            html=content["html_content"],
        )


def send_message(to: list, subject: str, text: str, html: str):
    """Send message via SES."""
    resp = {}
    try:
        resp = ses.send_email(
            Source=SMTP_FROM,
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
            Tags=[
                {"Name": "app", "Value": APP_NAME},
                {"Name": "environment", "Value": APP_ENV},
            ],
        )
    except ClientError as e:
        return e.response["Error"]

    return resp
