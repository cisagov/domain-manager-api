"""Check Category Lambda Function."""
# Standard Python Libraries
import json

# cisagov Libraries
from api.manager import DomainManager, ProxyManager
from settings import logger
from utils.proxies.proxies import get_check_proxies

domain_manager = DomainManager()
proxy_manager = ProxyManager()


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
        print(f"{payload=}")

        domain_name = payload["domain"]
        domain = domain_manager.get(filter_data={"name": domain_name})

        for k, v in get_check_proxies().items():
            try:
                resp = v(domain_name)
                update_submission(k, domain["is_category_submitted"], resp)
            except Exception as e:
                logger.exception(e)

        domain_manager.update(
            document_id=domain["_id"],
            data={"is_category_submitted": domain["is_category_submitted"]},
        )
