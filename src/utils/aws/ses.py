"""Create DNS email records from SES."""
# Third-Party Libraries
import boto3

route53 = boto3.client("route53")
ses = boto3.client("ses")


def list_hosted_zones(names_only: bool = False):
    """
    List hosted zones.

    Set names_only to true if only hosted zone names are needed.
    """
    if not names_only:
        return route53.list_hosted_zones()["HostedZones"]

    return [hosted_zone.get("Name") for hosted_zone in list_hosted_zones()]


def manage_resource_records(
    domain_name: str,
    action: str,
    verification_token: str,
):
    """Manage Route53 Records."""
    if f"{domain_name}." not in list_hosted_zones(names_only=True):
        return "Domain's hosted zone does not exist."

    dns_id = "".join(
        hosted_zone.get("Id")
        for hosted_zone in list_hosted_zones()
        if hosted_zone.get("Name") == f"{domain_name}."
    )

    return route53.change_resource_record_sets(
        HostedZoneId=dns_id,
        ChangeBatch={
            "Comment": "",
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"_amazonses.{domain_name}",
                        "Type": "TXT",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": f'"{verification_token}"'}],
                    },
                },
            ],
        },
    )


def enable_email_receiving(domain_name: str):
    """Enable receiving emails for a specified domain."""
    # Generate verification token
    verification_token = ses.verify_domain_identity(Domain=domain_name)[
        "VerificationToken"
    ]

    response = manage_resource_records(
        domain_name=domain_name,
        action="UPSERT",
        verification_token=verification_token,
    )

    return response


def disable_email_receiving(domain_name: str):
    """Disable receiving emails for a specified domain."""
    verification_token = ses.get_identity_verification_attributes(
        Identities=[domain_name]
    )["VerificationAttributes"][domain_name]["VerificationToken"]

    manage_resource_records(
        domain_name=domain_name,
        action="DELETE",
        verification_token=verification_token,
    )

    return ses.delete_identity(Identity=domain_name)
