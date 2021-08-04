"""Receive Emails Lambda Function."""
# Standard Python Libraries
import logging

# cisagov Libraries
from api.manager import DomainManager, EmailManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)
domain_manager = DomainManager()
email_manager = EmailManager()


def lambda_handler(event, context):
    """Lambda Handler."""
    incoming = event["Records"][0]["ses"]["mail"]
    target_email = incoming["destination"][0]
    domain = domain_manager.get(filter_data={"name": target_email.split("@")[1]})

    if not domain:
        logger.info(incoming)
        logger.error(f"domain from {target_email} does not exist")
        return

    data = {
        "domain_id": domain["_id"],
        "timestamp": incoming["timestamp"],
        "from_address": incoming["commonHeaders"]["from"],
        "to_address": incoming["commonHeaders"]["to"],
        "subject": incoming["commonHeaders"]["subject"],
        "message": "Not yet available.",
    }
    email_manager.save(data)
    logger.info("success")


if __name__ == "__main__":
    lambda_handler(None, None)
