"""Synchronize database script."""
# Standard Python Libraries
import logging

# Third-Party Libraries
import boto3

# cisagov Libraries
from api.manager import WebsiteManager
from settings import WEBSITE_BUCKET, WEBSITE_BUCKET_URL
from utils.aws.s3 import list_top_level_prefixes

logger = logging.getLogger()

website_manager = WebsiteManager()

# Initialize AWS Clients
s3 = boto3.client("s3")
route53 = boto3.client("route53")


def load_websites():
    """Load the latest website data from route53 and s3 into the database."""
    initial_load = route53.list_hosted_zones().get("HostedZones")

    domain_load = []
    for zone in initial_load:
        hosted_zone = {
            "name": zone["Name"][:-1],
            "route53": {"id": zone["Id"]},
        }
        hosted_zone["is_active"] = False
        domain_load.append(hosted_zone)

    # list websites within the S3 Repository
    websites = list_top_level_prefixes(WEBSITE_BUCKET)

    # load available websites if available
    data_load = []
    for domain in domain_load:
        if not website_manager.get(filter_data={"name": domain.get("name")}):
            domain_name = domain.get("name")
            if domain_name in websites:
                domain["s3_url"] = f"{WEBSITE_BUCKET_URL}{domain_name}"
            data_load.append(domain)

    # save latest data to the database
    if data_load != []:
        website_manager.save_many(data=data_load)
        logger.info("Database has been synchronized with domain data.")


def lambda_handler(event, context):
    """Lambda handler."""
    load_websites()


if __name__ == "__main__":
    load_websites()
