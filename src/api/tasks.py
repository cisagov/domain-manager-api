"""Background tasks."""
# Standard Python Libraries
import logging

# cisagov Libraries
from api.app import app
from api.manager import CategorizationManager
from utils.notifications import Notification

categorization_manager = CategorizationManager()


def email_categorization_updates():
    """Email categorization updates."""
    categorizations = categorization_manager.all(
        params={"status": {"$in": ["new", "recategorize", "submitted"]}},
        fields=["domain_name", "status"],
    )

    categorize_domains = list(
        {
            proxy["domain_name"]
            for proxy in categorizations
            if proxy["status"] in ["new", "recategorize"]
        }
    )
    verify_domains = list(
        {
            proxy["domain_name"]
            for proxy in categorizations
            if proxy["status"] == "submitted"
        }
    )
    if verify_domains:
        with app.app_context():
            email = Notification(
                message_type="categorization_updates",
                context={
                    "categorize_domains": categorize_domains,
                    "verify_domains": verify_domains,
                },
            )
            email.send()
        logging.info("Categorization updates email has been sent.")
