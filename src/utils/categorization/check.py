"""Check categorization utils."""
# cisagov Libraries
from api.config import logger
from api.manager import DomainManager
from utils.categorization.driver import get_driver
from utils.proxies import PROXIES

domain_manager = DomainManager()


def check_category(domain_name):
    """Check category across proxies."""
    domain = domain_manager.get(filter_data={"name": domain_name})

    category_results = []

    for proxy in PROXIES:
        if proxy.get("check_url"):
            category = process(proxy.get("check_category_func"), domain_name)
            data = {
                "proxy": proxy["name"],
                "check_url": proxy.get("check_url"),
                "category": category,
            }
            category_results.append(data)

    if domain:
        for result in category_results:
            existing_result = next(
                filter(
                    lambda x: x["proxy"] == result["proxy"], domain["category_results"]
                ),
                None,
            )
            if existing_result:
                result.update(existing_result)

        domain_manager.update(
            document_id=domain["_id"], data={"category_results": category_results}
        )

    return category_results


def process(proxy_func, domain_name):
    """Check for category against a single proxy."""
    driver = get_driver()
    driver.set_page_load_timeout(60)
    try:
        category = proxy_func(driver, domain_name)
        return category
    except Exception as e:
        logger.exception(e)
        return None
    finally:
        driver.quit()
