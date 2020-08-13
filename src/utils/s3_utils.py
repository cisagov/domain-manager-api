"""S3 utilities."""
# Standard Python Libraries
import json
import logging
import os

# Third-Party Libraries
import boto3

logger = logging.getLogger(__name__)

# Initializse S3 clients
s3 = boto3.client("s3")
s3_resource = boto3.resource("s3")

content_source = os.environ.get("SOURCE_BUCKET")


def launch_site(website_name, bucket_name):
    """Launch an active site onto s3."""
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
    source_bucket = s3_resource.Bucket(content_source)
    source_keys = [
        obj.key for obj in source_bucket.objects.all() if website_name in obj.key
    ]

    for key in source_keys:
        copy_source = {
            "Bucket": content_source,
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
        Bucket=bucket_name, Policy=bucket_policy,
    )

    # Set waiter
    waiter = s3.get_waiter("object_exists")
    waiter.wait(Bucket=bucket_name, Key="index.html")

    # Launch static site
    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={"IndexDocument": {"Suffix": "index.html"}},
    )

    return f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com/"


def delete_site(bucket_name):
    """Delete an active site off s3."""
    bucket = s3_resource.Bucket(bucket_name)

    # Delete all objects in bucket
    bucket.objects.all().delete()

    # Set waiter
    waiter = s3.get_waiter("object_not_exists")
    waiter.wait(Bucket=bucket_name, Key="index.html")

    # Delete bucket
    s3.delete_bucket(Bucket=bucket_name)
