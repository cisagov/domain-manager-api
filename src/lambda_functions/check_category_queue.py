"""Queue Check Category Lambda Function."""
# Standard Python Libraries
import json

# Third-Party Libraries
import boto3

# cisagov Libraries
from api.manager import DomainManager
from settings import SQS_CHECK_CATEGORY_URL, logger
from utils.proxies.proxies import get_check_proxies

sqs = boto3.client("sqs")

domain_manager = DomainManager()


def handler(event, context):
    """Write check category events to queue."""
    domains = domain_manager.all()

    for domain in domains:
        if not domain.get("is_category_submitted", None):
            logger.info(
                f"website {domain['name']} has not yet been submitted for categorization"
            )
            continue

        for proxy in get_check_proxies().keys():
            sqs.send_message(
                QueueUrl=SQS_CHECK_CATEGORY_URL,
                MessageBody=json.dumps({"domain": domain, "proxy": proxy}),
            )
