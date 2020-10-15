"""Create DNS email records from SES."""
import boto3


route53 = boto3.client("route53")
ses = boto3.client("ses")


def list_hosted_zones(names_only=False):
    """
    List hosted zones.

    Set names_only to true if only hosted zone names are needed.
    """
    if not names_only:
        return route53.list_hosted_zones()["HostedZones"]

    return [hosted_zone.get("Name") for hosted_zone in list_hosted_zones()]


def create_email_address(domain_name):
    """Create an admin email address for a specified domain."""
    if f"{domain_name}." not in list_hosted_zones(names_only=True):
        return "Domain's hosted zone does not exist."

    # Get hosted zone ID
    dns_id = "".join(
        hosted_zone.get("Id")
        for hosted_zone in list_hosted_zones()
        if hosted_zone.get("Name") == f"{domain_name}."
    )

    # Generate verification token
    verification_token = ses.verify_domain_identity(Domain=domain_name)[
        "VerificationToken"
    ]

    response = route53.change_resource_record_sets(
        HostedZoneId=dns_id,
        ChangeBatch={
            "Comment": "",
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": f"_amazonses.{domain_name}",
                        "Type": "TXT",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": f'"{verification_token}"'}],
                    },
                }
            ],
        },
    )

    return response
