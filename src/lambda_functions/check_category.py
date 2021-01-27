"""Check Category Lambda Function."""
# Standard Python Libraries
import json

# cisagov Libraries
from api.manager import DomainManager
from settings import logger

# from utils.proxies.proxies import get_check_proxy_func


domain_manager = DomainManager()


def update_submission(query, dicts, response):
    """Search through existing submissions and check as categorized."""
    next(
        item.update({"is_categorized": True, "category": response})
        for item in dicts
        if item["name"] == query
    )
    if not any(item["name"] == query for item in dicts):
        dicts.append({"name": query, "is_categorized": True, "category": response})


def handler(event, context):
    """Handle check category SQS event."""
    for record in event["Records"]:
        payload = json.loads(record["body"])
        # proxy_func = get_check_proxy_func(payload["proxy"])
        # domain_name = payload["domain"]
        # domain = domain_manager.get(filter_data={"name": domain_name})

        logger.info(payload)
