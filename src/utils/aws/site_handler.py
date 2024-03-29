"""AWS site gneeration utilities."""
# Standard Python Libraries
from datetime import datetime
import time

# Third-Party Libraries
import boto3
import botocore
import dns.resolver

# cisagov Libraries
from api.config import WEBSITE_BUCKET_URL, logger
from api.manager import DomainManager
from utils.notifications import Notification

domain_manager = DomainManager()

# Initialize aws clients
acm = boto3.client("acm")
cloudfront = boto3.client("cloudfront")
route53 = boto3.client("route53")


def launch_domain(domain):
    """Launch Domain."""
    try:
        domain_manager.update(
            document_id=domain["_id"],
            data={
                "is_available": False,
                "is_launching": True,
            },
        )

        resp = launch_site(domain)

        data = {
            "is_active": True,
            "is_available": True,
            "is_launching": False,
        }
        data.update(resp)
        domain_manager.update(
            document_id=domain["_id"],
            data=data,
        )

        email = Notification(
            message_type="website_launched", context={"domain_name": domain["name"]}
        )
        email.send()
    except Exception as e:
        logger.exception(e)
        domain_manager.update(
            document_id=domain["_id"],
            data={
                "is_available": True,
                "is_launching": False,
            },
        )


def unlaunch_domain(domain):
    """Unlaunch domain."""
    try:
        domain_manager.update(
            document_id=domain["_id"],
            data={
                "is_available": False,
                "is_delaunching": True,
            },
        )
        delete_site(domain)
        domain_manager.update(
            document_id=domain["_id"],
            data={
                "is_active": False,
                "is_available": True,
                "is_delaunching": False,
            },
        )

        domain_manager.remove(
            document_id=domain["_id"],
            data={"acm": "", "cloudfront": ""},
        )
    except Exception as e:
        logger.exception(e)
        domain_manager.update(
            document_id=domain["_id"],
            data={
                "is_available": True,
                "is_delaunching": False,
            },
        )


def launch_site(domain):
    """Launch an active site onto s3."""
    # Verify that site is owned.
    verify_hosted_zone(domain)

    # generate ssl certs and return certificate ARN
    certificate_arn = generate_ssl_certs(domain=domain)

    # setup cloudfront
    distribution_id, distribution_endpoint = setup_cloudfront(
        domain=domain, certificate_arn=certificate_arn
    )

    # setup DNS
    setup_dns(domain=domain, endpoint=distribution_endpoint)

    # wait for cloudfront to be deployed
    waiter = cloudfront.get_waiter("distribution_deployed")
    waiter.wait(Id=distribution_id)

    return {
        "cloudfront": {
            "id": distribution_id,
            "distribution_endpoint": distribution_endpoint,
        },
        "acm": {"certificate_arn": certificate_arn},
    }


def delete_site(domain):
    """Delete an active site off s3."""
    cloudfront_metadata = domain["cloudfront"]

    logger.info("Deleting clodufront distribution")
    delete_cloudfront(cloudfront_metadata)

    logger.info("Deleting ssl certificates from acm.")
    delete_ssl_certs(domain)

    logger.info("Deleting dns records from route53.")
    delete_dns(domain=domain, endpoint=cloudfront_metadata["distribution_endpoint"])


def delete_cloudfront(cloudfront_metadata):
    """Delete cloudfront distribution if it exists."""
    try:
        distribution = cloudfront.get_distribution(Id=cloudfront_metadata["id"])
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchDistribution":
            return
        else:
            raise error

    # disable cloudfront distribution
    distribution["Distribution"]["DistributionConfig"]["Enabled"] = False
    logger.info("Disabling cloudfront distribution.")
    cloudfront.update_distribution(
        Id=cloudfront_metadata["id"],
        IfMatch=distribution["ETag"],
        DistributionConfig=distribution["Distribution"]["DistributionConfig"],
    )

    # wait until distribution is fully disabled
    while True:
        time.sleep(2)
        status = cloudfront.get_distribution(Id=cloudfront_metadata["id"])
        if (
            status["Distribution"]["DistributionConfig"]["Enabled"] is False
            and status["Distribution"]["Status"] == "Deployed"
        ):
            logger.info("Cloudfront distribution disabled.")
            break

    logger.info("Deleting cloudfront distribution.")
    cloudfront.delete_distribution(Id=cloudfront_metadata["id"], IfMatch=status["ETag"])


def setup_cloudfront(domain, certificate_arn):
    """Create AWS CloudFront Distribution."""
    # Launch CloudFront distribution
    unique_identifier = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
    domain_name = domain["name"]

    distribution_config = {
        "CallerReference": unique_identifier,
        "Aliases": {"Quantity": 2, "Items": [domain_name, f"www.{domain_name}"]},
        "DefaultRootObject": "home.html",
        "Comment": "Managed by Domain Manager",
        "Enabled": True,
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": "1",
                    "DomainName": WEBSITE_BUCKET_URL,
                    "OriginPath": f"/{domain_name}",
                    "CustomOriginConfig": {
                        "HTTPPort": 80,
                        "HTTPSPort": 443,
                        "OriginProtocolPolicy": "http-only",
                    },
                }
            ],
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": "1",
            "ViewerProtocolPolicy": "redirect-to-https",
            "TrustedSigners": {"Quantity": 0, "Enabled": False},
            "ForwardedValues": {
                "QueryString": False,
                "Cookies": {"Forward": "all"},
                "Headers": {"Quantity": 0},
                "QueryStringCacheKeys": {"Quantity": 0},
            },
            "MinTTL": 1000,
        },
        "ViewerCertificate": {
            "ACMCertificateArn": certificate_arn,
            "SSLSupportMethod": "sni-only",
            "MinimumProtocolVersion": "TLSv1.2_2019",
        },
    }

    distribution = cloudfront.create_distribution(
        DistributionConfig=distribution_config
    )

    return (
        distribution["Distribution"]["Id"],
        distribution["Distribution"]["DomainName"],
    )


def setup_dns(domain, endpoint=None):
    """Create a domain's DNS."""
    domain_name = domain["name"]
    dns_id = domain["route53"]["id"]
    response = route53.change_resource_record_sets(
        HostedZoneId=dns_id,
        ChangeBatch={
            "Comment": domain_name,
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": domain_name,
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z2FDTNDATAQYW2",
                            "EvaluateTargetHealth": False,
                            "DNSName": endpoint,
                        },
                    },
                },
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": f"www.{domain_name}",
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": "Z2FDTNDATAQYW2",
                            "EvaluateTargetHealth": False,
                            "DNSName": endpoint,
                        },
                    },
                },
            ],
        },
    )
    logger.info(response)
    return response


def delete_dns(domain, endpoint=None):
    """Create a domain's DNS."""
    domain_name = domain["name"]
    dns_id = domain["route53"]["id"]
    try:
        # Delete main resource record
        route53.change_resource_record_sets(
            HostedZoneId=dns_id,
            ChangeBatch={
                "Comment": domain_name,
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": domain_name,
                            "Type": "A",
                            "AliasTarget": {
                                "HostedZoneId": "Z2FDTNDATAQYW2",
                                "EvaluateTargetHealth": False,
                                "DNSName": endpoint,
                            },
                        },
                    },
                ],
            },
        )
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "InvalidChangeBatch":
            pass
        else:
            raise error

    try:
        # Delete www dns record
        route53.change_resource_record_sets(
            HostedZoneId=dns_id,
            ChangeBatch={
                "Comment": domain_name,
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": f"www.{domain_name}",
                            "Type": "A",
                            "AliasTarget": {
                                "HostedZoneId": "Z2FDTNDATAQYW2",
                                "EvaluateTargetHealth": False,
                                "DNSName": endpoint,
                            },
                        },
                    },
                ],
            },
        )
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "InvalidChangeBatch":
            pass
        else:
            raise error

    try:
        # Try delete old CNAME record if it exists
        # This can be removed later after all
        # deployments have transitioned
        route53.change_resource_record_sets(
            HostedZoneId=dns_id,
            ChangeBatch={
                "Comment": domain_name,
                "Changes": [
                    {
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": f"www.{domain_name}",
                            "Type": "CNAME",
                            "AliasTarget": {
                                "HostedZoneId": "Z2FDTNDATAQYW2",
                                "EvaluateTargetHealth": False,
                                "DNSName": endpoint,
                            },
                        },
                    },
                ],
            },
        )
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "InvalidChangeBatch":
            pass
        else:
            raise error


def generate_ssl_certs(domain):
    """Request and Validate an SSL certificate using AWS Certificate Manager."""
    domain_name = domain["name"]
    dns_id = domain["route53"]["id"]
    requested_certificate = acm.request_certificate(
        DomainName=domain_name,
        ValidationMethod="DNS",
        SubjectAlternativeNames=[domain_name, f"www.{domain_name}"],
        DomainValidationOptions=[
            {"DomainName": domain_name, "ValidationDomain": domain_name},
        ],
        Options={"CertificateTransparencyLoggingPreference": "ENABLED"},
    )

    cert_arn = requested_certificate["CertificateArn"]
    acm_records = [None, None]
    while None in acm_records:
        time.sleep(2)
        acm_records = get_acm_records(cert_arn)

    # add validation records to dns
    for record in acm_records:
        route53.change_resource_record_sets(
            HostedZoneId=dns_id,
            ChangeBatch={
                "Comment": domain_name,
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": record["Name"],
                            "Type": "CNAME",
                            "TTL": 30,
                            "ResourceRecords": [{"Value": record["Value"]}],
                        },
                    },
                ],
            },
        )

    # wait until the certificate has been validated
    waiter = acm.get_waiter("certificate_validated")
    waiter.wait(CertificateArn=cert_arn)

    return cert_arn


def delete_ssl_certs(domain):
    """Delete acm ssl certs."""
    cert_arn = domain["acm"]["certificate_arn"]

    try:
        acm_records = get_acm_records(cert_arn)
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ResourceNotFoundException":
            return
        else:
            raise error

    for record in acm_records:
        try:
            route53.change_resource_record_sets(
                HostedZoneId=domain["route53"]["id"],
                ChangeBatch={
                    "Changes": [
                        {
                            "Action": "DELETE",
                            "ResourceRecordSet": {
                                "Name": record["Name"],
                                "Type": "CNAME",
                                "TTL": 30,
                                "ResourceRecords": [{"Value": record["Value"]}],
                            },
                        }
                    ]
                },
            )
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "InvalidChangeBatch":
                pass
            else:
                raise error

    try:
        acm.delete_certificate(CertificateArn=cert_arn)
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ResourceNotFoundException":
            return
        else:
            raise error


def get_acm_records(cert_arn):
    """Get acm route 53 record for validation."""
    certificate_description = acm.describe_certificate(CertificateArn=cert_arn)

    return [
        description.get("ResourceRecord", None)
        for description in certificate_description.get("Certificate", {}).get(
            "DomainValidationOptions"
        )
    ]


def verify_hosted_zone(domain):
    """Verify that we have control of hosted zone."""
    hosted_zone = route53.get_hosted_zone(Id=domain["route53"]["id"])
    r53_nameservers = hosted_zone["DelegationSet"]["NameServers"]

    new_nameservers = []
    for server in r53_nameservers:
        if not server.endswith("."):
            server = f"{server}."
        new_nameservers.append(server)

    dns_resolver = dns.resolver.Resolver()
    try:
        response = dns_resolver.resolve(domain["name"], "NS").response
    except Exception as e:
        logger.exception(e)
        raise e
    ns_servers = []
    for answer in response.answer[0]:
        ns_servers.append(answer.to_text())
    if len(set(ns_servers) - set(new_nameservers)) > 0:
        raise Exception("Route53 nameservers don't match NS lookup.")


def verify_launch_records(domain):
    """Verify that no DNS records will clash on launch."""
    bad_records = list(
        filter(
            lambda x: x["name"] in [f"www.{domain['name']}", domain["name"]]
            and x["record_type"] == "A",
            domain.get("records", []),
        )
    )
    if bad_records:
        raise Exception(
            "You cannot have an A apex record or an A www record before launching the domain."
        )
