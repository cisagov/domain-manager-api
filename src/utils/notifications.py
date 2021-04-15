"""Email Notifications."""
# Third-Party Libraries
import boto3
from botocore.exceptions import ClientError
from flask import g, render_template

# cisagov Libraries
from api.manager import UserManager
from settings import APP_ENV, APP_NAME, SES_ASSUME_ROLE_ARN, SMTP_FROM
from utils.aws import sts

if SES_ASSUME_ROLE_ARN:
    ses = sts.assume_role_client("ses", SES_ASSUME_ROLE_ARN)
else:
    ses = boto3.client("ses")

user_manager = UserManager()


class Notification:
    """Manage sending email notifications."""

    def __init__(
        self,
        message_type,
        context,
        send_to_admins=False,
        send_to_group=False,
    ):
        """Initialize."""
        self.message_type = message_type
        self.context = context
        self.send_to_admins = send_to_admins
        self.send_to_group = send_to_group

    def _set_context(self, message_type, context):
        """Set context."""
        send_to = []
        # Get authenticated user email
        context["username"] = g.get("username")
        auth_user = user_manager.get(filter_data={"Username": g.get("username")})
        send_to.append(
            "".join(
                attribute["Value"]
                for attribute in auth_user["Attributes"]
                if attribute["Name"] == "email"
            )
        )

        if self.send_to_group:
            group_users = user_manager.all(
                params={"Groups": auth_user.get("Groups", [])}
            )
            for user in group_users:
                send_to.append(
                    "".join(
                        attribute["Value"]
                        for attribute in user["Attributes"]
                        if attribute["Name"] == "email"
                    )
                )

        send_to = list(filter(None, send_to))

        return {
            "website_launched": {
                "send_to": send_to,
                "subject": "[Domain Manager] Your Website has been Launched",
                "text_content": render_template(
                    "emails/website_launched.txt", **context
                ),
                "html_content": render_template(
                    "emails/website_launched.html", **context
                ),
            }
        }.get(message_type)

    def send(self):
        """Send Email."""
        # Set Context
        content = self._set_context(self.message_type, self.context)

        return send_message(
            to=content["send_to"],
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
                "ToAddresses": to,
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
