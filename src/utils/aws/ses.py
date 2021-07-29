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
    dkim_token_1: str,
    dkim_token_2: str,
    dkim_token_3: str,
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
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"{dkim_token_1}._domainkey.{domain_name}",
                        "Type": "CNAME",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": f"{dkim_token_1}.amazonses.com"}],
                    },
                },
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"{dkim_token_2}._domainkey.{domain_name}",
                        "Type": "CNAME",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": f"{dkim_token_2}.amazonses.com"}],
                    },
                },
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": f"{dkim_token_3}._domainkey.{domain_name}",
                        "Type": "CNAME",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": f"{dkim_token_3}.amazonses.com"}],
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

    # Generate CNAME record DKIM tokens
    dkim_token_1, dkim_token_2, dkim_token_3 = ses.verify_domain_dkim(
        Domain=domain_name
    )["DkimTokens"]

    response = manage_resource_records(
        domain_name=domain_name,
        action="UPSERT",
        verification_token=verification_token,
        dkim_token_1=dkim_token_1,
        dkim_token_2=dkim_token_2,
        dkim_token_3=dkim_token_3,
    )

    return response


def disable_email_receiving(domain_name: str):
    """Disable receiving emails for a specified domain."""
    verification_token = ses.get_identity_verification_attributes(
        Identities=[domain_name]
    )["VerificationAttributes"][domain_name]["VerificationToken"]
    dkim_token_1, dkim_token_2, dkim_token_3 = ses.get_identity_dkim_attributes(
        Identities=[domain_name]
    )["DkimAttributes"][domain_name]["DkimTokens"]

    manage_resource_records(
        domain_name=domain_name,
        action="DELETE",
        verification_token=verification_token,
        dkim_token_1=dkim_token_1,
        dkim_token_2=dkim_token_2,
        dkim_token_3=dkim_token_3,
    )

    return ses.delete_identity(Identity=domain_name)
