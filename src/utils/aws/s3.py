"""S3 Utils."""
# Third-Party Libraries
import boto3

s3 = boto3.client("s3")


def list_top_level_prefixes(bucket):
    """List top level prefixes in S3 bucket."""
    top_level_prefixes = set()
    paginator = s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=bucket)
    for page in page_iterator:
        for item in page["Contents"]:
            top_level_prefixes.add(item["Key"].split("/")[0])
    return top_level_prefixes
