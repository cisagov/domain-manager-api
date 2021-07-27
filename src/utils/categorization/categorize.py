"""Categorization utils."""
# cisagov Libraries
from api.config import TWO_CAPTCHA_API_KEY, logger
from api.manager import DomainManager
from utils.categorization.driver import get_driver
from utils.proxies import CATEGORIES, PROXIES

domain_manager = DomainManager()


def categorize(requested_category, domain_name):
    """Categorize a domain across proxies."""
    domain = domain_manager.get(filter_data={"name": domain_name})

    category = CATEGORIES.get(requested_category.title())

    category_results = []

    for proxy in PROXIES:
        if proxy.get("categorize_url"):
            proxy_category = category.get(proxy["name"])
            categorize_response = process(
                proxy_func=proxy.get("categorize_func"),
                proxy_category=proxy_category,
                domain_name=domain_name,
            )
            data = {
                "proxy": proxy["name"],
                "submitted_category": proxy_category,
                "is_submitted": categorize_response,
                "categorize_url": proxy.get("categorize_url"),
            }
            category_results.append(data)

    if domain:
        domain_manager.update(
            document_id=domain["_id"],
            data={"category_results": category_results},
        )

    return category_results


def process(proxy_func, proxy_category, domain_name):
    """Categorize domain against a proxy."""
    driver = get_driver()
    driver.set_page_load_timeout(60)
    try:
        proxy_func(
            driver=driver,
            domain=domain_name,
            category=proxy_category,
            two_captcha_api_key=TWO_CAPTCHA_API_KEY,
        )
        return True
    except Exception as e:
        logger.exception(e)
        return False
    finally:
        driver.quit()
