"""Hosted Zone generator."""
# Standard Python Libraries
from datetime import datetime
import time

# Third-Party Libraries
import boto3

route53 = boto3.client("route53")
acm = boto3.client("acm")


def list_hosted_zones(names_only=False):
    """
    List hosted zones.

    Set names_only to true if only hosted zone names are needed.
    """
    if not names_only:
        return route53.list_hosted_zones()["HostedZones"]

    return [hosted_zone.get("Name") for hosted_zone in list_hosted_zones()]


def generate_hosted_zone(domain_name):
    """
    Generate a hosted zone in AWS Route53.

    Return a list of nameservers for the user specified domain
    """
    if f"{domain_name}." in list_hosted_zones(names_only=True):
        hosted_zone_id = "".join(
            hosted_zone.get("Id")
            for hosted_zone in list_hosted_zones()
            if hosted_zone.get("Name") == f"{domain_name}."
        )
        hosted_zone = route53.get_hosted_zone(Id=hosted_zone_id)
        return hosted_zone["DelegationSet"]["NameServers"]

    # used as unique identifier generation
    # every hosted zone must have unique identifer
    unique_identifier = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")

    hosted_zone = route53.create_hosted_zone(
        Name=domain_name,
        CallerReference=unique_identifier,
    )

    # generate ssl certificates
    arn_certificate = generate_ssl_certs(domain_name)
    time.sleep(5)
    records = acm.describe_certificate(CertificateArn=arn_certificate)
    resource_records = [
        record["ResourceRecord"]
        for record in records["Certificate"]["DomainValidationOptions"]
    ]
    resource_records
    return hosted_zone["DelegationSet"]["NameServers"]


def delete_hosted_zone(domain_name):
    """Delete a hosted zone from Route53."""
    if f"{domain_name}." in list_hosted_zones(names_only=True):
        # delete hosted zone
        hosted_zone_id = "".join(
            hosted_zone.get("Id")
            for hosted_zone in list_hosted_zones()
            if hosted_zone.get("Name") == f"{domain_name}."
        )
        route53.delete_hosted_zone(Id=hosted_zone_id)

        # delete ssl certificate
        arn_certificate = "".join(
            certificate.get("CertificateArn")
            for certificate in acm.list_certificates()["CertificateSummaryList"]
            if domain_name == certificate.get("DomainName")
        )
        acm.delete_certificate(CertificateArn=arn_certificate)
        return "hosted zone has been deleted."
    return "hosted zone does not exist"


def generate_ssl_certs(domain_name):
    """Request an SSL certificate using AWS Certificate Manager."""
    certificates = [
        certificate.get("DomainName")
        for certificate in acm.list_certificates()["CertificateSummaryList"]
    ]

    if domain_name not in certificates:
        response = acm.request_certificate(
            DomainName=domain_name,
            ValidationMethod="DNS",
            SubjectAlternativeNames=[
                domain_name,
                f"www.{domain_name}",
            ],
            DomainValidationOptions=[
                {"DomainName": domain_name, "ValidationDomain": domain_name},
            ],
            Options={"CertificateTransparencyLoggingPreference": "DISABLED"},
        )
        return response["CertificateArn"]
