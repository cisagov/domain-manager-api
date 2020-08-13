"""Namecheap Utilities."""
# Standard Python Libraries
import os

# Third-Party Libraries
from namecheap import Api

# Initialize namecheap api client
nc_api = Api(
    ApiUser=os.environ.get("NC_USERNAME"),
    UserName=os.environ.get("NC_USERNAME"),
    ApiKey=os.environ.get("NC_API_KEY"),
    ClientIP=os.environ.get("NC_IP"),
    sandbox=False,
)


def setup_dns(domain_name, url):
    """Setup a domain's DNS."""
    url = url.replace("http://", "").replace("/", "")
    host = nc_api.domains_dns_addHost(
        domain_name,
        {
            "RecordType": "CNAME",
            "HostName": "@",
            "Address": url,
            "MXPref": 10,
            "TTL": 60,
        },
    )
    return host


def delete_dns(domain_name, url):
    """Delete a domain's host."""
    url = url.replace("http://", "").replace("/", "")
    host = None
    # TODO:  domain_dns_delHost method does not work. Fix!
    # host = nc_api.domains_dns_delHost(
    #     domain_name, {"Type": "CNAME", "Name": "@", "Address": url,},
    # )
    return host
