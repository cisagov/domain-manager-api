"""Check Category Lambda Function."""
# Standard Python Libraries
import json

# Third-Party Libraries
from selenium import webdriver

# cisagov Libraries
from api.manager import DomainManager
from settings import BROWSERLESS_ENDPOINT, logger
from utils.proxies.proxies import get_check_proxies

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
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    for record in event["Records"]:
        payload = json.loads(record["body"])
        print(f"{payload=}")

        domain_name = payload["domain"]
        domain = domain_manager.get(filter_data={"name": domain_name})

        driver = webdriver.Remote(
            command_executor=f"http://{BROWSERLESS_ENDPOINT}/webdriver",
            desired_capabilities=chrome_options.to_capabilities(),
        )
        driver.set_page_load_timeout(60)

        for k, v in get_check_proxies().items():
            try:
                resp = v(driver, domain_name)
                update_submission(k, domain["is_category_submitted"], resp)
                driver.quit()
            except Exception as e:
                driver.quit()
                logger.exception(e)

        print(f"Updating {domain_name} with {domain['is_category_submitted']}")
        domain_manager.update(
            document_id=domain["_id"],
            data={"is_category_submitted": domain["is_category_submitted"]},
        )
