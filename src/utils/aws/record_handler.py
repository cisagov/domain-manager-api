"""DNS Record Handler."""
# Third-Party Libraries
import boto3

# cisagov Libraries
from utils.aws.regional_s3_endpoints import (
    REGIONAL_HOSTED_ZONE_ID,
    REGIONAL_WEBSITE_ENDPOINT,
)

route53 = boto3.client("route53")
s3 = boto3.client("s3")


def add_record(hosted_zone_id, record):
    """Create record."""
    return {
        "A": modify_a_record,
        "CNAME": modify_cname_record,
        "MAILGUN": modify_mailgun_record,
        "REDIRECT": modify_redirect_record,
    }[record["record_type"]]("CREATE", hosted_zone_id, record)


def delete_record(hosted_zone_id, record):
    """Delete record."""
    return {
        "A": modify_a_record,
        "CNAME": modify_cname_record,
        "MAILGUN": modify_mailgun_record,
        "REDIRECT": modify_redirect_record,
    }[record["record_type"]]("DELETE", hosted_zone_id, record)


def modify_cname_record(action, hosted_zone_id, record):
    """Modify CNAME record."""
    return route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": record["name"],
                        "Type": "CNAME",
                        "TTL": 30,
                        "ResourceRecords": [{"Value": record["config"]["value"]}],
                    },
                }
            ]
        },
    )


def modify_a_record(action, hosted_zone_id, record):
    """Modify A record."""
    return route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": record["name"],
                        "Type": "A",
                        "TTL": 30,
                        "ResourceRecords": [{"Value": record["config"]["value"]}],
                    },
                }
            ]
        },
    )


def modify_mailgun_record(action, hosted_zone_id, record):
    """Modify mailgun record."""
    return route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": record["name"],
                        "Type": "TXT",
                        "TTL": 30,
                        "ResourceRecords": [
                            {"Value": '"v=spf1 include:mailgun.org ~all"'}
                        ],
                    },
                },
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"{record['key']}.{record['name']}",
                        "Type": "TXT",
                        "TTL": 30,
                        "ResourceRecords": [
                            {"Value": f"\"{record['config']['value']}\""}
                        ],
                    },
                },
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"email.{record['name']}",
                        "Type": "CNAME",
                        "TTL": 30,
                        "ResourceRecords": [{"Value": "mailgun.org"}],
                    },
                },
            ]
        },
    )


def modify_redirect_record(action, hosted_zone_id, record):
    """Modify records for redirects."""
    resp = route53.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": record["name"],
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

    if action == "CREATE":
        s3.create_bucket(ACL="private", Bucket=record["name"])
        s3.put_bucket_website(
            Bucket=record["name"],
            WebsiteConfiguration={
                "RedirectAllRequestsTo": {
                    "HostName": record["config"]["value"],
                    "Protocol": record["config"]["protocol"],
                }
            },
        )

    if action == "DELETE":
        s3.delete_bucket(Bucket=record["name"])

    return resp
