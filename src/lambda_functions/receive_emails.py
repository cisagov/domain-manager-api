"""Receive Emails Lambda Function."""
# Standard Python Libraries
import logging

# cisagov Libraries
from api.manager import DomainManager

logger = logging.getLogger()
logger.setLevel(logging.INFO)
domain_manager = DomainManager()


def lambda_handler(event, context):
    """Lambda Handler."""
    incoming = event["Records"][0]["ses"]["mail"]
    domain = domain_manager.get(filter_data={"name": incoming["destination"][0]})

    if not domain:
        logger.error("domain does not exist")
        return

    data = {
        "domain_id": domain["_id"],
        "timestamp": incoming["timestamp"],
        "from": incoming["commonHeaders"]["from"],
        "to": domain["name"],
        "subject": incoming["commonHeaders"]["subject"],
    }
    print("domain: ", domain)
    print("context: ", context)
    print("data: ", data)
    logger.info("success")


if __name__ == "__main__":
    lambda_handler(None, None)
