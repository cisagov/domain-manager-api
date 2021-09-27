"""Background tasks."""
# Standard Python Libraries
import logging

# cisagov Libraries
from api.app import app
from utils.notifications import Notification


def email_categorization_updates():
    """Email categorization updates."""
    with app.app_context():
        email = Notification(
            message_type="user_registered",
            context={
                "new_user": "mostafa.abdo",
                "application": "Test Application",
            },
        )
        email.send()
    logging.info("Categorization updates email has been sent.")
