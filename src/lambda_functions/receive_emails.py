"""Receive Emails Lambda Function."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from botocore.exceptions import ClientError

# cisagov Libraries
from api.main import app
from api.manager import DomainManager, EmailManager
from utils.notifications import Notification

logger = logging.getLogger()
logger.setLevel(logging.INFO)

domain_manager = DomainManager()
email_manager = EmailManager()


def forward_email(message):
    """Forward a Received Email to specified email address."""
    try:
        email = Notification(
            message_type="email_received",
            context=message,
        )
        email.send()
    except ClientError as e:
        logger.error(e.response["Error"]["Message"])

    return {"success": "email has been forwarded."}


def lambda_handler(event, context):
    """Lambda Handler."""
    logger.info(event)

    target_email = event["mail"]["destination"][0]
    domain = domain_manager.get(filter_data={"name": target_email.split("@")[1]})

    if not domain:
        logger.info(event)
        logger.error(f"domain from {target_email} does not exist")
        return

    data = {
        "domain_id": domain["_id"],
        "timestamp": event["mail"]["timestamp"],
        "from_address": event["mail"]["source"],
        "to_address": target_email,
        "subject": event["mail"]["commonHeaders"]["subject"],
        "message": event["content"].split("Content-Type: text/plain")[1],
    }
    logger.info(data)

    with app.app_context():
        email_manager.save(data)
        forward_resp = forward_email(data)
        logger.info(forward_resp)

    logger.info("success")


if __name__ == "__main__":
    lambda_handler(None, None)
