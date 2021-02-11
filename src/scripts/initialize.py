"""Initialize database script."""
# Standard Python Libraries
import json
import os

# Third-Party Libraries
import boto3
from bson.binary import Binary

# cisagov Libraries
from api.manager import ApplicationManager, DomainManager, ProxyManager
from settings import WEBSITE_BUCKET, WEBSITE_BUCKET_URL, logger
from utils.aws.s3 import list_top_level_prefixes

application_manager = ApplicationManager()
domain_manager = DomainManager()
proxy_manager = ProxyManager()


# Initialize AWS Clients
route53 = boto3.client("route53")


def load_file(data_file, data_type="json"):
    """Load json files."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, data_file)
    with open(data_file, "rb") as f:
        if data_type == "script":
            data = f.read()
        else:
            data = json.load(f)
    return data


def load_domains():
    """Load the latest domain data from route53 and s3 into the database."""
    initial_load = route53.list_hosted_zones().get("HostedZones")

    domain_load = []
    for zone in initial_load:
        hosted_zone = {
            "name": zone["Name"][:-1],
            "route53": {"id": zone["Id"]},
        }
        hosted_zone["is_active"] = False
        domain_load.append(hosted_zone)

    # list domains within the S3 Repository
    domains = list_top_level_prefixes(WEBSITE_BUCKET)

    # load available domains if available
    data_load = []
    for domain in domain_load:
        if not domain_manager.get(filter_data={"name": domain.get("name")}):
            domain_name = domain.get("name")
            if domain_name in domains:
                domain["s3_url"] = f"{WEBSITE_BUCKET_URL}/{domain_name}"
            data_load.append(domain)

    # save latest data to the database
    if data_load != []:
        domain_manager.save_many(data_load)
        logger.info("Database has been synchronized with domain data.")


def load_applications():
    """Load dummy application data to the database."""
    application_json = load_file("data/applications.json")

    application_data = []
    for application in application_json:
        if not application_manager.get(filter_data={"name": application.get("name")}):
            application_data.append(application)

    # Save latest data to the database
    if application_data != []:
        application_manager.save_many(data=application_data)
        logger.info("Application data has been loaded into the database.")


def load_proxy_scripts():
    """Load categorization proxy scripts."""
    proxy_json = load_file("data/proxies.json")

    # load scripts
    trustedsource_script = load_file(
        "data/proxies/trusted_source.py", data_type="script"
    )
    bluecoat_script = load_file("data/proxies/bluecoat.py", data_type="script")
    fortiguard_script = load_file("data/proxies/fortiguard.py", data_type="script")
    palo_alto_script = load_file("data/proxies/palo_alto.py", data_type="script")
    trustedsource_script = load_file(
        "data/proxies/trusted_source.py", data_type="script"
    )
    trendmicro_script = load_file("data/proxies/trendmicro.py", data_type="script")

    proxy_data = []
    for proxy in proxy_json:
        name = proxy.get("name")
        if not proxy_manager.get(filter_data={"name": name}):
            if name == "Trusted Source":
                proxy["script"] = Binary(trustedsource_script)
            elif name == "Blue Coat":
                proxy["script"] = Binary(bluecoat_script)
            elif name == "Fortiguard":
                proxy["script"] = Binary(fortiguard_script)
            elif name == "Palo Alto Networks":
                proxy["script"] = Binary(palo_alto_script)
            elif name == "Trend Micro":
                proxy["script"] = Binary(trendmicro_script)

            proxy_data.append(proxy)

    # Save latest data to the database
    if proxy_data != []:
        proxy_manager.save_many(data=proxy_data)
        logger.info("Proxy data has been loaded into the database.")


if __name__ == "__main__":
    load_domains()
    load_applications()
    load_proxy_scripts()
    logger.info("Database has been initialized.")
