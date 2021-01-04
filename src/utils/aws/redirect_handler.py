"""Redirect AWS Logic."""
# Third-Party Libraries
import boto3

# cisagov Libraries
from api.manager import WebsiteManager
from utils.aws.regional_s3_endpoints import (
    REGIONAL_HOSTED_ZONE_ID,
    REGIONAL_WEBSITE_ENDPOINT,
)

website_manager = WebsiteManager()

s3 = boto3.client("s3")
route53 = boto3.client("route53")


def get_website_redirect_info(website_id, subdomain):
    """Get s3 website info."""
    website = website_manager.get(document_id=website_id)
    domain = website["name"]
    subdomain = f"{subdomain}.{domain}"
    hosted_zone_id = website["route53"]["id"]
    return domain, subdomain, hosted_zone_id


def setup_redirect(website_id, subdomain, redirect_url):
    """Create s3 bucket and route53 records for redirecting traffic."""
    # Get website
    domain, subdomain, hosted_zone_id = get_website_redirect_info(website_id, subdomain)

    # Create S3 bucket with subdomain name.
    s3.create_bucket(
        ACL="private",
        Bucket=subdomain,
    )

    # Modify S3 bucket to redirect requests.
    s3.put_bucket_website(
        Bucket=subdomain,
        WebsiteConfiguration={"RedirectAllRequestsTo": {"HostName": redirect_url}},
    )

    # Create Route53 Record to point at s3 website bucket.
    route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": subdomain,
                        "Type": "A",
                        "AliasTarget": {
                            "DNSName": REGIONAL_WEBSITE_ENDPOINT,
                            "EvaluateTargetHealth": False,
                            "HostedZoneId": REGIONAL_HOSTED_ZONE_ID,
                        },
                    },
                }
            ]
        },
    )


def delete_redirect(website_id, subdomain):
    """Delete s3 bucket and route53 records for redirects."""
    domain, subdomain, hosted_zone_id = get_website_redirect_info(website_id, subdomain)
    route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": "DELETE",
                    "ResourceRecordSet": {
                        "Name": subdomain,
                        "Type": "A",
                        "AliasTarget": {
                            "DNSName": REGIONAL_WEBSITE_ENDPOINT,
                            "EvaluateTargetHealth": False,
                            "HostedZoneId": REGIONAL_HOSTED_ZONE_ID,
                        },
                    },
                }
            ]
        },
    )
    s3.delete_bucket(Bucket=subdomain)


def modify_redirect(website_id, subdomain, redirect_url):
    """Change redirect."""
    # Modify S3 bucket to redirect requests.
    domain, subdomain, hosted_zone_id = get_website_redirect_info(website_id, subdomain)
    s3.put_bucket_website(
        Bucket=subdomain,
        WebsiteConfiguration={"RedirectAllRequestsTo": {"HostName": redirect_url}},
    )
