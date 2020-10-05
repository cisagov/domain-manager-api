"""S3 utilities."""
# Standard Python Libraries
import json
import logging
import os

# Third-Party Libraries
import boto3

logger = logging.getLogger(__name__)

HOSTED_ZONE_ID = os.environ.get("HOSTED_ZONE_ID")
CONTENT_SOURCE = os.environ.get("SOURCE_BUCKET")

# Initialize aws clients
s3 = boto3.client("s3")
s3_resource = boto3.resource("s3")
route53 = boto3.client("route53")


def launch_site(website, domain):
    """Launch an active site onto s3."""
    # Name new bucket after its domain
    bucket_name = domain.get("Name")[:-1]
    website_name = website.get("name")
    available_buckets = [
        bucket.get("Name") for bucket in s3.list_buckets().get("Buckets")
    ]

    # Create S3 bucket
    if bucket_name not in available_buckets:
        s3.create_bucket(Bucket=bucket_name)

    # Set waiter
    waiter = s3.get_waiter("bucket_exists")
    waiter.wait(Bucket=bucket_name)

    # Copy contents from source
    source_bucket = s3_resource.Bucket(CONTENT_SOURCE)
    source_keys = [
        obj.key for obj in source_bucket.objects.all() if website_name in obj.key
    ]

    for key in source_keys:
        copy_source = {
            "Bucket": CONTENT_SOURCE,
            "Key": key,
        }
        bucket = s3_resource.Bucket(bucket_name)
        bucket.copy(copy_source, key.replace(f"{website_name}/", ""))

    # Attach bucket policy
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AddPerm",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": "arn:aws:s3:::%s/*" % bucket_name,
            }
        ],
    }

    # Attach policy
    bucket_policy = json.dumps(bucket_policy)
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=bucket_policy,
    )

    # Set waiter
    waiter = s3.get_waiter("object_exists")
    waiter.wait(Bucket=bucket_name, Key="index.html")

    # Launch static site
    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={"IndexDocument": {"Suffix": "index.html"}},
    )

    # Setup DNS
    setup_dns(domain=domain, bucket_name=bucket_name)

    return bucket_name


def delete_site(domain):
    """Delete an active site off s3."""
    bucket_name = domain.get("Name")[:-1]
    bucket = s3_resource.Bucket(bucket_name)

    # delete all objects in bucket
    bucket.objects.all().delete()

    # set waiter
    waiter = s3.get_waiter("object_not_exists")
    waiter.wait(Bucket=bucket_name, Key="index.html")

    # delete bucket
    s3.delete_bucket(Bucket=bucket_name)

    response = delete_dns(domain=domain, bucket_name=bucket_name)
    return response


def setup_dns(domain, bucket_name=None, ip_address=None):
    """Setup a domain's DNS."""
    dns_id = domain.get("Id")
    if ip_address:
        response = route53.change_resource_record_sets(
            HostedZoneId=dns_id,
            ChangeBatch={
                "Comment": ip_address,
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": domain.get("Name")[:-1],
                            "Type": "A",
                            "TTL": 15,
                            "ResourceRecords": [{"Value": ip_address}],
                        },
                    }
                ],
            },
        )
    else:
        response = route53.change_resource_record_sets(
            HostedZoneId=dns_id,
            ChangeBatch={
                "Comment": bucket_name,
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": bucket_name,
                            "Type": "A",
                            "AliasTarget": {
                                "HostedZoneId": HOSTED_ZONE_ID,
                                "EvaluateTargetHealth": False,
                                "DNSName": "s3-website-us-east-1.amazonaws.com",
                            },
                        },
                    }
                ],
            },
        )
    logger.info(response)
    return response


def delete_dns(domain, bucket_name=None, ip_address=None):
    """Setup a domain's DNS."""
    dns_id = domain.get("Id")
    if ip_address:
        response = route53.change_resource_record_sets(
            HostedZoneId=dns_id,
            ChangeBatch={
                "Comment": ip_address,
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": domain.get("Name")[:-1],
                            "Type": "A",
                            "TTL": 15,
                            "ResourceRecords": [{"Value": ip_address}],
                        },
                    }
                ],
            },
        )
    else:
        response = route53.change_resource_record_sets(
            HostedZoneId=dns_id,
            ChangeBatch={
                "Comment": bucket_name,
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": bucket_name,
                            "Type": "A",
                            "AliasTarget": {
                                "HostedZoneId": HOSTED_ZONE_ID,
                                "EvaluateTargetHealth": False,
                                "DNSName": "s3-website-us-east-1.amazonaws.com",
                            },
                        },
                    }
                ],
            },
        )
    logger.info(response)
    return response
