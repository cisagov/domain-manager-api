"""DNS Record Handler."""
# Third-Party Libraries
import boto3

route53 = boto3.client("route53")


def add_record(hosted_zone_id, record):
    """Create record."""
    return {
        "A": modify_a_record,
        "CNAME": modify_cname_record,
        "MAILGUN": modify_mailgun_record,
    }[record["record_type"]]("CREATE", hosted_zone_id, record)


def delete_record(hosted_zone_id, record):
    """Delete record."""
    return {
        "A": modify_a_record,
        "CNAME": modify_cname_record,
        "MAILGUN": modify_mailgun_record,
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
                        "Name": record["record_name"],
                        "Type": "CNAME",
                        "ResourceRecords": [{"Value": record["record_value"]}],
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
                        "Name": record["record_name"],
                        "Type": "A",
                        "ResourceRecords": [{"Value": record["record_value"]}],
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
                        "Name": record["record_name"],
                        "Type": "TXT",
                        "ResourceRecords": [
                            {"Value": "v=spf1 include:mailgun.org ~all"}
                        ],
                    },
                },
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"mx._domainkey.{record['record_name']}",
                        "Type": "TXT",
                        "ResourceRecords": [{"Value": record["record_value"]}],
                    },
                },
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"email.{record['record_name']}",
                        "Type": "CNAME",
                        "ResourceRecords": [{"Value": "mailgun.org"}],
                    },
                },
            ]
        },
    )
