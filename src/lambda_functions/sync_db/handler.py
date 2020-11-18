"""Synchronize database script."""
# Standard Python Libraries
import logging
import os

# Third-Party Libraries
import boto3
import pymongo

from settings import TEMPLATE_BUCKET, TEMPLATE_BUCKET_URL

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


def load_websites():
    """Load the latest website data from route53 and s3 into the database."""
    db_websites = db.websites
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
    websites = s3.list_objects(Bucket=TEMPLATE_BUCKET)

    # load available websites if available
    data_load = []
    for domain in domain_load:
        if not db_websites.find_one({"name": domain.get("name")}):
            domain_name = domain.get("name")
            available_sites = [
                website.get("Key").split(domain_name)[0]
                for website in websites.get("Contents")
                if domain_name in website.get("Key")
            ]
            if available_sites:
                domain["s3_url"] = (
                    TEMPLATE_BUCKET_URL + available_sites[0] + domain_name
                )
            data_load.append(domain)

    # save latest data to the database
    if data_load != []:
        db_websites.insert_many(data_load)
        logger.info("Database has been synchronized with domain data.")


def lambda_handler(event, context):
    """Lambda handler."""
    load_websites()


if __name__ == "__main__":
    load_websites()
