"""Email Notifications."""
# Third-Party Libraries
from flask import g, render_template, render_template_string

# cisagov Libraries
from api.config import SMTP_FROM, logger
from api.manager import UserManager
from api.settings import Settings
from utils.aws.clients import SES, Cognito
from utils.users import get_users_in_group

user_manager = UserManager()
cognito = Cognito()
settings = Settings()


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
            "email_received": {
                "send_to": "ForwardEmail",
                "subject": f"[Domain Manager] FW: {context.get('subject', '')}",
                "text_content": render_template_string(
                    "emails/email_received.html", **context
                ),
                "html_content": render_template(
                    "emails/email_received.html", **context
                ),
            },
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
            "user_registered": {
                "send_to": "UserRegistered",
                "subject": "[Domain Manager] A New User Has Registered",
                "text_content": render_template_string(
                    "emails/new_user_registered.html", **context
                ),
                "html_content": render_template(
                    "emails/new_user_registered.html", **context
                ),
            },
            "user_confirmed": {
                "send_to": "Specified",
                "subject": "[Domain Manager] Your Account Has Been Confirmed",
                "text_content": render_template_string(
                    "emails/user_confirmed.html", **context
                ),
                "html_content": render_template(
                    "emails/user_confirmed.html", **context
                ),
            },
            "categorization_request": {
                "send_to": "CategorizationEmail",
                "subject": "[Domain Manager] Categorization Request",
                "text_content": render_template_string(
                    "emails/categorization_request.html", **context
                ),
                "html_content": render_template(
                    "emails/categorization_request.html", **context
                ),
            },
            "categorization_updates": {
                "send_to": "CategorizationEmail",
                "subject": "[Domain Manager] Categorization Updates",
                "text_content": render_template_string(
                    "emails/categorization_updates.html", **context
                ),
                "html_content": render_template(
                    "emails/categorization_updates.html", **context
                ),
            },
        }.get(message_type)

    def get_to_addresses(self, content):
        """Get email addresses to send to."""
        addresses = []
        logger.info(content["send_to"])
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
        elif content["send_to"] == "UserRegistered":
            addresses.append(settings.to_dict()["USER_NOTIFICATION_EMAIL"])
        elif content["send_to"] == "Specified":
            email = self.context.get("UserEmail", "")
            addresses.append(email)
        elif content["send_to"] == "ForwardEmail":
            addresses.append(settings.to_dict()["SES_FORWARD_EMAIL"])
        elif content["send_to"] == "CategorizationEmail":
            addresses.append(settings.to_dict()["CATEGORIZATION_EMAIL"])
        return addresses

    def send(self):
        """Send Email."""
        ses = SES(assume_role=True)
        # Set Context
        self.context["username"] = g.get("username", "bot")
        content = self._set_context(self.message_type, self.context)

        addresses = self.get_to_addresses(content)

        logger.info(f"Sending template {self.message_type} to {addresses}")
        if len(addresses) > 0 and addresses[0] is not None:
            return ses.send_email(
                source=SMTP_FROM,
                to=addresses,
                subject=content["subject"],
                text=content["text_content"],
                html=content["html_content"],
            )
