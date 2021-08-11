"""Receive Emails Lambda Function."""
# Standard Python Libraries
import email
import json
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


def get_email_payload(content):
    """Get Email payload body."""
    message = email.message_from_string(content)
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/html":
                return part.get_payload(decode=True).decode("ASCII")
    else:
        return message.get_payload(decode=True).decode("ASCII")


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

    incoming = json.loads(event["Records"][0]["Sns"]["Message"])
    target_email = incoming["mail"]["destination"][0]
    domain = domain_manager.get(filter_data={"name": target_email.split("@")[1]})

    if not domain:
        logger.info(incoming)
        logger.error(f"domain from {target_email} does not exist")
        return

    # Parse email body
    content = get_email_payload(incoming["content"])

    data = {
        "domain_id": domain["_id"],
        "timestamp": incoming["mail"]["timestamp"],
        "from_address": incoming["mail"]["source"],
        "to_address": target_email,
        "subject": incoming["mail"]["commonHeaders"]["subject"],
        "message": content,
    }
    logger.info(data)

    with app.app_context():
        email_manager.save(data)
        forward_resp = forward_email(data)
        logger.info(forward_resp)

    logger.info("success")


if __name__ == "__main__":
    lambda_handler(None, None)
