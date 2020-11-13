"""Initialize database script."""
# Standard Python Libraries
from bson.binary import Binary
from datetime import datetime
import logging
import json
import os

# Third-Party Libraries
import boto3
import pymongo

from settings import TEMPLATE_BUCKET, TEMPLATE_BUCKET_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
    CONN_STR = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&retryWrites=false".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

else:
    CONN_STR = "mongodb://{}:{}@{}:{}/".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

client = pymongo.MongoClient(CONN_STR)

db = client.domain_management

# Initialize AWS Clients
s3 = boto3.client("s3")
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


def load_s3():
    """Load the latest website data from s3 into the database."""
    db_sites = db.websites

    # List websites within the S3 Repository
    websites = s3.list_objects(Bucket=TEMPLATE_BUCKET)

    # Pull Available websites
    available_prefixes = {i.get("Key").split("/")[0] for i in websites.get("Contents")}

    # Create load data
    s3_load = [
        {"name": i, "url": TEMPLATE_BUCKET_URL + i}
        for i in available_prefixes
        if not db_sites.find_one({"name": i})
    ]

    # Save latest data to the database
    if s3_load != []:
        db_sites.insert_many(s3_load)
        logger.info("Database has been synchronized with S3 data.")


def load_domains():
    """Load the latest domain data from route53 into the database."""
    db_domains = db.domains
    initial_load = route53.list_hosted_zones().get("HostedZones")

    domain_load = []
    for zone in initial_load:
        zone["Name"] = zone["Name"][:-1]
        domain_load.append(zone)

    domain_list = [
        domain
        for domain in domain_load
        if not db_domains.find_one({"Name": domain.get("Name")})
    ]

    # Save latest data to the database
    if domain_list != []:
        db_domains.insert_many(domain_list)
        logger.info("Database has been synchronized with domain data.")


def load_applications():
    """Load dummy application data to the database."""
    db_applications = db.applications

    application_json = load_file("data/applications.json")

    application_data = []
    for application in application_json:
        if not db_applications.find_one({"name": application.get("name")}):
            application["created"] = datetime.utcnow()
            application_data.append(application)

    # Save latest data to the database
    if application_data != []:
        db_applications.insert_many(application_data)
        return logger.info("Application data has been loaded into the database.")


def load_proxy_scripts():
    """Load categorization proxy scripts."""
    db_proxies = db.proxies

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
        if not db_proxies.find_one({"name": name}):
            proxy["created_date"] = datetime.utcnow()

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
        db_proxies.insert_many(proxy_data)
        return logger.info("Proxy data has been loaded into the database.")


def load_categories():
    """Load general categories."""
    db_categories = db.categories

    categories_json = load_file("data/categories.json")

    categories_data = []
    for category in categories_json:
        name = category.get("name")
        if not db_categories.find_one({"name": name}):
            categories_data.append(category)

    # Save latest data to the database
    if categories_data != []:
        db_categories.insert_many(categories_data)
        return logger.info("Category data has been loaded into the database.")


if __name__ == "__main__":
    load_domains()
    load_s3()
    load_applications()
    load_proxy_scripts()
    load_categories()
    logger.info("Database has been initialized.")
