"""Email Notifications."""
# Third-Party Libraries
from flask import g, render_template

# cisagov Libraries
from api.manager import UserManager
from utils.aws.ses import send_message

user_manager = UserManager()


class Notification:
    """Manage sending email notifications."""

    def __init__(self, message_type, context):
        """Initialize."""
        self.message_type = message_type
        self.context = context

    def _set_context(self, message_type, context):
        """Set context."""
        return {
            "website_launched": {
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
        # Get user email
        dm_user = user_manager.get(filter_data={"Username": g.username})
        send_to = "".join(
            attribute["Value"]
            for attribute in dm_user["Attributes"]
            if attribute["Name"] == "email"
        )

        # Set Context
        self.context["username"] = g.username
        content = self._set_context(self.message_type, self.context)

        return send_message(
            to=send_to,
            subject=content["subject"],
            text=content["text_content"],
            html=content["html_content"],
        )
